# Troubleshooting Guide

## Common Issues and Solutions

### 1. MCP Services Not Responding
**Issue:** Consensus or Scite MCP tools fail in chat with `Please Reconnect to the server`, or the MCP services return 502/connection errors.
**Solution:**
- Check the MCP proxy container status: `docker ps | grep mcp_proxy`
- Reconnect the affected MCP server from the chat-bar MCP dropdown if the tool error includes `Please Reconnect to the server`
- Restart the container: `docker restart onyx-mcp_proxy-1`
- Verify the configuration: `deployment/onyx/nginx_configs/mcp_proxy.conf.template`

### 2. Physics Validation Mode Not Available
**Issue:** Physics Validation Mode persona doesn't appear in Onyx UI
**Solution:**
- Verify the persona was created: Check database or run the creation script again
- Restart Onyx services: `cd ~/aisci/deployment/onyx && docker compose restart`

### 3. GPU Not Detected
**Issue:** GPU acceleration not working for document processing
**Solution:**
- Check NVIDIA drivers: `nvidia-smi`
- Verify Docker is configured for GPU access: `docker run --rm --gpus all nvidia/cuda:11.0-base-ubuntu20.04 nvidia-smi`
- Check Ollama container: `docker exec onyx-ollama-1 nvidia-smi`

### 4. API Connection Issues
**Issue:** Cannot connect to Onyx API
**Solution:**
- Verify API server is running: `docker ps | grep api_server`
- Check the API key is correctly set in environment
- Verify network connectivity between containers

### 5. Volume Mapping Problems
**Issue:** Files created by Onyx not appearing in expected locations
**Solution:**
- Verify volume configuration in `deployment/onyx/docker-compose.yml`
- Check permissions on mounted directories
- Ensure the directories exist on the host system

### 6. Vespa Feed Blocked (507 Insufficient Storage)
**Issue:** Vespa feed blocked with 507 NO_SPACE error. Disk exhaustion at 85%.
**Solution:**
- In-container edits to `/app/onyx/document_index/vespa/app_config/services.xml.jinja` are temporary and do not survive a recreate.
- After the backend recreate on `2026-04-28`, `onyx-index-1` again logged `configured limit is 85.0%` and re-blocked feed at `2026-04-28 14:12:34 UTC`.
- The durable fix is now tracked in `deployment/onyx/Dockerfile.backend`, which patches Vespa's generated template from `<disk>0.85</disk>` to `<disk>0.95</disk>` before `api_server` redeploys the application package.
- On `2026-04-28`, `api_server` and `background` were rebuilt and recreated from that tracked source, and the live template inside `onyx-api_server-1` now reports `0.95`.
- Background logs after the recreate show the previously failing `vespa_metadata_sync_task` calls succeeding instead of returning 507 feed-block errors.
- **Status:** Durably patched in tracked source and deployed on `2026-04-28`. Re-verify after any future backend-image change or stack recreate.

### 7. Background Worker Crash Loops (Craft Templates)
**Issue:** `onyx-api_server-1` and `onyx-background-1` racing to run `setup_craft_templates.sh` concurrently on shared volume, causing `npm install` failures and `ENOTEMPTY` errors.
**Solution:**
- Keep Craft enabled with `IMAGE_TAG=craft-latest`, `ENABLE_CRAFT=true`, and matching `ONYX_WEB_SERVER_IMAGE` / `ONYX_MODEL_SERVER_IMAGE` image tags.
- If the shared Craft volumes race again, recreate `api_server` and `background` after confirming the image/tag pairing above; do not disable Craft as a workaround.
- **Status:** Correct Craft pairing is applied in the local ignored `.env` as of 2026-05-02.

