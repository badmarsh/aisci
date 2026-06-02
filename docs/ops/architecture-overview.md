# Architecture Overview

This document describes the full AiSci platform: how Onyx, DeerFlow, LiteLLM, MCP, and the model providers fit together.

For operational status and open work, see Multica Issues. For deployment shape and commands, see `docs/ops/deployment-reference.md`.

---

## System Map

```
┌─────────────────────────────────────────────────────────────────────┐
│  User / Agent                                                        │
│  Browser → http://localhost:3000 (Onyx)                             │
│  Browser → http://localhost:2026 (DeerFlow)                         │
└────────────────┬────────────────────────────────────────────────────┘
                 │
    ┌────────────▼────────────┐      ┌──────────────────────────────┐
    │  Onyx Stack             │      │  DeerFlow Stack              │
    │  (deployment/onyx/)     │      │  (deployment/deer-flow/)     │
    │                         │      │                              │
    │  onyx-nginx :80/:3000   │      │  deer-flow-nginx :2026       │
    │  onyx-web-server        │      │  deer-flow-frontend :3000    │
    │  onyx-api-server :8080  │◄─────│  deer-flow-gateway :8001     │
    │  onyx-background        │      │  (LangGraph runtime)         │
    │  onyx-mcp-server :3000  │      └──────────────┬───────────────┘
    │  onyx-mcp-proxy :80     │◄────────────────────┘
    │    (127.0.0.1:8095)     │      DeerFlow reaches MCP internally
    └────────────┬────────────┘      via http://onyx-mcp-proxy:80/
                 │                   on the shared onyx_default network
    ┌────────────▼────────────┐
    │  Storage & Search       │
    │  onyx-opensearch :9200  │  Dense vector retrieval (Alibaba/1536)
    │  onyx-db (Postgres) :5432│  Document metadata, personas, connectors
    │  onyx-redis :6379       │  Celery task queue
    │  onyx-minio :9000       │  File store (S3-compatible)
    └────────────┬────────────┘
                 │
    ┌────────────▼────────────┐
    │  LiteLLM Proxy          │
    │  onyx-litellm :4001     │  Routes to DashScope, NVIDIA, Ollama
    │  (127.0.0.1:4001)       │
    └────────────┬────────────┘
                 │
    ┌────────────▼────────────────────────────────────────────────────┐
    │  Model Providers                                                 │
    │  DashScope (Singapore)  qwen3.5-omni-flash, qwen3.5-omni-plus  │
    │  NVIDIA NIM             llama-3.3-70b, nemotron-super-49b       │
    │  OpenRouter             gemini-2.5-flash, claude-4.7-opus       │
    │  Ollama (local)         gemma2:27b, qwen2.5vl:7b (fallback)    │
    └─────────────────────────────────────────────────────────────────┘
```

---

## Onyx

**Role:** Private RAG platform. Indexes documents, serves search, hosts personas (AI assistants with scoped document sets).

**Key components:**

| Container | Role |
|---|---|
| `onyx-api-server` | REST API, chat, search, connector management |
| `onyx-background` | Celery workers — indexing, connector sync, contextual summaries |
| `onyx-web-server` | Next.js frontend |
| `onyx-indexing-model-server` | Embedding generation during indexing |
| `onyx-inference-model-server` | Embedding generation during search |
| `onyx-opensearch` | Vector + keyword search index |
| `onyx-litellm` | LLM proxy for RAG generation and contextual summaries |
| `onyx-mcp-server` | MCP server exposing Onyx search as an MCP tool |
| `onyx-mcp-proxy` | nginx proxy routing MCP calls to Scite, Consensus, and Onyx |

**Embedding model:** `Alibaba-NLP/gte-Qwen2-1.5B-instruct` (1536 dims). Active index: `danswer_chunk_alibaba_nlp_gte_qwen2_1_5b_instruct`.

**Personas:** Physics-validator (id=2), Evidence-auditor (id=5), Referee-prep (id=6), arXiv-intake (id=3). See `docs/ops/onyx-persona-ids.md`.

---

## DeerFlow

**Role:** Multi-agent orchestration. LangGraph-based lead agent with subagents, sandbox execution, MCP tools, and skills.

**Key components:**

| Container | Role |
|---|---|
| `deer-flow-gateway` | FastAPI + LangGraph runtime, REST API on :8001 |
| `deer-flow-frontend` | Next.js chat UI on :3000 |
| `deer-flow-nginx` | Reverse proxy, exposes :2026 to host |

