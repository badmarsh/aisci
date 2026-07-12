**Instructions for the User:** Copy everything below the line and paste it into a fresh agent session.

---

You are a senior DevOps and Full-Stack engineer responsible for the AiSci Research Control-Plane. The system is **functional but fragile**. Your mission is to execute a safe, incremental, and thoroughly verified stabilization pass covering four isolated phases. You are working only on infrastructure, deployment, and dashboard code. You are **not** a science researcher. Do not touch, reinterpret, or promote any evidence claims.

## Mandatory Intake Stage

Before executing any phase:

1. Read `AGENTS.md` in full.
2. Read `docs/ops/CURRENT_STATUS.md` and `docs/ops/platform-backlog.md`.
3. Confirm the stack is running: `ss -ltnp '( sport = :5173 or sport = :8001 )'`. If either service is down, note it — do not restart it yourself unless the user explicitly permits it in this session.
4. Confirm the HEAD commit SHA: `git -C /home/ubuntu/aisci rev-parse HEAD`.
5. Report findings as a **brief pre-execution summary** and wait for explicit user approval before starting Phase 1.

---

## Phase 1 — DB Sync Resilience: Fix `sync_tasks_to_db` Crash

**File:** `deployment/aisci-dashboard/ignition/sync_markdown.py`

### Background: Root-Cause Analysis

The `UNIQUE constraint failed: Tasks.id` crash originates in `sync_tasks_to_db`. The function:
1. Performs a `DELETE FROM Tasks WHERE project_id=?` (safe).
2. Re-inserts all parsed tasks using raw `INSERT INTO Tasks (id, ...)`.

The crash occurs because the Markdown parser (`_parse_tasks_from_markdown`) can produce **duplicate `id` values** from the same file. Three confirmed sources of duplication in `research/robert/next-actions.md`:

- **Source 1 — Bare list items without headings:** Items like `- [ ] **D-02 (Docs):** ...` are parsed by the fallback list-item parser and receive an auto-generated ID (e.g. `c-D-02-(Docs` or a truncated slug). If two such list items produce the same slug, the second INSERT crashes.
- **Source 2 — Completed-table ID collisions:** Rows in the `✅ Completed` table use `[A-05]`, `[D-01]`, etc. as IDs. If a heading task with the same ID (e.g. `[A-01]`) exists in the Active section and _also_ appears as a completed-table row after a re-run, the DELETE+re-INSERT cycle produces a collision on the second run.
- **Source 3 — Strikethrough text in list items:** The `_extract_text()` helper does not strip `~~strikethrough~~` markdown. A stricken list item like `~~[W-05] title~~` can generate a partial match against a real `[W-05]` heading task, adding a second row with the same ID.

### Fix Requirements

**1A. Make `INSERT` idempotent using `INSERT OR REPLACE`.**

In `sync_tasks_to_db`, change every `INSERT INTO Tasks (...)` to `INSERT OR REPLACE INTO Tasks (...)`. This is a minimal one-line fix that eliminates the crash for all current duplication sources. It must be the **first** change applied so the crash is resolved before any deeper refactor.

```python
# BEFORE
cursor.execute("INSERT INTO Tasks (id, ...) VALUES (?, ...)", (...))
# AFTER
cursor.execute("INSERT OR REPLACE INTO Tasks (id, ...) VALUES (?, ...)", (...))
```

**1B. Deduplicate parsed tasks in-memory before any DB write.**

