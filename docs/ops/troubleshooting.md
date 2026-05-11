# Troubleshooting

Operational runbook for diagnosing and resolving known failure modes across Onyx, DeerFlow, MCP, and sandbox services.

---

## DeerFlow

### HTTP 404: Run `{run_id}` not found

**Symptom:** `GET /api/runs/{run_id}` returns `{"detail": "Run <uuid> not found"}` even immediately after the run was created.

**Root cause:** `run_events.backend: memory` in `config.yaml` — run state is never written to disk. Any restart or new request context loses the run object.

**Fix — `config.yaml`:**
```yaml
# Remove the legacy checkpointer block entirely if present:
# checkpointer:
#   type: sqlite
#   connection_string: checkpoints.db

# Ensure database is set:
database:
  backend: sqlite
  sqlite_dir: .deer-flow/data

# Change run_events backend:
run_events:
  backend: db        # was: memory
  max_trace_content: 10240
  track_token_usage: true
```

**Why remove `checkpointer:`?** When both `checkpointer:` and `database:` are present, LangGraph state goes into the legacy `checkpoints.db` while run/thread application data goes into `.deer-flow/data/` — two separate SQLite files that drift out of sync, causing cross-referencing failures.

**After editing:** `docker compose restart deerflow` (or equivalent).

---

### `summarization:` config silently ignored / wrong keep count

**Symptom:** Summarization triggers at wrong token counts or `preserve_recent_skill_*` settings have no effect.

**Root cause:** YAML nesting bug — `trim_tokens_to_summarize`, `summary_prompt`, and `preserve_*` keys were accidentally indented inside `keep:` instead of as siblings.

**Broken:**
```yaml
summarization:
  keep:
    type: messages
    value: 10
    trim_tokens_to_summarize: 15564   # ← WRONG: inside keep:
    summary_prompt: null              # ← WRONG
    preserve_recent_skill_count: 5   # ← WRONG
    preserve_recent_skill_tokens: 25000  # ← WRONG
```

**Fixed:**
```yaml
summarization:
  keep:
    type: messages
    value: 10
  trim_tokens_to_summarize: 15564    # ← sibling of keep:
  summary_prompt: null
  preserve_recent_skill_count: 5
  preserve_recent_skill_tokens: 25000
  preserve_recent_skill_tokens_per_skill: 5000
```

---

### AIO Sandbox — uploaded or unzipped files not accessible to agents

**Symptom:** Agent running inside the Docker sandbox reports `Permission denied` or `No such file` for files that were uploaded via the DeerFlow gateway or unzipped by a previous bash step.

**Root cause:** When `AioSandboxProvider` uses deterministic persistent mounts, the gateway sets `sync_to_sandbox=False`, which skips `_make_file_sandbox_writable()`. Files are written by the gateway process with the host umask (typically `0o644` or `0o640`), making them unreadable/unwritable by the sandbox container user.

**Live fix** (re-apply after any container rebuild or volume reset):

File: `deployment/deer-flow/backend/app/gateway/routers/uploads.py`

Locate the upload handler and ensure `_make_file_sandbox_writable` is called **unconditionally** (not guarded by `sync_to_sandbox`):

```python
# Ensure _make_file_sandbox_writable sets both world-readable and world-writable:
import stat

def _make_file_sandbox_writable(file_path: str) -> None:
    """Set permissions so sandbox container user can read and write the file."""
    os.chmod(
        file_path,
        stat.S_IRUSR | stat.S_IWUSR |   # owner rw
        stat.S_IRGRP | stat.S_IWGRP |   # group rw
        stat.S_IROTH | stat.S_IWOTH     # world rw  ← required for sandbox user
    )

# In the upload handler, call unconditionally after file is written:
await file_obj.write(content)
_make_file_sandbox_writable(str(file_path))   # ← must NOT be inside `if sync_to_sandbox:`
```

**Note:** `deployment/deer-flow/` is gitignored. This patch must be re-applied manually after any `git checkout`, container rebuild, or vendor sync. Consider un-ignoring `uploads.py` specifically or tracking the patch as a diff under `deployment/deer-flow/patches/`.

---

### Model `base_url` pointing at wrong provider

**Symptom:** NVIDIA NIM model returns OpenRouter-style errors, or vice versa.

**Known instance:** `nvidia-qwen3-5-122b` had `base_url: $OPENROUTER_API_BASE` instead of `$NVIDIA_API_BASE`.

**Fix:** Audit `config.yaml` model entries — every `nvidia-*` model must use `$NVIDIA_API_BASE`; every OpenRouter model must use `$OPENROUTER_API_BASE`.

