# Ops Documentation Index

Operational documentation for the active AiSci control plane. Scientific
claims and fit conclusions belong in the relevant project workspace.

## Documentation Index

| File | Tag | Description |
|---|---|---|
| [`CURRENT_STATUS.md`](CURRENT_STATUS.md) | [active] | Current verified state of the platform. |
| [`README.md`](README.md) | [active] | This index file. |
| [`activepieces-integration.md`](activepieces-integration.md) | [historical] | Legacy ActivePieces integration notes. |
| [`architecture-overview.md`](architecture-overview.md) | [active] | Architecture and boundaries. |
| [`critical-components.md`](critical-components.md) | [active] | Component map and system overview. |
| [`deployment-reference.md`](deployment-reference.md) | [active] | Active local startup/deployment guide. |
| [`k-dense-skills-reference.md`](k-dense-skills-reference.md) | [historical] | Legacy K-dense skills reference. |
| [`kdense-agent-skills.md`](kdense-agent-skills.md) | [historical] | Legacy K-dense agent skills guide. |
| [`literature-corpus-policy.md`](literature-corpus-policy.md) | [historical] | Legacy literature corpus policy. |
| [`manuscript-verification-narrative.md`](manuscript-verification-narrative.md) | [active] | Narrative of Robert's manuscript verification. |
| [`mcp-endpoints.md`](mcp-endpoints.md) | [historical] | Legacy MCP endpoints reference. |
| [`mcp-hep-servers.md`](mcp-hep-servers.md) | [historical] | Legacy MCP HEP servers configuration. |
| [`model-optimization-report.md`](model-optimization-report.md) | [historical] | Legacy model optimization report. |
| [`model-selection-guide.md`](model-selection-guide.md) | [historical] | Legacy model selection guide. |
| [`platform-backlog.md`](platform-backlog.md) | [active] | Operational work and backlog. |
| [`platform-status.md`](platform-status.md) | [active] | High-level platform status. |
| [`rag-evaluation-results.md`](rag-evaluation-results.md) | [historical] | Legacy RAG evaluation results. |
| [`rag-evaluation-set.md`](rag-evaluation-set.md) | [historical] | Legacy RAG evaluation set definitions. |
| [`secrets-and-deployment-notes.template.md`](secrets-and-deployment-notes.template.md) | [active] | Template for secrets and deployment notes. |
| [`semantic-scholar-asta-api.md`](semantic-scholar-asta-api.md) | [historical] | Legacy Semantic Scholar API notes. |
| [`subtree-management.md`](subtree-management.md) | [historical] | Legacy subtree management operations. |
| [`troubleshooting.md`](troubleshooting.md) | [active] | Current failure modes and troubleshooting. |

## Active platform scope

The active platform consists of the Vite/TanStack Start dashboard, the FastAPI
Ignition control API, a project registry, project workspaces, SQLite local
operational state, and the shared physics-core environment. There is no active
Onyx, DeerFlow, LiteLLM, OpenSearch, Celery, MCP proxy, or Docker Compose stack
in the current checkout.

## Historical records

Files whose names refer to `onyx`, `rag`, `mcp`, `deerflow`, or prior model
routing preserve historical context only. They are not current architecture,
deployment, status, or troubleshooting references. In particular,
[`mcp-endpoints.md`](mcp-endpoints.md) now records that no MCP proxy is active.

When current and historical documents disagree, the current sources table
above wins.

## Conventions

- Keep secrets out of tracked documentation.
- Keep current operational work concise in `platform-backlog.md`; use Issues
  and PRs as the execution history.
- Keep project science state under `research/<project>/`.
- Date historical records and do not represent absent services as operational.
