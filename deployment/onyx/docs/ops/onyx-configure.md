# Onyx Runtime Configuration Reference

_Reflects deployment state as of 2026-05-06._

Canonical copy: `docs/ops/onyx-configure.md`.

## Active Embedding Model

| Setting | Value |
|---|---|
| Model | `Alibaba-NLP/gte-Qwen2-1.5B-instruct` |
| Dimensions | 1536 |
| DB search_settings id | 10 (status: PRESENT) |
| Compatibility shim | `deployment/helper/sitecustomize.py` |

Do not change the embedding model without a full reindex. The shim in
`deployment/helper/sitecustomize.py` is required for this model under
Transformers 5 and is loaded via `PYTHONPATH` in both model-server commands.

## Runtime Decisions

- **Craft**: `ENABLE_CRAFT=true`, `IMAGE_TAG=craft-latest`.
- **Workers**: API server runs one Uvicorn worker with `--factory`.
- **Timeouts**: Nginx proxy and `LLM_SOCKET_READ_TIMEOUT` are 600s.
- **File storage**: MinIO always starts with `FILE_STORE_BACKEND=s3`.
- **Redis**: AOF persistence is enabled in named volume `redis_data`.
- **Workspace mount**: `/home/ubuntu/aisci` is read-only in all containers
  except `code-interpreter`.
- **OpenSearch retrieval**: enabled for the Alibaba/1536 active index.
- **Connector scheduler**: `check_for_indexing` runs every 15s; connector
  `refresh_freq` controls when a new attempt is created.
- **Onyx Documentation connector**: CC pair `11`, connector `15`, source `WEB`,
  uses `refresh_freq=86400` (daily).
- **Contextual RAG LLM**: `search_settings id=10` uses `qwen-cloud-fast` via
  LiteLLM. LiteLLM has RAG fallbacks: `qwen-rag-fast`,
  `qwen-rag-balanced`, `qwen-rag-vision`, and local `qwen-rag-local`.

## LiteLLM Route Check

```bash
deployment/helper/litellm_quota_check.py --timeout 90
```

## Secrets And Env Files

- `.env` is tracked and secret-free.
- `.env.local` is ignored and holds live provider keys.
- Compose loads `.env` first and `.env.local` second so local secrets override
  tracked empty defaults.

## MCP Server

- Host-local clients: `http://127.0.0.1:8095/...`.
- DeerFlow containers on `onyx_default`: `http://onyx-mcp-proxy:80/...`.
- Host port `8095` remains bound to `127.0.0.1`.
- Nested MCP source is reachable at
  `https://github.com/badmarsh/onyx-mcp-server.git`.

## Celery Beat

The `background` service command patches out the duplicate
`DynamicTenantScheduler.setup_schedule()` call. The schedule file lives at
`/tmp/celerybeat-schedule` inside the container.

## Local Images

`onyx-python-webdeps:3.11` supplies Python web dependencies for `auth_proxy` and
`image_bridge`. Rebuild when buildx/DNS are fixed:

```bash
DOCKER_BUILDKIT=0 docker build -t onyx-python-webdeps:3.11 \
  -f deployment/onyx/Dockerfile.python-webdeps deployment/onyx/
```