### 8. OpenSearch Migration Failure
**Issue:** Chunk migration from Vespa to OpenSearch can fail on paginated Vespa visit data that contains metadata-only records with no `document_id`, which can surface as `KeyError: 'document_id'` or as a candidate-count mismatch.
**Solution:**
- Deploy the backend patch that skips metadata-only visit records missing `document_id` in the OpenSearch migration transformer.
- Deploy the matching Vespa metadata-update patch that removes `?create=true` from document PUTs so metadata refreshes cannot create skeletal docs for missing chunks.
- Re-run the helper visit check after deploy. The `2026-04-28` validation produced `raw_total=403`, `with_document_id=241`, `missing_document_id=162`, `transformed_total=241`, `skipped_total=162`, and `errored_total=0`.
- Probe a random missing doc id directly after deploy. The `2026-04-28` validation returned `GET 404 -> PUT 200 -> GET 404`, and Vespa chunk count stayed `464`, confirming that metadata updates no longer materialize new skeletal docs.
- Use `deployment/helper/onyx_opensearch_cutover.py --json` as the live parity check before any tenant flip. It compares Postgres `document.id` chunk counts against the active OpenSearch `search_settings.index_name` index and reports whether cutover is actually safe.
- The `2026-04-28` live audit still showed cutover blocked: the active alt index had `65` docs but `37` chunk-count mismatches, the primary OpenSearch index was absent, `opensearch_document_migration_record` still had `0` rows, and `opensearch_tenant_migration_record.enable_opensearch_retrieval` remained `false`.
- To repair that parity gap, full `REINDEX` runs were queued through Onyx's internal trigger path on `2026-04-28` for connector/credential pairs `(11,0)`, `(13,8)`, `(14,9)`, `(10,6)`, `(4,3)`, `(1,1)`, `(7,5)`, and `(3,2)`.
- The Vespa 507 feed-block was preventing those rebuilds from progressing until the disk-threshold patch above was deployed. After the recreate, the blocker shifted from Vespa NO_SPACE to waiting for the queued reindex attempts to finish and repopulate OpenSearch.
- As of `2026-05-02`, the active Alibaba index is `danswer_chunk_alibaba_nlp_gte_qwen2_1_5b_instruct`; use the helper's `active_index_name`, not contextual-RAG status alone, to decide which OpenSearch index is live.
- OpenSearch 3.4 KNN indexes can fail search requests that return `_source` while still allowing `GET /_doc/{id}`. The tracked `patch_mcp_tool.py` startup patch makes Onyx search request IDs first and hydrate sources by document GET; rebuild/recreate the backend image after changing that patch.
- **Status:** Transformer patch and OpenSearch search-source hydration patch deployed. The Alibaba/1536 rebuild reached active-index parity on `2026-05-02`: `279` documents, `629` chunks, `0` missing/mismatched/extra documents, and `enable_opensearch_retrieval=true`.

### 9. Stale Index Attempt Blocks Fresh Runs
**Issue:** A connector pair can stay stuck in `IN_PROGRESS` with a frozen heartbeat, and background logs show `skipped_active=1` instead of starting a new run.
**Solution:**
- Clear the stale attempt through the app code path with `mark_attempt_failed()` rather than raw SQL.
- On `2026-04-28`, failing attempt `312` this way unblocked connector pair `10` (`Onyx Docs`), and the background worker created new attempt `344`.
- On `2026-04-28`, the same pattern reappeared during the OpenSearch cutover after `background` was recreated while attempts `374`-`379` were already active. The new worker kept polling those rows but did not own the original docfetching/docprocessing subprocesses, so the attempts had to be failed through `mark_attempt_failed()` before full reruns could be queued again.
- Treat any failures on the new attempt as a separate issue; they do not mean the stale-attempt blocker has returned.
- **Status:** Verified on `2026-04-28`.

## Diagnostic Commands

### Check all Onyx containers:
```bash
docker ps | grep onyx
```

### Check MCP services:
```bash
curl -s http://localhost:8095/consensus/health
curl -s http://localhost:8095/scite/health
```

### Verify Physics Validation persona:
```bash
curl -s -H "Authorization: Bearer $ONYX_API_KEY" http://localhost:3000/api/admin/persona
```

### Check GPU status:
```bash
nvidia-smi
docker exec onyx-ollama-1 nvidia-smi
```

## When to Reset

If multiple issues persist:
1. Stop all Onyx services: `cd ~/aisci/deployment/onyx && docker compose down`
2. Restart: `cd ~/aisci/deployment/onyx && docker compose up -d`
3. Re-create or re-sync the Physics Validation persona if the database was reset.

Do not run `docker system prune`, remove volumes, or delete containers as part of routine troubleshooting unless the operator explicitly approves the destructive cleanup for that incident.
