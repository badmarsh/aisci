# Deployment & Infrastructure Reference

This document records the actual local deployment shape. For current operational status and open work, use Multica Issues (`multica issue list`) and `docs/ops/platform-status.md`. For historical-only material, keep `docs/archive/` untouched.

## Canonical Pointers

- Operational source of truth: Multica Issues (`multica issue list`) and `docs/ops/platform-status.md`
- Active implementation/review tracking: GitHub Issues and Pull Requests
- High-level milestones only: `ACTION_PLAN.md`
- Science queue and evidence: `research/robert/next-actions.md`, `research/robert/evidence-ledger.md`
- Durable architecture and process decisions: `docs/decisions/`

## Live Services

| Service | Host URL | Purpose |
|---|---|---|
| Onyx UI | `http://localhost:3000` | Private RAG, document ingestion, and literature search |
| DeerFlow | `http://localhost:2026` | Multi-agent orchestration and tool execution |
| LiteLLM proxy | `http://localhost:4000` | LLM routing and key management |
| MCP proxy | `http://localhost:8095` | Shared gateway for Consensus, Scite, Semantic Scholar, and similar research tools |
| Unstructured | `http://localhost:9560` | Local document parsing and extraction |
| Ollama | `http://localhost:11434` | Local LLM and embedding model serving |

## Actual Repository Layout

| Path | Role | Notes |
|---|---|---|
| `deployment/onyx/docker-compose.yml` | Live compose root for the Onyx stack | Builds `api_server` and `background` from `Dockerfile.backend`; mounts the MCP proxy template from `deployment/onyx/nginx_configs/` |
| `deployment/onyx/Dockerfile.backend` | Live custom backend build layer | Referenced by `api_server` and `background` in compose; do not delete without replacing those build references |
| `deployment/onyx/Dockerfile.python-webdeps` | Local Python web-dependency image layer | Builds `onyx-python-webdeps:3.11` for `auth_proxy` and `image_bridge`; rebuild is blocked until Docker buildx/DNS are healthy |
| `deployment/helper/sitecustomize.py` | Runtime compatibility shim | Injected into model-server containers via `PYTHONPATH` for Transformers 5 / Qwen2 embedding compatibility |
| `deployment/data/nginx/` | Live runtime mount for the main Onyx nginx service | `nginx` mounts `../data/nginx` and copies those templates into `/etc/nginx/conf.d/` at container start |
| `deployment/onyx/nginx_configs/mcp_proxy.conf.template` | Live MCP proxy template | Mounted by the `mcp_proxy` service; secret-free and env-driven |
| `deployment/onyx/nginx_mcp_proxy.conf` | Standalone reference copy | Not mounted by current compose; keep only as a documented manual/static example |
| `mcp_config.yaml` | Repo-local MCP client reference | Not auto-loaded by Onyx compose; documents a project-level client-facing MCP layout and should stay secret-free |
| `deployment/deer-flow/` | Historical backup and patch reference only — DeerFlow source is NOT in the aisci repo | The live DeerFlow checkout is at `C:\users\marek\deer-flow` (Windows-native). `deployment/deer-flow/` may contain legacy custom overlays and should not be treated as the live compose root. |
| `deployment/deerflow-custom-backup/2026-05-04-aio-redeploy/` | Pre-redeploy custom overlay backup | Contains local custom skills, Onyx tool package, agent prompt, workflows, playbooks, and pre-change config snapshots; no `.env`, logs, DB, cache, or checkpoint files |

## DeerFlow — Canonical Path (Windows-Native)

DeerFlow is maintained as a Windows-native checkout at `C:\users\marek\deer-flow`, **not** inside the `aisci` repo. All `docker compose` commands for DeerFlow must be run from that path (or from WSL as `/mnt/c/users/marek/deer-flow`).

```bash
# Start DeerFlow (gateway, frontend, nginx) from WSL:
cd /mnt/c/users/marek/deer-flow
docker compose -f docker/docker-compose-dev.yaml up -d gateway nginx frontend

# Check logs:
docker logs deer-flow-gateway

# DeerFlow UI:
# http://localhost:2026
```

