# DeerFlow Local Patches

`deployment/deer-flow/` is a vendored checkout of the upstream DeerFlow repo and is **gitignored**. Several local patches must be re-applied after any clean checkout, container rebuild, or vendor sync.

Run `apply_local_patches.sh` to restore all patches at once.

---

## Patch 1 — `run_events.backend: db` (config.yaml)

**File:** `deployment/deer-flow/config.yaml`

**Problem:** Default `run_events.backend: memory` means run state is never persisted. Every `GET /api/runs/{run_id}` returns 404 after the spawning request completes or the container restarts.

**Fix:** Set `run_events.backend: db` and remove any legacy `checkpointer:` block. Both cannot coexist — LangGraph state splits across two SQLite files and cross-references fail.

```yaml
# Remove entirely if present:
# checkpointer:
#   type: sqlite
#   connection_string: checkpoints.db

database:
  backend: sqlite
  sqlite_dir: .deer-flow/data

run_events:
  backend: db
  max_trace_content: 10240
  track_token_usage: true
```

**Reference:** `docs/ops/troubleshooting.md` — "HTTP 404: Run not found"

---

## Patch 2 — `summarization:` YAML nesting fix (config.yaml)

**File:** `deployment/deer-flow/config.yaml`

**Problem:** `trim_tokens_to_summarize`, `summary_prompt`, and `preserve_*` keys were accidentally indented inside `keep:` instead of as siblings. Summarization triggers at wrong counts and preserve settings have no effect.

**Fix:** Ensure these keys are siblings of `keep:`, not children:

```yaml
summarization:
  enabled: true
  model_name: gemini-2.5-flash
  trigger:
    - type: tokens
      value: 10240
    - type: messages
      value: 30
  keep:
    type: messages
    value: 8
  trim_tokens_to_summarize: 8192      # ← sibling of keep:, NOT child
  summary_prompt: null
  preserve_recent_skill_count: 3
  preserve_recent_skill_tokens: 12000
  preserve_recent_skill_tokens_per_skill: 3000
```

**Reference:** `docs/ops/troubleshooting.md` — "summarization: config silently ignored"

---

## Patch 3 — Upload file permissions (uploads.py)

**File:** `deployment/deer-flow/backend/app/gateway/routers/uploads.py`

**Problem:** `AioSandboxProvider` sets `sync_to_sandbox=False` for deterministic persistent mounts, which skips `_make_file_sandbox_writable()`. Files uploaded via the gateway inherit the host umask (`0o644`) and are unreadable/unwritable by the sandbox container user.

**Fix:** Call `_make_file_sandbox_writable()` unconditionally after every file write, and ensure it sets world-readable + world-writable:

```python
import stat, os

def _make_file_sandbox_writable(file_path: str) -> None:
    os.chmod(
        file_path,
        stat.S_IRUSR | stat.S_IWUSR |
        stat.S_IRGRP | stat.S_IWGRP |
        stat.S_IROTH | stat.S_IWOTH   # world rw required for sandbox user
    )

# In the upload handler — unconditional, NOT inside `if sync_to_sandbox:`:
_make_file_sandbox_writable(str(file_path))
```

**Reference:** `docs/ops/troubleshooting.md` — "AIO Sandbox — uploaded files not accessible"

---

## Patch 4 — NVIDIA model base_url (config.yaml)

**File:** `deployment/deer-flow/config.yaml`

**Problem:** `nvidia-qwen3-5-122b` (and potentially other NVIDIA models) had `base_url: $OPENROUTER_API_BASE` instead of `$NVIDIA_API_BASE`, causing OpenRouter-style errors on NVIDIA NIM calls.

**Fix:** Every `nvidia-*` model entry must use `$NVIDIA_API_BASE`:

```yaml
- name: nvidia-qwen3-5-122b
  base_url: $NVIDIA_API_BASE   # NOT $OPENROUTER_API_BASE
  api_key: $NVIDIA_API_KEY
```

**Reference:** `docs/ops/troubleshooting.md` — "Model base_url pointing at wrong provider"

---

## Long-term plan

These patches should eventually be tracked as proper diffs or the affected files should be un-ignored selectively. Options:

1. Add `!deployment/deer-flow/config.yaml` and `!deployment/deer-flow/backend/app/gateway/routers/uploads.py` to `.gitignore` to track only the patched files.
2. Store unified diffs under `deployment/deer-flow/patches/` and apply with `patch -p1`.
3. De-vendor: track only AiSci overlays and pull upstream DeerFlow as a submodule or Docker image.
