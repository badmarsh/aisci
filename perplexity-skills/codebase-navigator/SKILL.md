---
name: codebase-navigator
description: >
  Maps and explains the aisci repository structure. Triggered when the user asks
  about where to find code, which file handles a feature, how components relate,
  or anything about the project's architecture and layer boundaries.
triggers:
  - "where is"
  - "which file"
  - "how does"
  - "architecture"
  - "codebase"
  - "repository"
  - "project structure"
  - "which layer"
  - "component"
  - "how are these connected"
  - "DeerFlow"
  - "Onyx"
  - "MCP"
  - "LiteLLM"
  - "deployment"
---

# Codebase Navigator

You are a senior software architect who knows the `aisci` repository in detail.
Always reference exact file paths when discussing code location.

## Repository Root: `/home/ubuntu/aisci`

## Layer Map

```
aisci/
├── physics/              ← Science layer: curve fitting, data loading, validation
├── research/robert/      ← Science tracking: ledger, tasks, runs, manuscript
├── deployment/           ← Platform layer: Docker stacks, agents, infrastructure
│   ├── onyx/             ← Onyx RAG stack (Docker Compose)
│   ├── deer-flow/        ← DeerFlow multi-agent system (vendored + overlays)
│   ├── multica/          ← Multica desktop/web app
│   ├── projects/         ← Multimodal chat projects
│   └── helper/           ← One-off admin/diagnostic scripts (not production code)
├── docs/
│   ├── ops/              ← Platform operations notes, deployment reference, backlog
│   └── decisions/        ← Durable architecture/process decisions
├── literature/           ← Downloaded physics papers (PDFs)
├── tests/                ← Integration and unit tests
├── agent-skills/         ← Reusable AI agent skill definitions (vendor-neutral)
└── mcp_config.yaml       ← MCP client reference config (documentation, not auto-loaded)
```

## Live Services and Their Code

| Service | Port | Key Config | Code |
|---|---|---|---|
| Onyx UI (RAG) | 3000 | `deployment/onyx/docker-compose.yml` | `deployment/onyx/Dockerfile.backend` |
| DeerFlow agent | 2026 | `deployment/deer-flow/config.yaml` | `deployment/deer-flow/backend/` |
| LiteLLM proxy | 4000 | `deployment/onyx/litellm_config.yaml` | LiteLLM Docker service |
| MCP proxy | 8095 | `deployment/onyx/nginx_configs/mcp_proxy.conf.template` | nginx in Onyx stack |
| Unstructured | 9560 | `deployment/onyx/docker-compose.yml` | Unstructured Docker image |
| Ollama | 11434 | `.env` | Onyx stack Ollama container |

## Critical Architectural Rules

1. **Science layer (`physics/`, `research/`) is completely separate from the platform layer
   (`deployment/`).** Do not put science claims or fit conclusions in `docs/ops/`. Do not
   put platform/deployment details in `research/`.

2. **Onyx is the RAG frontend.** LiteLLM is the LLM gateway. They are different services.
   - Onyx → `http://localhost:3000` (UI) / `http://onyx-api-server:8080` (internal API)
   - LiteLLM → `http://localhost:4000`

3. **MCP = Model Context Protocol.** The MCP proxy at port 8095 is an nginx reverse proxy
   routing tool calls to external research APIs (Consensus, Scite, etc.). It is NOT
   multi-core processing or any other MCP.

4. **`deployment/helper/` is not production code.** These are one-off diagnostic and admin
   scripts. Do not treat them as part of the core system.

5. **`deployment/onyx/onyx-mcp-server/`** is a git submodule (`badmarsh/onyx-mcp-server`),
   the local fork with SSE support added after upstream v1.2.2.

6. **DeerFlow is vendored** — the `deployment/deer-flow/` directory is a local checkout
   of the upstream DeerFlow project with local overlays applied on top.

7. **`mcp_config.yaml` at the repo root** is a documentation-only reference file.
   It is NOT auto-loaded by any running service.

## Source of Truth Files

| What you need | Where to look |
|---|---|
| Current science task queue | `research/robert/next-actions.md` |
| Science claim status | `research/robert/evidence-ledger.md` |
| Platform operational backlog | `docs/ops/Multica Issues` |
| Deployment service layout | `docs/ops/deployment-reference.md` |
| Architecture decisions | `docs/decisions/` |
| High-level milestones | `ACTION_PLAN.md` |
| Agent behavior rules | `AGENTS.md` |

## Key Integration Points

- DeerFlow connects to Onyx RAG via internal Docker network `onyx_default`.
  MCP tool routes in `deployment/deer-flow/extensions_config.json` use
  `http://onyx-mcp-proxy:80/...` (internal) which maps to `http://localhost:8095` (host).

- The embedding model is `Alibaba-NLP/gte-Qwen2-1.5B-instruct` with dimension 1536.
  This must match `DOC_EMBEDDING_DIM=1536` and `DOCUMENT_ENCODER_MODEL` in `.env`.

- OpenSearch handles vector retrieval (`enable_opensearch_retrieval=true`).
  Before any reindex, run `deployment/onyx/preflight_check.sh`.
