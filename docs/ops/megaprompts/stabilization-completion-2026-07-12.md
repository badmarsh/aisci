**Instructions for the User:** Copy everything below the line and paste it into a fresh agent session.

---

You are the Principal Systems Architect for the AiSci repository located at `/home/ubuntu/aisci`. Your mission is to execute a thorough, incremental, and safe **stabilization, sanitation, and dashboard completion** pass on the control-plane. This is a pure platform/infrastructure session — you are not a science researcher and must not touch, reinterpret, or promote any science claims.

## Mandatory Intake Stage

Before executing any phase, perform the full Mandatory Intake Stage defined in `AGENTS.md`:

1. Read `AGENTS.md` in full.
2. Read `docs/ops/platform-backlog.md`, `docs/ops/architecture-overview.md`, `docs/ops/deployment-reference.md`, and `docs/ops/CURRENT_STATUS.md`.
3. Confirm the two Open items in `platform-backlog.md` (P1: Science Artifacts Provenance; P2: Literature Provenance/Idempotency) are still open and have not been resolved in a recent commit.
4. Identify any root-level or `docs/` files that violate the single-source-of-truth rule described in `AGENTS.md` (e.g. `ACTION_PLAN.md` having duplicate backlog detail, orphaned session notes like `docs/ops/next-session-prompt.md` or `docs/ops/next-session-jacobian-validation.md`, legacy ops files not clearly marked historical).
5. Report your findings as a **brief pre-execution summary** and **wait for explicit user approval before beginning Phase 1**.

---

## Phase 1 — Repository Sanitation

### 1A. Root-level hygiene

- Confirm `ACTION_PLAN.md` contains only high-level project tracking and no duplicate backlog rows (per `AGENTS.md`: "Keep `ACTION_PLAN.md` high level; do not duplicate detailed backlog rows there"). If it does, reduce it to one-line status bullets.
- Inspect whether `docs/ops/next-session-prompt.md` and `docs/ops/next-session-jacobian-validation.md` represent orphaned session handoffs whose actionable items have been absorbed into `research/robert/next-actions.md` or `docs/ops/platform-backlog.md`. If the actionable items were implemented, delete or archive them. If any actionable items are unimplemented, migrate them to the appropriate canonical file before deleting.
- Check `docs/ops/agent-skills-audit-report.md`, `docs/ops/gemini-audit-prompt.md`, `docs/ops/multica_day_1_evaluation.md` — these appear to be historical evaluation artifacts that may violate the hygiene rule ("do not create new backlog, audit, or status markdown files when a GitHub Issue plus an update to an existing canonical doc will do"). Verify whether their content is already captured in canonical docs. Retain only if they serve a unique historical purpose; otherwise flag for archival or deletion with user confirmation.
- Check `deployment/aisci-dashboard/ignition/evidence_graph.db.archive` — a 77 KB binary archive file committed into the repository. Confirm whether this violates `.gitignore` or `AGENTS.md` file hygiene. If it is not needed for any documented purpose, propose its deletion with git-filter-repo guidance or simply delete the file and note its removal in `CHANGELOG.md`.
- Confirm `test_ast.py` in `deployment/aisci-dashboard/ignition/` is a real test exercised by `pytest.ini` and not a scratch file. If it is a scratch file, move it to `deployment/helper/` or delete it.

### 1B. Docs/ops classification

- Review `docs/ops/README.md` to confirm it correctly describes what currently lives in `docs/ops/`. Update it to reflect any files added or removed during this session.
- Ensure all files currently in `docs/ops/` that are historical-only are prefixed or noted clearly (e.g. a front-matter note: `> Historical record only — not active operational guidance`).

---

## Phase 2 — Backend Stabilization

Work only inside `deployment/aisci-dashboard/ignition/`. Make small, individually verified changes.

### 2A. Worker race-condition hardening (`worker.py`)

The current `poll_and_run()` loop performs a `SELECT ... WHERE status = 'pending'` on one connection and an `UPDATE ... SET status = 'running'` on the same connection but in separate round-trips. Under SQLite WAL mode with multiple readers this is safe for a single-worker scenario, but the pattern is fragile if the worker is ever restarted mid-job, because a job can be left in `running` status permanently.

Fix requirements:
1. Wrap the SELECT + UPDATE in a single atomic transaction using `BEGIN IMMEDIATE` (not `BEGIN EXCLUSIVE`, which is excessive for a single-worker design). The pattern must be:
   ```python
   with conn:
       cursor.execute("BEGIN IMMEDIATE")
       cursor.execute("SELECT id, project_id, pipeline_id FROM JobExecutions WHERE status = 'pending' ORDER BY created_at ASC LIMIT 1")
       job = cursor.fetchone()
       if job:
           cursor.execute("UPDATE JobExecutions SET status = 'running', log_path = ?, updated_at = ? WHERE id = ? AND status = 'pending'",
                          (log_path, datetime.now().isoformat(), job_id))
   ```
   Only proceed if the UPDATE affected exactly 1 row (use `cursor.rowcount`). This prevents a restarted worker from double-executing a job.
