# Onyx Runtime Configuration Reference

_Reflects deployment state as of 2026-06-19. Last config-drift corrections applied 2026-06-19 (optimal local RAG stack migration)._

This is the canonical Onyx runtime reference. The short mirror under
`deployment/onyx/docs/ops/` exists for operators working inside the deployment
tree; update both when runtime assumptions change.

## Active RAG Stack (as of 2026-06-19)

| Pipeline Stage | Model | Location | Notes |
|---|---|---|---|
| **Document parsing** | `onyx-unstructured` | Local (container) | ✅ running |
| **Embedding** | `Alibaba-NLP/gte-Qwen2-1.5B-instruct` | Local (model-server) | 1536-dim, MTEB ~68, multipass enabled |
| **Contextual RAG** | `gemma2:27b` | Local (Ollama) | Index-time chunk context generation |
| **Visual RAG** | `qwen2.5vl:7b` | Local (Ollama) | Image/figure extraction from PDFs |
| **Reranking** | `BAAI/bge-reranker-v2-m3` | Local (model-server) | Cross-encoder, best multilingual reranker |
| **Chat / personas** | Cloud via LiteLLM (Qwen/DashScope) | Cloud | User-facing chat always cloud |

## Active Embedding Model

| Setting | Value |
|---|---|
| Model | `Alibaba-NLP/gte-Qwen2-1.5B-instruct` |
| Dimensions | 1536 |
| DB search_settings id | 27 (status: PRESENT, reindex in progress) |
| New OpenSearch index | `danswer_chunk_alibaba_nlp_gte_qwen2_1_5b_instruct` (reindex triggered 2026-06-19) |
| Previous index | `danswer_chunk_baai_bge_m3` (670 docs, now PAST) |
| DB schema | Alembic `01c63968ff8f` |
| Query prefix | `Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery: ` |
| Multipass indexing | `true` (higher indexing quality) |
| Contextual RAG | `true`, model: `gemma2:27b` via Ollama (model_configuration id=784) |
| `.env` | `DOCUMENT_ENCODER_MODEL=Alibaba-NLP/gte-Qwen2-1.5B-instruct`, `EMBEDDING_DIM=1536`, `DOC_EMBEDDING_DIM=1536` |

Do not change the embedding model without a full reindex plan and evidence-ledger entry.

## Reranking Model

| Setting | Value |
|---|---|
| Model | `BAAI/bge-reranker-v2-m3` |
| Location | Local model-server (onyx-inference, onyx-indexing) |
| `.env` | `RERANK_MODEL_NAME=BAAI/bge-reranker-v2-m3` |
| Compose | `RERANK_MODEL_NAME=${RERANK_MODEL_NAME:-BAAI/bge-reranker-v2-m3}` in both model-server env blocks |

## Contextual RAG Configuration

| Setting | Value |
|---|---|
| Enabled | `true` (DB: `search_settings.enable_contextual_rag=true`) |
| Model | `gemma2:27b` via direct Ollama (`http://onyx-ollama:11434`) |
| LLM provider | `ollama_chat` (llm_provider id=6) |
| model_configuration id | 784 (`gemma2-27b-contextual`) |
| Purpose | Generates a short context sentence per chunk at index time (improves retrieval precision) |

## Visual RAG Configuration

| Setting | Value |
|---|---|
| Vision model | `qwen-rag-vision` → `qwen2.5vl:7b` via Ollama |
| DB | `llm_provider id=2, default_vision_model=qwen-rag-vision` |
| Fixed | 2026-06-19 (was `qwen-vl-vision`, non-existent route) |


## Runtime Decisions

- **Craft**: `ENABLE_CRAFT=true` with `IMAGE_TAG=craft-latest` (corrected 2026-05-30 — the CRAFT binary only ships in `craft-latest`; the stack was recreated to apply it). Do not set Craft false as a crash workaround; fix the startup race instead.
- **Workers**: API server runs one Uvicorn worker with `--factory` to avoid the
  Vespa dual-activation race on startup.
