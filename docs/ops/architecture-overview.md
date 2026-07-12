# Architecture Overview

This document describes the full AiSci platform: how Onyx, DeerFlow, LiteLLM, MCP, and the model providers fit together.

For operational status and open work, see GitHub Issues. For deployment shape and commands, see `docs/ops/deployment-reference.md`.

---

## System Map

```
┌─────────────────────────────────────────────────────────────────────┐
│  User / Agent                                                        │
│  Browser → http://localhost:3000 (Onyx)                             │
│  Browser → http://localhost:5173 (AiSci Dashboard)                  │
└────────────────┬────────────────────────────────────────────────────┘
                 │
    ┌────────────▼────────────┐      ┌──────────────────────────────┐
    │  Onyx Stack             │      │  AiSci Core                  │
    │  (deployment/onyx/)     │      │                              │
    │                         │      │  AiSci Dashboard :5173       │
    │  onyx-nginx :80/:3000   │      │  Ignition Engine :8001       │
    │  onyx-web-server        │◄─────│  (FastAPI + Physics)         │
    │  onyx-api-server :8080  │      │                              │
    │  onyx-background        │      └──────────────┬───────────────┘
    │  onyx-mcp-server :3000  │      AiSci reaches MCP via
    │  onyx-mcp-proxy :80     │◄──── 127.0.0.1:8095
    │    (127.0.0.1:8095)     │      
    └────────────┬────────────┘      
                 │                   
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

## AiSci Core & Ignition Engine

The AiSci Ignition Engine (FastAPI) acts as the bridge between the Dashboard and the underlying physics core. It relies on a CQRS (Command Query Responsibility Segregation) and background task architecture to execute heavy operations.

- **Queries (Reads)**: Endpoints fetch data directly from canonical research files (e.g., `research/robert/evidence-ledger.md`, `next-actions.md`) or the SQLite database. Path resolution maps accurately to the `research/robert/` namespace.
- **Commands & Tasks (Writes)**: Modifying operations and long-running jobs (like executing fits or validating hypotheses) are strictly dispatched as safe `asyncio`-based background tasks rather than blocking `subprocess.Popen` calls.
- **State tracking**: Background tasks provide status and log outputs seamlessly to the React frontend without tying up FastAPI worker threads.

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

## MCP Proxy

`onyx-mcp-proxy` is an nginx container that routes MCP protocol calls:

| Path | Upstream | Auth |
|---|---|---|
| `/onyx/` | `onyx-mcp-server:3000` | `MCP_PROXY_AUTH_TOKEN` |
| `/scite/` | `https://api.scite.ai/mcp` | OAuth Bearer (client-supplied) |
| `/consensus/` | `https://mcp.consensus.app/mcp/` | OAuth Bearer (client-supplied) |

Host binding: `127.0.0.1:8095`. Internal Docker binding: `:80` on `onyx_default`.

Scite and Consensus OAuth tokens must be completed manually and stored in `.env.local` (not `/tmp/`). See GitHub Issues — "Scite and Consensus OAuth never completed".

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

| `deployment/helper/onyx_opensearch_cutover.py` | OpenSearch parity gate |
| `docs/ops/deployment-reference.md` | Live service URLs and layout |
| GitHub Issues | Active tasks and operational work |
| `docs/ops/troubleshooting.md` | Known failure modes and fixes |

---

## Related Docs

- `docs/ops/deployment-reference.md` — live service URLs, repo layout, operational commands
- `docs/ops/troubleshooting.md` — failure mode runbook
- `docs/decisions/2026-04-27-mcp-topology.md` — MCP routing decisions
- `docs/ops/onyx-rag-optimization-2026-04-27.md` — OpenSearch retrieval stack details