2. Add a **startup recovery step**: at worker startup (before the polling loop begins), query for any jobs with `status = 'running'` that have no updated `updated_at` within the last N minutes (configurable, default 30). Mark those jobs `failed` with `error = 'Worker restart recovery: job was abandoned'`. Log recovery actions.
3. Add a **child-process timeout**: wrap `subprocess.run(...)` with `timeout=` parameter (configurable via env var `AISCI_PIPELINE_TIMEOUT_SECONDS`, default `3600`). Catch `subprocess.TimeoutExpired`, kill the child process, and set the job status to `failed` with `error = 'Pipeline timed out'`.
4. Ensure the `except Exception as e:` block in the polling loop also sets any job that was transitioning to `failed` if its `job_id` is in scope, to prevent perpetual `running` ghost jobs after a worker crash.

### 2B. API security hardening (`api.py`)

1. **`verify_token` fail-closed in production**: The current implementation raises HTTP 500 only if `ENVIRONMENT == 'production'` AND `AUTH_TOKEN` is not set. This is correct, but confirm `config.py` actually reads `ENVIRONMENT` from the environment (not hardcoded). Add a docstring comment to `verify_token` explicitly noting the security contract.
2. **CORS**: The `ALLOWED_ORIGINS` list comes from `config.py`. Verify that in a local-dev fallback, `config.py` defaults to `["http://localhost:5173"]` only — not a wildcard. Document this in a comment in `config.py`.
3. **Duplicate-job check race window**: The current duplicate-job check in `trigger_pipeline` (SELECT then INSERT on separate connection opens) has a narrow TOCTOU window. Wrap the check and the INSERT in a single `BEGIN IMMEDIATE` transaction. If an `IntegrityError` or conflicting row is found, return 409.
4. **`log_activity` connection leak**: `log_activity` opens a connection but only closes it on the happy path. Wrap in `try/finally` to guarantee `conn.close()`.
5. **`stream_log_file` busy-loop**: The inner `for _ in range(60)` loop calls `time.sleep(0.5)` in a sync generator that runs inside a `StreamingResponse`. Ensure this is confirmed to run in a thread pool (FastAPI will do this for sync generators), but add a comment explaining the threading context so a future developer does not move it into an async generator.

### 2C. Database schema hygiene (`database.py`)

1. The schema-migration block uses a series of bare `ALTER TABLE ... ADD COLUMN` wrapped in `try/except OperationalError`. This pattern works but produces silent schema drift. Add a `SchemaVersion` table (single-row, integer version) and gate each migration on a version check. This prevents redundant migration attempts on every startup.
2. The `Papers` table does not have a `provenance` column (source provider string) or a `source_hash` column (idempotency key). These are required for the P2 literature provenance backlog item. Add them as `NULL`-able columns in the migration block so existing rows are unaffected.
3. The `JobExecutions` table has an `artifact_manifest` column (`TEXT`) and a `git_commit` column, but neither is populated by the current worker. These columns are the hook for the P1 versioned-artifact provenance item. Confirm they exist after migration (they do per `database.py`) and document in a comment that they are intentionally unpopulated until Phase 3B.

---

## Phase 3 — Dashboard Feature Completion

Implement the two Open P1/P2 items from `platform-backlog.md`. Each sub-task below ends with a verification step.

### 3A. Versioned run/artifact provenance (P1)

**Goal:** Every completed pipeline job must record a manifest of its output artifacts and the git commit SHA at the time of the run, and the dashboard must be able to display this provenance.

**Backend (`worker.py` and `api.py`):**
1. After a pipeline completes successfully, the worker must:
   a. Call `git rev-parse HEAD` in the project root to get the current commit SHA.
   b. Walk the run output directory (`spec.get_runs_dir()`) for any files created or modified since the job started (use `os.stat().st_mtime >= job_start_time`).
   c. For each such file, compute an SHA-256 hash of its contents.
   d. Serialize the manifest as JSON: `{"git_commit": "...", "artifacts": [{"path": "...", "sha256": "...", "size_bytes": N}]}`.
   e. Write the JSON to `JobExecutions.artifact_manifest` and `JobExecutions.git_commit` in the database.
2. Add a new API endpoint: `GET /api/projects/{project_id}/jobs` — returns all `JobExecutions` rows for the project, ordered by `created_at DESC`, with `artifact_manifest` parsed into a structured list.
3. Add a new API endpoint: `GET /api/projects/{project_id}/jobs/{job_id}` — returns a single job row with full provenance detail.