- **Structured logs**: `LOG_FORMAT=json` is the tracked default and is passed
  into the API, background, inference, and indexing services.
- **Timeouts**: Nginx proxy timeouts and `LLM_SOCKET_READ_TIMEOUT` are 600s for
  large reasoning-model calls.
- **File storage**: MinIO is always started. `FILE_STORE_BACKEND=s3` and
  `S3_ENDPOINT_URL=http://onyx-minio:9000` (the compose service name is `onyx-minio`, not `minio`).
- **Redis**: AOF persistence is enabled and stored in named volume `redis_data`.
  This preserves queued Celery jobs across Redis container restarts.
- **Workspace mount**: `/home/ubuntu/aisci` is mounted read-only into all Onyx
  containers except `code-interpreter`.
- **OpenSearch retrieval**: `ENABLE_OPENSEARCH_RETRIEVAL_FOR_ONYX=true` with
  the Alibaba/1536 active index.
- **Connector scheduler**: Celery Beat runs `check_for_indexing` every 15s and
  `check_for_vespa_sync_task` every 20s. Individual connector retry cadence is
  controlled by each connector's `refresh_freq` in Postgres.
- **Onyx Documentation connector**: CC pair `11`, connector `15`, source `WEB`,
  now uses `refresh_freq=86400` (daily). It was previously `1800` seconds and
  retried too often after partial/error runs.
- **Contextual RAG LLM**: `search_settings id=10` has contextual RAG enabled and
  currently points at `qwen-cloud-fast` through the `LiteLLM` provider.

## LiteLLM RAG Routes

`deployment/onyx/onyx-litellm_config.yaml` defines these RAG-focused routes (this is the **live** file mounted by the container; `litellm_config.yaml` is a stale reference copy — do not edit it):

| Route | Purpose |
|---|---|
| `qwen-cloud-fast` | Existing contextual-RAG route used by `search_settings id=10` |
| `qwen-rag-fast` | Low-cost non-thinking Qwen flash pool for summaries and routine RAG |
| `qwen-rag-balanced` | Higher-quality Qwen route for harder document processing |
| `qwen-rag-vision` | Vision-capable route for image/table/page-section summaries (backed by `qwen2.5vl:7b` on Ollama; set as `default_vision_model` in `llm_provider` id=2 — fixed 2026-06-19) |
| `qwen-rag-local` | Local Ollama `qwen2.5vl:7b` fallback when cloud quota is exhausted |
| `gemma2` | Local Ollama `gemma2:27b` — secondary fallback in router chains |

Router fallbacks cool down a failing deployment for **30 seconds** after one failure and
fall back from `qwen-cloud-fast` through `qwen-rag-local` and `gemma2`. Probe route health with:

```bash
deployment/helper/litellm_quota_check.py --timeout 90
```

## GPU Acceleration

- Host GPU: NVIDIA RTX 3090. GPU device access is configured in
  `deployment/onyx/docker-compose.yml` for `ollama`, `inference_model_server`,
  and `indexing_model_server` (plus `onyx-unstructured`, see below).
- The active model servers run the 1536-dim Alibaba model above. `nemotron_embed_vl`
  is an optional NVIDIA NIM trial service (up to 2048-dim) and is **not** part of the
  active retrieval path unless explicitly started and validated at
  `http://localhost:8000/v1/health/ready`. Switching to it requires a new search
  setting, reindex, and `input_type` validation.

## Multimodal PDF Indexing (Hi-Res + Vision)

Onyx extracts images and tables from PDFs using `unstructured` (YOLOX), then summarizes them using a Vision LLM.