After the parser produces the `tasks` list and before the DELETE+INSERT block, add a deduplication step that keeps only the _last_ occurrence of each `id` (last wins, so completed-table entries don't override active-section headings):

```python
seen = {}
for t in tasks:
    seen[t["id"]] = t  # last occurrence wins
tasks = list(seen.values())
```

**1C. Sanitize auto-generated IDs for bare list items.**

The fallback ID generator for non-heading list items currently truncates to 10 chars: `"c-" + title_str[:10].replace(" ", "-")`. This is too short and produces collisions. Replace with a SHA-256-based suffix:

```python
import hashlib
t_id = "c-" + hashlib.sha256(title_str.encode()).hexdigest()[:12]
```

**1D. Strip strikethrough from extracted text.**

In `_extract_text()`, add a post-processing step to strip `~~...~~` wrappers from raw text:

```python
text = re.sub(r'~~(.*?)~~', '', text)
```

Apply this in `sync_tasks_to_db` when calling `_extract_text()` on list item children.

### Verification for Phase 1

After implementing 1A–1D:
1. Delete the SQLite DB: `rm /home/ubuntu/aisci/deployment/aisci-dashboard/data/evidence_graph.db`
2. Restart the API: verify it starts cleanly with no UNIQUE constraint errors in stderr.
3. Call `POST http://localhost:8001/api/projects/robert-boson-manuscript/sync` (no token needed in dev).
4. Call `GET http://localhost:8001/api/projects/robert-boson-manuscript/tasks` — confirm it returns a non-empty list with no duplicate IDs.
5. Run `sync_markdown.py` twice in succession: `python deployment/aisci-dashboard/ignition/sync_markdown.py`. Confirm the second run produces no errors.

**Do not proceed to Phase 2 until all Phase 1 verification steps pass.**

---

## Phase 2 — API Hardening

**File:** `deployment/aisci-dashboard/ignition/api.py`

Work on each sub-task independently. After each sub-task, run a smoke test: `curl http://localhost:8001/api/projects` must return a valid JSON list.

### 2A. Fix `stream_pipeline_log` stale log path

`GET /api/projects/{project_id}/logs/{pipeline_id}` constructs:
```python
log_path = os.path.join(runs_dir, f"{pipeline_id}_latest.log")
```
But the worker writes logs to `{job_id}.log`, not `{pipeline_id}_latest.log`. The endpoint will always return "No logs found" for any real job.

**Fix:** Change the endpoint to look up the latest job for the given `pipeline_id` from `JobExecutions` and stream its `log_path` field:

```python
@app.get("/api/projects/{project_id}/logs/{pipeline_id}")
def stream_pipeline_log(project_id: str, pipeline_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT log_path FROM JobExecutions WHERE project_id = ? AND pipeline_id = ? ORDER BY created_at DESC LIMIT 1",
        (project_id, pipeline_id)
    )
    row = cursor.fetchone()
    conn.close()
    if not row or not row["log_path"]:
        return StreamingResponse(iter([f'data: {{"line": "No logs found for {pipeline_id}.\\n"}}\n\n']), media_type="text/event-stream")
    return stream_log_file(row["log_path"])
```

### 2B. Fix `get_agents` hardcoded log paths

`GET /api/agents` references `backend.log`, `ingest.log`, and `fits.log` relative to `deployment/aisci-dashboard/`. These files likely do not exist in the current deployment, causing all agents to show `IDLE` incorrectly.

**Fix:** Change agent status detection to query `JobExecutions` for the most recently updated job per pipeline type:

```python
@app.get("/api/agents", response_model=List[AgentModel])
def get_agents():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT pipeline_id, status, updated_at, log_path FROM JobExecutions ORDER BY updated_at DESC LIMIT 20"
    )
    rows = cursor.fetchall()
    conn.close()
    # Build per-pipeline latest status
    ...
```

Provide a reasonable fallback agent list from live `JobExecutions` data. The "FastAPI Backend" agent should always show `ACTIVE` with a `last` of `datetime.now()`.

### 2C. Validate `project_id` on all routes

Several endpoints (e.g. `get_evidence`, `get_tasks`, `get_anomalies`) will crash with an unhandled `KeyError` from `registry.get_project(project_id)` when given an unknown project ID. The `get_project` method currently raises an uncaught exception.

**Fix:** Wrap every `registry.get_project(project_id)` call (or add a guard in `ProjectRegistry.get_project()`) to raise `HTTPException(status_code=404, detail=f"Project '{project_id}' not found")` instead of a bare Python exception:

```python
# In project_registry.py
def get_project(self, project_id: str) -> ProjectSpec:
    spec = self._projects.get(project_id)
    if not spec:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    return spec
```

### 2D. Add missing `done`/`closed` filter to `get_tasks`

`GET /api/projects/{project_id}/tasks` currently returns all tasks including `done` ones. The UI's three-tab layout (Active / Blocked / Proposed) silently drops `done` tasks. This is correct UX, but the endpoint should support an optional `?exclude_done=true` query param for callers that want the filtered set server-side:

```python
@app.get("/api/projects/{project_id}/tasks", response_model=List[TaskModel])
def get_tasks(project_id: str, exclude_done: bool = False):
    ...
    if exclude_done:
        cursor.execute("SELECT * FROM Tasks WHERE project_id = ? AND status != 'done'", (project_id,))
    else:
        cursor.execute("SELECT * FROM Tasks WHERE project_id = ? ", (project_id,))
```

### Verification for Phase 2

1. `curl http://localhost:8001/api/projects/robert-boson-manuscript/tasks` — returns valid JSON.
2. `curl http://localhost:8001/api/projects/NONEXISTENT/tasks` — returns `{"detail": "Project 'NONEXISTENT' not found"}` with HTTP 404 (not 500).
3. `curl http://localhost:8001/api/agents` — returns a list with at least one agent and `ACTIVE` status.
4. `curl http://localhost:8001/api/projects/robert-boson-manuscript/logs/fit-pipeline` — returns SSE stream (even if "No logs found" message), not a 500 error.

**Do not proceed to Phase 3 until all Phase 2 verification steps pass.**

---

## Phase 3 — Frontend Completion

**Directory:** `deployment/aisci-dashboard/src/`

### 3A. Wire Tasks query to use `project_id`

In `src/lib/api.ts` (or equivalent), `fetchTasks` currently calls a hardcoded or project-agnostic URL. Audit the call and ensure it passes the current `projectId` from the route params:

```typescript
// BEFORE (likely)
export const fetchTasks = () => fetch(`/api/projects/robert-boson-manuscript/tasks`).then(r => r.json())
// AFTER
export const fetchTasks = (projectId: string) =>
  fetch(`/api/projects/${projectId}/tasks`).then(r => r.json())
```

Update the `useQuery` call in `projects.$projectId.tasks.tsx` to pass `projectId` from the route.

### 3B. Add empty-state panels for all tab views

In `projects.$projectId.tasks.tsx`, each `TabsContent` renders an empty grid when its list is empty, with no user-facing feedback. Add a consistent empty-state panel for each tab:

```tsx
{active.length === 0 && (
  <div className="rounded-lg border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
    No active tasks.
  </div>
)}
```

Apply the same pattern to the `blocked` and `proposed` tabs.

### 3C. Add a Jobs route (if not already present)

Check `src/routes/` for `projects.$projectId.jobs.tsx`. If it does not exist:

1. Create `src/routes/projects.$projectId.jobs.tsx` with a full implementation:
   - Fetches `GET /api/projects/{projectId}/jobs`.
   - Displays a table: Job ID (first 8 chars), Pipeline Name, Status badge, Created At, Git Commit (8-char), Artifact Count.
   - Clicking a row expands an artifact manifest panel: path, size (human-readable), SHA-256 (truncated to 16 chars).
   - Empty state: "No pipeline jobs have been run yet."
   - Loading skeleton using `<Skeleton>`.
   - Error state with `text-rose-brand`.

2. Add a "Jobs" nav link to `__root.tsx` project nav. Gate it using the same capability-check pattern already used for the fits/anomalies tabs (show only when `capabilities` includes `fit_validation` or `symbolic_validation`).

3. Re-generate `routeTree.gen.ts` by running `npm run dev` once (TanStack Router auto-generates the tree file on startup). Do **not** manually edit `routeTree.gen.ts`.

### 3D. Sync button feedback in Tasks page

In `projects.$projectId.tasks.tsx`, the "Sync from Files" button has no success/error toast. After `syncMutation` completes, the query is invalidated but the user has no confirmation. Add:

```tsx
const syncMutation = useMutation({
  mutationFn: syncFromFiles,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ["evidence"] });
    queryClient.invalidateQueries({ queryKey: ["tasks"] });
    toast.success("Synced from canonical files.");
  },
  onError: () => {
    toast.error("Sync failed. Check the API logs.");
  }
});
```

### Verification for Phase 3

1. Open `http://localhost:5173`. Navigate to the Tasks page for `robert-boson-manuscript`.
2. Confirm all three tabs render correctly; the `proposed` tab shows at least the `A-01`, `A-02`, `A-04` tasks.
3. Confirm the "Sync from Files" button shows a success toast after clicking.
4. Navigate to the Jobs page (if created). Confirm it renders without errors (empty state is acceptable if no jobs have run).
5. Confirm no browser console errors related to missing route params or undefined `projectId`.

**Do not proceed to Phase 4 until all Phase 3 verification steps pass.**

---

## Phase 4 — Final Ops Audit & Canonical Doc Updates

### 4A. Ops hygiene checklist

Verify each item. Fix only if confirmed broken:

- [ ] `deployment/aisci-dashboard/ignition/evidence_graph.db.archive` — if this file exists, confirm it is listed in `.gitignore`. If it is committed to the repo but serves no documented purpose, propose deletion to the user before removing.
- [ ] `deployment/aisci-dashboard/ignition/test_ast.py` — confirm it is exercised by `pytest.ini`. Run `cd deployment/aisci-dashboard/ignition && python -m pytest test_ast.py -v`. If it fails or is not a real test, move it to `deployment/helper/` and update `pytest.ini` accordingly.
- [ ] Confirm no scratch `.py` files exist at the repo root or `deployment/aisci-dashboard/ignition/` that are not imported by any module and not tested.
- [ ] Confirm `docs/ops/CURRENT_STATUS.md` accurately reflects that `artifact_manifest` and `git_commit` are now populated by the worker (the status file already says this, but verify the wording is still accurate after Phase 1–3 changes).

### 4B. `platform-backlog.md` update

Open `docs/ops/platform-backlog.md`. Add a new row for the crash that this session fixed:

```markdown
| P1 | DB Sync | Fix UNIQUE constraint crash in sync_tasks_to_db | Markdown parser produced duplicate Task IDs; second INSERT crashed on UNIQUE constraint. | Use INSERT OR REPLACE, deduplicate in-memory before DB write, harden auto-generated IDs, strip strikethrough text. | Done |
```

Do **not** create any other new markdown files. If you find issues that cannot be resolved in this session, add them as new rows to `platform-backlog.md` only.

### 4C. Create verification GitHub Issue

Create a GitHub Issue using the project's standard label set, titled:
**`Control-plane stabilization 2026-07-12 — sync crash fix, API hardening, frontend completion`**

Body should include:
- The HEAD commit SHA at the end of this session.
- A checklist of each phase and its verification status.
- Any deferred items (rows added to `platform-backlog.md`).

This serves as the execution record per `AGENTS.md` GitHub Workflow rules.

---

## Hard Constraints

- Do not touch `research/robert/evidence-ledger.md`, `research/robert/next-actions.md`, or any science claim status without explicit user instruction.
- Do not promote any claim beyond its current evidence-ledger status.
- Do not create scratch files. Temporary helper scripts go to `deployment/helper/`.
- Do not paste secret values anywhere. Reference only env var names.
- Do not manually edit `routeTree.gen.ts` — let TanStack Router auto-generate it.
- If running in Windows/WSL: wrap all Node/Python commands as `wsl bash -c "cd /home/ubuntu/aisci && <command>"`.
- Use `libs/physics-core/.venv/bin/python` for all Python execution in `ignition/`.
- After each phase, run the full verification checklist for that phase before moving on.
- This Megaprompt was generated by analysis of commit `58f906dc79c7342cab31d045e1676023ffe8b6a4` on 2026-07-12. Verify the repository HEAD matches before beginning.