**Frontend:**
4. Add a new route `projects.$projectId.jobs.tsx` that:
   - Fetches from `/api/projects/{project_id}/jobs`.
   - Displays a table of jobs: ID, pipeline name, status, created_at, git_commit (truncated to 8 chars), artifact count.
   - Clicking a job row expands an artifact manifest panel showing each artifact's path, size, and SHA-256.
   - Shows a "No jobs run yet" empty state when the list is empty.
5. Add a "Jobs" nav link to `__root.tsx` project nav, visible only when the project has the `fit_validation` or `symbolic_validation` capability. Use the same capability-gating pattern already used in the codebase.
6. On the Fits page (`projects.$projectId.fits.tsx`), augment the run selector to show the git commit SHA and artifact count next to each run name (fetch from the jobs endpoint, join by run directory name or job ID).

**Verification:** After implementation, start the dashboard with `bash start_dashboard.sh`. Trigger a pipeline run via the dashboard (or a `curl -X POST` with a valid token). Confirm the job record in the database has `artifact_manifest` populated. Confirm the Jobs route renders the manifest in the UI.

### 3B. Literature provenance & idempotency (P2)

**Goal:** Literature ingestion must be project-scoped and idempotent; each paper record must carry explicit `provenance` (provider name, e.g. `openalex`, `arxiv`) and a `source_hash` (idempotency key, e.g. SHA-256 of paper ID + project ID) that prevents duplicate inserts.

**Backend (`api.py`, `database.py`, `ingest_pipeline.py`, `load_legacy_papers.py`):**
1. The `Papers` table now has `provenance` and `source_hash` columns (added in Phase 2C). Add a `UNIQUE` constraint on `(project_id, source_hash)` via a migration — if the constraint already exists (re-run scenario), skip silently.
2. In `api.py`, remove the hardcoded source inference logic:
   ```python
   source = "OpenAlex" if p['id'].startswith("W") else "arXiv"  # REMOVE THIS
   ```
   Replace with `p['provenance'] or 'Unknown'`.
3. Audit `ingest_pipeline.py` and `load_legacy_papers.py`. In every `INSERT INTO Papers` call, compute `source_hash = sha256(f"{project_id}:{paper_id}".encode()).hexdigest()` and use `INSERT OR IGNORE` semantics so re-running ingestion is fully idempotent.
4. Ensure `insert_paper()` in `database.py` accepts and stores `provenance` and `source_hash`, using `INSERT OR IGNORE` (not `INSERT OR REPLACE`) to preserve existing records.

**Frontend (`projects.$projectId.literature.tsx`):**
5. Replace any hardcoded `"OpenAlex"` / `"arXiv"` source badge logic with the `provenance` field returned from the API.
6. Add a `provenance` column or badge to the literature table if not already present.

**Verification:** Re-run the ingest pipeline (or manually call `load_legacy_papers.py`). Confirm that running it twice does not create duplicate rows. Confirm the `provenance` field is non-null for all ingested records.

---

## Phase 4 — Post-Implementation Canonical Doc Updates

After all phases are complete and verified:

1. Update `docs/ops/platform-backlog.md`:
   - Mark **P1 Science Artifacts** as `Done` with evidence: `GET /api/projects/{project_id}/jobs`, `artifact_manifest` column, `projects.$projectId.jobs.tsx`.
   - Mark **P2 Literature Provenance** as `Done` with evidence: `provenance`/`source_hash` columns, `INSERT OR IGNORE` ingestion, frontend provenance badge.
   - Mark **P2 Archive Hygiene** as `Done` (or `In Progress`) based on what was actually completed in Phase 1.
2. Update `CHANGELOG.md` with a dated entry summarising the stabilization changes.
3. Create a GitHub Issue using the `platform` label and `from-perplexity` source tag, titled `Platform stabilization 2026-07-12 — verification tracking`, linking to the relevant commit SHA(s). This serves as the execution record per `AGENTS.md` GitHub Workflow rules.
4. Do **not** create any new markdown reports or status documents. All findings go into the above-listed canonical files only.

---

## Hard Constraints (from `AGENTS.md`)

- Do not touch `research/robert/evidence-ledger.md`, `research/robert/next-actions.md`, or any science claim status without explicit user instruction.
- Do not promote any claim beyond its current evidence-ledger status.
- Do not create scratch files in the working directory. Temporary helper scripts go to `deployment/helper/`.
- Do not paste secret values anywhere. Reference only env var names and file paths.
- If running in Windows/WSL: wrap all Node/Python commands as `wsl bash -c "cd /home/ubuntu/aisci && <command>"`.
- Use `libs/physics-core/.venv/bin/python` for all Python execution.
- After each phase, verify the API and dashboard are still running correctly with `ss -ltnp '( sport = :5173 or sport = :8001 )'` and a smoke-test `curl http://localhost:8001/api/projects`.
- This Megaprompt was generated by analysis of commit `e1a9db9eea714ec6da0add485062b25c41621cc6` on 2026-07-12. Verify the repository HEAD before beginning.
