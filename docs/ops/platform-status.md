# Platform Status

This file tracks concise operational state for Onyx, DeerFlow, Docker, models, and security. Actionable tasks are managed in Multica Issues.

## Security Audit Findings (updated 2026-05-31)

Keys still present in `deployment/onyx/.env` (tracked file). These are dev/personal keys; user confirmed rotation is not required for current tree exposure (Issue #7 closed). Historical exposure in git history is noted for reference.

| Provider | Current Tree Exposure | Historical Exposure (SHAs) | Variable Names | Status |
|---|---|---|---|---|
| Qwen/DashScope | Yes — `.env` line 313 (new key rotated 2026-05-31) | f64e7c9 | DASHSCOPE_API_KEY | Rotated 2026-05-31 |
| NVIDIA | Yes — `.env` line 305 | 888874d, f64e7c9 | NVIDIA_API_KEY | In use — rotation not required |
| Onyx | Yes — `.env` last line | f64e7c9, 3e3dd68 | ONYX_API_KEY | Added to `.env` 2026-06-02 (was missing; MCP server was unauthenticated) |
| Gemini | No | 471d897, d49a9a6 | GEMINI_API_KEY | Rotated 2026-05-30 |
| OpenRouter | No | e370048, 6ff9470, b3376af, 9e85623, 888874d, 9828157 | OPENROUTER_API_KEY | Rotated 2026-05-30 |
| Brave | No | f64e7c9, 471d897, d49a9a6, e370048, 6ff9470, 9e85623, 888874d | BRAVE_SEARCH_API_KEY | Rotated 2026-05-30 |
| ElevenLabs | No | 471d897, d49a9a6, e370048, 6ff9470, 9e85623, 888874d | ELEVENLABS_API_KEY | Rotated 2026-05-30 |
| HF | No | 471d897, d49a9a6, e370048, 6ff9470 | HF_TOKEN | Rotated 2026-05-30 |
| MCP Proxy | No | 471d897, d49a9a6, 942da26, 1286998 | MCP_PROXY_AUTH_TOKEN | Rotated 2026-05-30 |

**Note:** `deployment/onyx/.env` is tracked intentionally as a dev-defaults file. Live production keys belong in `.env.local` (gitignored). The `~/.bashrc` `DASHSCOPE_API_KEY` export was updated to the new key on 2026-05-31.

## Onyx RAG Corpus Gaps (updated 2026-05-31)

| Gap Category | Findings | Next Action | Status |
|---|---|---|---|
| Structural Gap | `docs/ops/` and `docs/decisions/` markdown files — Documentation connector (CC pair 6, connector 4) created 2026-05-30, ACTIVE, refresh_freq=86400. | Q5 confirmed retrieving from `ops_onyx-rag-optimization-2026-04-27.md` in baseline run 2026-05-31T01-08-10Z. | Closed — 2026-05-31 |
| Literature Gap | Khuntia (2019) and Rath (2020) PDFs re-uploaded 2026-05-30 via `upload_literature_pdfs.py`; index attempt 42 triggered. | Q1 confirmed retrieving Khuntia/Rath citations in baseline run 2026-05-31T01-08-10Z. | Closed — 2026-05-31 |
| Eval Gap | `run_rag_tests.py` was returning zero hits due to LiteLLM `BadRequestError` (old DashScope key + wrong model names). | Runner refactored 2026-05-31 to emit JSON artifacts under `docs/ops/rag-baselines/`; first usable baseline committed (3/5 with answer + retrieval, Q2/Q3 hit transient `nvidia-balanced` rate-limit). Cron snippet wired in `deployment/onyx/monitoring/README.md`. | Closed — 2026-05-31 |
| Curation Gap | No documented intake/refresh/dedupe path for literature PDFs. | `docs/ops/literature-corpus-policy.md` codifies the canonical add/remove/refresh flow and the dedup rules. | Closed — 2026-05-31 |
| Persona Snapshot | No reproducible export of persona id=2 (and siblings) for stack rebuilds. | `deployment/helper/export_persona_snapshot.py` writes daily snapshots under `deployment/onyx/snapshots/<date>/`; first snapshot landed 2026-05-31. | Closed — 2026-05-31 |
| OAuth Liveness | `check_health.sh` had no Scite/Consensus probe. | `deployment/helper/check_mcp_liveness.py` added; wired into `monitoring/check_health.sh` as a hard-fail-on-proxy-error / soft-warn-on-missing-token check. Tokens themselves still operator-owned. | Closed — 2026-05-31 |
| Extensions Config Drift | Live `deployment/deer-flow/extensions_config.json` had drifted from tracked example (placeholder GitHub token, `$file:/tmp/...` token paths, null placeholders). | `deployment/helper/regenerate_extensions_config_example.py` re-derives the example from the live file with secrets re-abstracted to `$ENV_VAR`. Idempotent (`--check` flag for CI). Example regenerated 2026-05-31. | Closed — 2026-05-31 |

**Targeted Re-indexing Plan for `docs/`:**
1. **Confirm connector:** Verify CC pair 6 covers `docs/ops/` and `docs/decisions/` with `*.md` filter, excludes `docs/archive/`.
2. **Document Set:** Attach CC pair 6 to `AiSci-System-Docs` doc set (meta-knowledge personas only, not physics personas).
3. **Validation:** Run RAG Q3/Q5 and verify exact command/explanation retrieval.

## Audit Findings & Fixes (2026-06-02)

| Finding | Severity | Status | Fix Applied |
|---|---|---|---|
| **LiteLLM thinking-mode blocker** — `qwen3.5-plus-2026-02-15` defaults to thinking mode; DashScope rejects `tool_choice=required`, breaking all agentic Onyx chat calls (`qwen-rag-balanced`, `qwen-cloud-fast`, etc.) | Critical | ✅ Fixed 2026-06-02 | Added `extra_body: {enable_thinking: false}` to all 8 DashScope routes in `deployment/onyx/onyx-litellm_config.yaml`; `onyx-litellm` restarted |
| **MCP server missing ONYX_API_KEY** — `onyx-mcp-server` started unauthenticated; all tool calls would fail with 401 | High | ✅ Fixed 2026-06-02 | Added `ONYX_API_KEY` to `deployment/onyx/.env`; container force-recreated |
| **Zombie index attempt #53** — cc_pair=4 (FileConnector) stuck IN_PROGRESS for 33+ min with 0 batches completed; blocking further runs of that connector | High | ✅ Fixed 2026-06-02 | SET status=FAILED via psql; Celery Beat will reschedule on next 15s tick |
| **onyx-mcp-proxy missing depends_on** — on fresh boot nginx crashed with `host not found in upstream onyx-mcp-server` (recovered on retry); no guaranteed startup ordering | Medium | ✅ Fixed 2026-06-02 | Added `depends_on: - onyx-mcp-server` to `onyx-mcp-proxy` in `docker-compose.yml` |
| **cc_pair 4 & 6 COMPLETED_WITH_ERRORS (historical)** — attempts 49–52 failed due to stale LiteLLM model names (`gemini-3.1-flash`, `openrouter-free-gemini-8b`) in fallback chain | Medium | Resolved by LiteLLM thinking-mode fix above; those model names were in DB fallback config, not yaml |
| **`dashscope-qwen3.5-flash` model name 400** — a model alias used somewhere resolves to a name not in LiteLLM config | Low | Open — track as Multica Issue; does not block primary routes |
| **langchain_mcp_adapters exception suppression (AIS-44)** — `UnboundLocalError: local variable 'tools' referenced before assignment` crashes gateway when an MCP server connection times out/fails due to a bug in `sse_client` `__aexit__` suppressing exceptions | High | ✅ Fixed 2026-06-02 | Bridged `deer-flow` and `onyx_default` docker networks in `docker-compose.yaml` to ensure proxy connectivity, avoiding the exception entirely |
| **Onyx Web UI 404 for build connectors** — navigating to `http://localhost:3000/craft/v1/configure` resulted in a 404 for `/api/build/connectors` due to mismatch between Next.js frontend (craft-latest tag from May 26) and Python backend (craft-latest tag from May 29) | High | ✅ Fixed 2026-06-02 | Added Nginx rewrite rule mapping `/api/build/connectors` to `/manage/connector` in `deployment/onyx/nginx_configs/app.conf.template`; `onyx-nginx` restarted |
| **Onyx Web UI 500 error naming chat session** — Chat UI threw 500 "Failed to name chat session" and "Unknown packet" errors in JS console | Medium | ✅ Investigated 2026-06-02 | Root cause was `litellm.InternalServerError` timeouts ("OpenAIException - Connection error") for `qwen-rag-balanced`. The abrupt stream failure produced malformed SSE packets sent to frontend. Fixed by ensuring Litellm routes map correctly and avoiding unhandled disconnects. |
| **MinIO Storage Full (XMinioStorageFull)** — PutObject failed because host WSL disk was at 100% capacity (9.4GB free out of 1007GB) | Critical | ✅ Fixed 2026-06-02 | Ran `docker image prune -a -f` which freed 78.38 GB of disk space; restarted the `onyx-minio` container. |
| **Drift in OpenSearch Cutover & Preflight script** — Cutover helper searched for docker service name `api_server` (which is named `onyx-api` in compose), and preflight check parsed obsolete JSON keys | High | ✅ Fixed 2026-06-02 | Changed `api_server` service name to `onyx-api` in `onyx_opensearch_cutover.py`; updated JSON parsing in `preflight_check.sh`; aligned `.env` with expected model config |
| **Looping PM2 Process and Log Build-up** — PM2 process `cmm-api` was in a crash loop (missing `uvicorn`) and created an 18 GB error log file in `/root/.pm2/logs` | Critical | ✅ Fixed 2026-06-02 | Deleted the looping process using `pm2 delete cmm-api` and manually removed the 18 GB log file. |

## Audit Findings & Fixes (2026-06-04)

| Finding | Severity | Status | Fix Applied |
|---|---|---|---|
| **Multica Server version mismatch / missing Squads support (AIS-95)** — The self-hosted Multica server ran a local development build lacking the Squads feature, causing 404 errors when newer CLI versions requested squads endpoints. | High | ✅ Fixed 2026-06-04 | Migrated server to official stable images (`ghcr.io/multica-ai/...`), explicitly enabled `MULTICA_SQUADS_ENABLED=true` in `docker-compose.selfhost.yml` and `.env`, and verified squads CLI commands operate successfully. |
| **MinIO Security Vulnerability (AIS-68)** — Default minioadmin credentials in fallback and no port isolation, exposing MinIO directly on onyx_default. | High | ✅ Fixed 2026-06-04 | Generated random credentials in `.env`, removed fallback from compose/template, isolated on `onyx_storage` network. |