The gateway container attaches to the `onyx_default` network for internal Onyx MCP proxy access.
MCP routes in `extensions_config.json` (in the DeerFlow checkout) use `http://onyx-mcp-proxy:80/...`.

## Production Components (DeerFlow Extras)

To enable asynchronous task queues, observability, and vector search in DeerFlow, run from the Windows-native checkout:

```bash
cd /mnt/c/users/marek/deer-flow
docker compose -f docker/docker-compose-dev.yaml -f docker/docker-compose-extras.yaml up -d
```

| Service | Host URL | Purpose |
|---|---|---|
| Prometheus | `http://localhost:9090` | System metrics, token usage, and latency tracking |
| Redis | `http://localhost:6379` | Message broker for ARQ async task queue |
| Chroma | `http://localhost:8000` | Vector database for research report indexing |

## Operational Commands

```bash
docker ps
docker exec onyx-ollama ollama list
docker logs -f deer-flow-gateway
# DeerFlow compose (from WSL):
cd /mnt/c/users/marek/deer-flow && docker compose -f docker/docker-compose-dev.yaml ps
```

## Pre-Reindex Checklist

Run this before **any** reindex, backend image rebuild, or embedding model change:

```bash
# 1. Full preflight gate (parity + embedding alignment + search probe)
bash deployment/onyx/preflight_check.sh

# 2. OpenSearch parity detail (standalone)
python3 deployment/helper/onyx_opensearch_cutover.py --json

# 3. Runtime health (alembic, index failures, Redis, LiteLLM)
bash deployment/onyx/monitoring/check_health.sh
```

All three must exit 0 before triggering a reindex. Run the same three commands after the reindex completes to confirm parity is restored.

**Critical invariants to verify before reindexing:**
- `DOCUMENT_ENCODER_MODEL=BAAI/bge-m3` in `.env`
- `EMBEDDING_DIM=1024` and `DOC_EMBEDDING_DIM=1024` in `.env`
- DB `search_settings` model and dim match the above (id=26, PRESENT, 1024-dim)
- Active OpenSearch index: `danswer_chunk_baai_bge_m3`
- `enable_opensearch_retrieval=true` in the cutover output

## Onyx–DeerFlow Bridge

| Component | Internal URL | Host URL |
|---|---|---|
| `onyx-mcp-proxy` | `http://onyx-mcp-proxy:80` (on `onyx_default`) | `http://127.0.0.1:8095` |
| `onyx-api-server` | `http://onyx-api-server:8080` (on `onyx_default`) | — |
| `deer-flow-gateway` | — | `http://127.0.0.1:8001` |

`deer-flow-gateway` is attached to both `deer-flow-dev_deer-flow-dev` and `onyx_default`. MCP routes in `extensions_config.json` use `http://onyx-mcp-proxy:80/...`. Renaming any container or network requires updating both `extensions_config.json` and `config.yaml`.

## Maintenance Notes

- `deployment/onyx/.env` is tracked as a defaults file. Live API keys belong in ignored `.env.local` files or private operator config. The tracked `.env` intentionally includes the embedding model setting so agents can detect model drift.
- Secret-bearing notes belong in `docs/ops/private/`.
- `mcp_config.yaml` is documentation/reference until a specific client is wired to consume it.
- For OpenSearch migration status and cutover checks, use `deployment/helper/onyx_opensearch_cutover.py --json`.
- For a clean DeerFlow rebuild, restore from `deployment/deerflow-custom-backup/2026-05-04-aio-redeploy/` or clone fresh at `C:\users\marek\deer-flow`. The live checkout is Windows-native; do not attempt to manage it from within the aisci repo.
- For the Onyx MCP submodule, use the reachable fork in `.gitmodules` (`badmarsh/onyx-mcp-server`). The configured compose command requires the local SSE support added after upstream `v1.2.2`.
- For a full system architecture diagram, see `docs/ops/architecture-overview.md`.
- For DeerFlow end-to-end smoke tests, see `docs/ops/deerflow-smoke-tests.md`.
