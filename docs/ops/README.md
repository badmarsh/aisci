# Ops Documentation Index

Operational documentation for the active AiSci control plane. Scientific
claims and fit conclusions belong in the relevant project workspace.

## Current sources

| Topic | Canonical file |
|---|---|
| Architecture and boundaries | [`architecture-overview.md`](architecture-overview.md) |
| Current verified state | [`CURRENT_STATUS.md`](CURRENT_STATUS.md) |
| Active local startup/deployment | [`deployment-reference.md`](deployment-reference.md) |
| Operational work | [`platform-backlog.md`](platform-backlog.md) |
| Component map | [`critical-components.md`](critical-components.md) |
| Current failure modes | [`troubleshooting.md`](troubleshooting.md) |

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
