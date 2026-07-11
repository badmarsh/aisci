# Troubleshooting

Operational runbook for diagnosing and resolving known failure modes across Onyx, MCP, and sandbox services.

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

