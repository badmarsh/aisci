# Onyx Runtime Configuration Reference

_Reflects deployment state as of 2026-05-06_

## Active Embedding Model

| Setting | Value |
|---------|-------|
| Model | `Alibaba-NLP/gte-Qwen2-1.5B-instruct` |
| Dimensions | 1536 |
| DB search_settings id | 10 (status: PRESENT) |
| Compatibility shim | `deployment/helper/sitecustomize.py` |

**Important**: Do not change the embedding model without a full reindex.
The shim in `deployment/helper/sitecustomize.py` is required for this model
under Transformers 5. It is loaded via `PYTHONPATH` in both model-server
container startup commands.

## Key Runtime Decisions

- **Workers**: API server runs 1 Uvicorn worker (`--factory`) to avoid
  the Vespa dual-activation race on startup.
- **Timeouts**: Nginx proxy and `LLM_SOCKET_READ_TIMEOUT` are both 600s.
  This is required for large reasoning models (qwen3-235b-a22b with
  `enable_thinking`).
- **File storage**: MinIO (S3-compatible) is always started.
  `FILE_STORE_BACKEND=s3`, `S3_ENDPOINT_URL=http://minio:9000`.
- **Redis**: AOF persistence enabled, data in named volume `redis_data`.
  This preserves queued Celery jobs across cache container restarts.
- **Workspace mount**: `/home/ubuntu/aisci` is mounted `:ro` into all
  containers except `code-interpreter`. The shim at
  `deployment/helper/sitecustomize.py` is injected via PYTHONPATH, not
  by writing into the container image.

## Celery Beat

Onyx uses `DynamicTenantScheduler` (persistent). A startup patch in the
`background` service command removes the duplicate `setup_schedule()` call
that caused a gdbm lock warning. The schedule file lives at
`/tmp/celerybeat-schedule` inside the container.

## MCP Server

- Runtime: Works via Compose `command` wrapper (Node.js called directly).
- Docker image: Build is blocked pending `docker-buildx-plugin` install
  and stable PyPI DNS. See platform-backlog.md.
- Proxy: `onyx-mcp-proxy` bound to `127.0.0.1:8095` (not 0.0.0.0).
