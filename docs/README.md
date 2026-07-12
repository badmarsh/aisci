# AiSci Documentation Map

This folder holds project-wide documentation. Scientific claims, validation
criteria, and reproducible runs belong in the relevant `research/` project
workspace, not in operational documents.

## Current documentation

- `ops/` — current control-plane architecture, local deployment reference,
  runbook, component map, and platform backlog.
- `decisions/` — durable architecture and process decisions. Older decisions
  remain historical records and do not imply their former services are active.
- `archive/` — historical-only material.

## Current platform

The active local platform is the AiSci Dashboard (Vite/TanStack Start) and
Ignition (FastAPI), operating against registered repository projects. Start
with:

- [`ops/architecture-overview.md`](ops/architecture-overview.md)
- [`ops/deployment-reference.md`](ops/deployment-reference.md)
- [`ops/CURRENT_STATUS.md`](ops/CURRENT_STATUS.md)
- [`ops/platform-backlog.md`](ops/platform-backlog.md)

The project registry is [`../research/projects.toml`](../research/projects.toml).
Robert's current science workspace is [`../research/robert/`](../research/robert/).

## Historical integration material

Some dated files retain records of prior Onyx, DeerFlow, LiteLLM, MCP, and RAG
work. Those services are not present in the current `deployment/` tree. Treat
such files as historical context unless a current document explicitly restores
an integration.

## Work tracking

Use GitHub Issues and Pull Requests for accepted implementation/review work.
Keep durable facts in the appropriate canonical location:

- platform state and active runbooks: `docs/ops/`
- durable decisions: `docs/decisions/`
- project science evidence and tasks: `research/<project>/`

Do not create new backlog/status files by default.