**Networks:** `deer-flow-gateway` is attached to both `deer-flow-dev_deer-flow-dev` and `onyx_default`. This is what allows it to reach `onyx-mcp-proxy` and `onyx-api-server` by container name.

**Config:** `deployment/deer-flow/config.yaml` (gitignored). See `deployment/deer-flow/README-local-patches.md` for required local patches.

---

## Onyx–DeerFlow Bridge

DeerFlow agents access Onyx knowledge via two paths:

1. **MCP (primary):** `deer-flow-gateway` → `http://onyx-mcp-proxy:80/onyx/` → `onyx-mcp-server` → `onyx-api-server`. Configured in `deployment/deer-flow/extensions_config.json` (gitignored; see `extensions_config.example.json`).

2. **Direct REST (secondary):** `deerflow.community.onyx.tools:onyx_search_tool` calls `onyx-api-server:8080` directly using `ONYX_API_KEY`. Configured in `deployment/deer-flow/config.yaml` under `tools`.

**Renaming any container or network requires updating both `extensions_config.json` and `config.yaml`.**

---

## MCP Proxy

`onyx-mcp-proxy` is an nginx container that routes MCP protocol calls:

| Path | Upstream | Auth |
|---|---|---|
| `/onyx/` | `onyx-mcp-server:3000` | `MCP_PROXY_AUTH_TOKEN` |
| `/scite/` | `https://api.scite.ai/mcp` | OAuth Bearer (client-supplied) |
| `/consensus/` | `https://mcp.consensus.app/mcp/` | OAuth Bearer (client-supplied) |

Host binding: `127.0.0.1:8095`. Internal Docker binding: `:80` on `onyx_default`.

Scite and Consensus OAuth tokens must be completed manually and stored in `.env.local` (not `/tmp/`). See Multica Issues — "Scite and Consensus OAuth never completed".

---

## LiteLLM

Routes all LLM calls for both Onyx and DeerFlow. Config: `deployment/onyx/onyx-litellm_config.yaml`.

**Active model tiers (Onyx):**

| Alias | Model | Provider |
|---|---|---|
| `qwen-fast` | qwen3.5-omni-flash | DashScope SG |
| `qwen-balanced` | qwen3.5-omni-flash | DashScope SG |
| `qwen-max` | qwen3.5-omni-plus | DashScope SG |
| `nvidia-balanced` | llama-3.3-70b-instruct | NVIDIA NIM |
| `local-chat` | qwen2.5:latest | Ollama |

**DeerFlow** uses its own model list in `config.yaml` pointing at OpenRouter and NVIDIA directly (not via LiteLLM).

---

## Data Flow: RAG Query

```
User message
  → Onyx chat API
  → Query rephrasing (qwen-balanced via LiteLLM)
  → OpenSearch KNN search (Alibaba/1536 embeddings)
  → Top-k chunks retrieved
  → LLM generation with context (qwen-balanced)
  → Streamed response to UI
```

---

## Key Files

| File | Purpose |
|---|---|
| `deployment/onyx/docker-compose.yml` | Onyx stack definition |
| `deployment/onyx/.env` | Tracked defaults (no live secrets) |
| `deployment/onyx/onyx-litellm_config.yaml` | LiteLLM model routing |
| `deployment/onyx/monitoring/check_health.sh` | Runtime health checks |
| `deployment/onyx/preflight_check.sh` | Pre-reindex safety gate |
| `deployment/deer-flow/config.yaml` | DeerFlow agent config (gitignored) |
| `deployment/deer-flow/README-local-patches.md` | Required local patches |
| `deployment/deer-flow/apply_local_patches.sh` | Patch verification script |
| `deployment/helper/onyx_opensearch_cutover.py` | OpenSearch parity gate |
| `docs/ops/deployment-reference.md` | Live service URLs and layout |
| Multica Issues | Active tasks and operational work |
| `docs/ops/troubleshooting.md` | Known failure modes and fixes |

---

## Related Docs

- `docs/ops/deployment-reference.md` — live service URLs, repo layout, operational commands
- `docs/ops/troubleshooting.md` — failure mode runbook
- `docs/decisions/2026-04-27-mcp-topology.md` — MCP routing decisions
- `docs/ops/onyx-rag-optimization-2026-04-27.md` — OpenSearch retrieval stack details