---

## Onyx / LiteLLM

### LiteLLM quota exhaustion — contextual RAG indexing stalls

**Symptom:** Celery background workers emit `LLMTimeoutError` or `429 quota exceeded` during contextual-summary indexing; chunk gaps appear in OpenSearch.

**Known instances:**
- 2026-05-03: `qwen2.5`, `qwen3-omni-flash-2025-09-15`, `qwen3-coder-plus-2025-09-23`, `dashscope-qwen-plus` all hit free-tier quota limits simultaneously.
- 2026-05-06: `qwen-cloud-fast` returned repeated DashScope `limit_requests` 429s during the Onyx Documentation connector run.

**Fix:**
1. Check active route status: `deployment/helper/litellm_quota_check.py --timeout 90`.
2. Keep RAG routes in `deployment/onyx/litellm_config.yaml`: `qwen-rag-fast`, `qwen-rag-balanced`, `qwen-rag-vision`, and local `qwen-rag-local`.
3. Restart the LiteLLM container after config edits: `docker compose -f deployment/onyx/docker-compose.yml restart litellm`.
4. If a connector is retrying too often after partial runs, reduce its `refresh_freq` in Postgres rather than repeatedly disabling contextual RAG.

**Prevention:** Check DashScope quota monthly. Keep `gemma2:27b` (Ollama, local) as the final fallback so quota exhaustion on cloud models does not completely block indexing.

---

### OpenSearch KNN search returns empty `_source`

**Symptom:** Onyx retrieval returns hits with metadata but empty document text; chunks appear indexed but content is blank.

**Root cause:** OpenSearch 3.4 KNN derived-source search does not populate `_source` inline. The Onyx backend must hydrate `_source` via a secondary document-id lookup.

**Fix:** Keep `deployment/onyx/Dockerfile.backend` building from the patched source that includes `patch_mcp_tool.py`'s OpenSearch source-hydration fix. Do not switch to an upstream Onyx image without re-verifying this patch is present.

---

### Index Attempts Hang or Loop Forever (0 Batches Processed)

**Symptom:** The Onyx UI shows a connector indexing attempt indefinitely "In Progress" with 0 batches processed, or repeatedly failing and restarting without processing documents. Background logs may show: `RuntimeError('Index attempt <id> is not running, status IndexingStatus.FAILED')`.

**Root cause:** If the `onyx-background` container is restarted while an attempt is running, Celery loses the memory state but the Postgres `index_attempt` row remains `IN_PROGRESS`. Subsequent worker spawns see a corrupted/orphaned task and fail to resume the Celery chain properly, causing a zombie loop.

**Fix:**
1. Manually fail the stuck attempt in the DB: `docker exec onyx-db psql -U postgres -d postgres -c "UPDATE index_attempt SET status = 'FAILED' WHERE status = 'IN_PROGRESS';"`
2. If the connector bypasses Unstructured processing due to cached `document_by_connector_credential_pair` records, force a fresh fetch by clearing the tracking state for that connector ID:
   ```bash
   docker exec onyx-db psql -U postgres -d postgres -c "DELETE FROM document_by_connector_credential_pair WHERE connector_id = <id>;"
   docker exec onyx-db psql -U postgres -d postgres -c "DELETE FROM document WHERE id NOT IN (SELECT id FROM document_by_connector_credential_pair);"
   ```
3. Ensure the vision model is configured in the UI, otherwise `unstructured_to_result` will refuse to send images for summarization.

## Regression Gates

Run these checks after any container recreate, volume reset, or config change:

```bash
# 1. OpenSearch parity
python deployment/helper/onyx_opensearch_cutover.py --json
# Expect: 0 missing, 0 mismatched, 0 extra; active index = danswer_chunk_alibaba_nlp_gte_qwen2_1_5b_instruct

# 2. Ollama models present
docker exec onyx-ollama ollama list
# Expect: gemma2:27b listed

# 3. LiteLLM health
curl -s http://localhost:4000/health | jq .
# Expect: all active model providers green

# 4. DeerFlow run persistence
curl -s -X POST http://localhost:2026/api/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"thread_id":"test-001","messages":[{"role":"user","content":"ping"}]}' \
  | grep run_id
# Then verify:
curl -s http://localhost:2026/api/runs/<run_id_from_above>
# Expect: 200, not 404

# 5. Sandbox file permissions
docker exec <deerflow-sandbox-container> stat /path/to/last/upload
# Expect: permissions include o+r and o+w
```
