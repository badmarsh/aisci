# Deployment & Infrastructure Reference

This document records the actual local deployment shape. For current operational status and open work, use `docs/ops/platform-backlog.md`. For historical-only material, keep `docs/archive/` untouched.

## Canonical Pointers

- Operational source of truth: `docs/ops/platform-backlog.md`
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
| MCP proxy | `http://localhost:8095` | Shared gateway for Consensus, Scite, and similar research tools |
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
| `deployment/deer-flow/` | Vendored DeerFlow checkout plus local project overlays | Live gateway joins both `deer-flow` and `onyx_default`; MCP routes use `http://onyx-mcp-proxy:80/...` inside Docker |
| `deployment/deerflow-custom-backup/2026-05-04-aio-redeploy/` | Pre-redeploy custom overlay backup | Contains local custom skills, Onyx tool package, agent prompt, workflows, playbooks, and pre-change config snapshots; no `.env`, logs, DB, cache, or checkpoint files |

## Production Components (DeerFlow Extras)

To enable asynchronous task queues, observability, and vector search in DeerFlow, use the extras stack:

```bash
cd deployment/deer-flow
docker compose -f docker-compose.yml -f docker-compose.extras.yml up -d
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
cd deployment/deer-flow && make setup-sandbox
cd deployment/deer-flow && make up
```

## Maintenance Notes

- `deployment/onyx/.env` is tracked as a secret-free defaults file. Live keys
  belong in ignored `.env.local` files or private operator config.
- Secret-bearing notes belong in `docs/ops/private/`.
- `mcp_config.yaml` is documentation/reference until a specific client is wired to consume it.
- For OpenSearch migration status and cutover checks, use `docs/ops/onyx-rag-optimization-2026-04-27.md` and `deployment/helper/onyx_opensearch_cutover.py --json`.
- For a clean DeerFlow rebuild, preserve `deployment/deerflow-custom-backup/2026-05-04-aio-redeploy/`, reclone or reset the upstream checkout, then restore only selected overlays instead of copying runtime state, logs, SQLite files, or `.env` files.
- For the Onyx MCP submodule, use the reachable fork in `.gitmodules`
  (`badmarsh/onyx-mcp-server`). The configured compose command requires the
  local SSE support added after upstream `v1.2.2`.