**Architecture / Assumptions:**
- `IMAGE_ANALYSIS_ENABLED=true` and `UNSTRUCTURED_STRATEGY=hi_res` must be active in `.env`.
- The `onyx-unstructured` service uses a host GPU via `deploy: nvidia: count: 1` in `docker-compose.yml`.
- **GPU Driver Bootstrapping:** The upstream unstructured image lacks `onnxruntime-gpu`. After any container `recreate`, operators MUST run the following command to bootstrap CUDA execution:
  ```bash
  docker exec onyx-unstructured bash -c "python3 /usr/share/python-wheels/pip-26.0.1-py3-none-any.whl/pip install -q onnxruntime-gpu --extra-index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/onnxruntime-cuda-12/pypi/simple/"
  ```
- **Vision Model Config:** The vision model (`qwen2.5vl:7b` via LiteLLM `qwen-rag-vision` route) is configured as `default_vision_model` in `llm_provider` row id=2 in Postgres (fixed 2026-06-19 — was set to non-existent `qwen-vl-vision`). If the background worker emits a `no vision-capable LLM` warning, verify this DB value with: `docker exec onyx-db psql -U postgres -d postgres -c 'SELECT id, name, default_vision_model FROM llm_provider WHERE id=2;'`

## Secrets And Env Files

- `deployment/onyx/.env` is a **tracked file that currently holds live API keys** (DashScope, NVIDIA, ElevenLabs, OpenRouter, Brave, ONYX_API_KEY). The intended policy (secret-free tracked defaults + secrets in gitignored `.env.local`) has not been fully implemented. Rotation of these keys is tracked in `platform-status.md`.
- `deployment/onyx/.env.local` is gitignored and will override any variable set in `.env` if it exists. Currently it does not exist on this host.
- Compose loads `.env` first and `.env.local` second so local secrets would override tracked defaults if the file were present.
- Do not print key values from history or local env files. If auditing history, report only file paths, variable names, and commit SHAs.

## MCP Server

- Runtime route for host-local clients: `http://127.0.0.1:8095/...`.
- Runtime route for DeerFlow containers on the shared Docker network:
  `http://onyx-mcp-proxy:80/...`.
- Host port `8095` is intentionally bound to `127.0.0.1`, not `0.0.0.0`.
- `deployment/deer-flow/docker/docker-compose.yaml` connects the gateway to the
  external `onyx_default` network so DeerFlow can use the internal service name.
- The nested MCP source now points at `https://github.com/badmarsh/onyx-mcp-server.git`
  because the local SSE/token-fallback commits must be reachable for fresh
  clones and rebuilds.

## Celery Beat

Onyx uses `DynamicTenantScheduler` (persistent). The `background` service command
patches out the duplicate `setup_schedule()` call that caused a gdbm lock
warning. The schedule file lives at `/tmp/celerybeat-schedule` inside the
container.

The same startup chain applies `deployment/helper/patch_onyx_monitoring.py` so
Onyx's memory monitor recognizes the current Celery worker names
(`docfetching`, `docprocessing`, `user_file_processing`, etc.) instead of
emitting false `Missing processes` errors every five minutes.

## Local Images

- `onyx-python-webdeps:3.11` supplies Python web dependencies for
  `auth_proxy` and `image_bridge`.
- The image was originally built from a running container because Docker buildx
  and PyPI DNS were unavailable on the host.
- Reproducible rebuild path, once build tooling/networking are fixed:

```bash
DOCKER_BUILDKIT=0 docker build -t onyx-python-webdeps:3.11 \
  -f deployment/onyx/Dockerfile.python-webdeps deployment/onyx/
```

## Verification Commands

```bash
cd deployment/onyx
docker compose config --quiet
curl -fsS http://127.0.0.1:3000/api/health
docker exec onyx-redis redis-cli info persistence | grep aof_enabled
docker ps --format '{{.Names}} {{.Status}}' | grep onyx
```

Expected invariants:

- `/api/health` returns 200.
- `aof_enabled:1`.
- No Onyx container is restarting.
- Model-server embedding check returns one 1536-dimensional vector with norm
  close to 1.0.
