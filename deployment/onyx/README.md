# Onyx Deployment Directory

This directory is the compose and build root for the local Onyx stack. For current status and open tasks, use [docs/ops/platform-backlog.md](../../docs/ops/platform-backlog.md). For the concrete deployment map, use [docs/ops/deployment-reference.md](../../docs/ops/deployment-reference.md).

## What Lives Here

- `docker-compose.yml`: live compose definition for the Onyx stack
- `Dockerfile.backend`: live custom backend build used by `api_server` and `background`
- `litellm_config.yaml`: live LiteLLM routing config
- `nginx_configs/mcp_proxy.conf.template`: live template mounted by the `mcp_proxy` service
- `nginx_mcp_proxy.conf`: standalone reference copy for the MCP proxy, not the live compose mount
- `env.template`: tracked environment template only
- helper scripts such as `patch_mcp_tool.py`, `trigger_reindex.py`, and parser/indexing utilities

## Path Responsibilities

- The main Onyx web proxy does not use `nginx_configs/`; it currently mounts `deployment/data/nginx/` from the sibling path `../data/nginx`.
- The MCP proxy does use `nginx_configs/mcp_proxy.conf.template`.
- Secrets belong in the untracked local `.env` or other untracked local material, not in tracked config files.
- `nemotron_embed_vl` is a trial NVIDIA NIM embedding service. Start it with `NGC_API_KEY` available in the shell or ignored `.env`, then verify `http://localhost:8000/v1/health/ready` before testing `http://localhost:8000/v1/embeddings`.

## Notes

- `openapi.json` is not a maintained source file in this repository and is intentionally no longer tracked.
- Historical status notes were retired in favor of `docs/ops/platform-backlog.md`.
