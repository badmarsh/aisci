# AiSci Action Plan

This file is a milestone tracker only. The operational source of truth is [docs/ops/platform-backlog.md](docs/ops/platform-backlog.md). The science task queue is [research/robert/next-actions.md](research/robert/next-actions.md). The science claim-status canon is [research/robert/evidence-ledger.md](research/robert/evidence-ledger.md). `docs/archive/` is preserved as historical-only context.

## Canonical Links

- Platform operations: [docs/ops/platform-backlog.md](docs/ops/platform-backlog.md)
- Deployment reference: [docs/ops/deployment-reference.md](docs/ops/deployment-reference.md)
- Critical component map: [docs/ops/critical-components.md](docs/ops/critical-components.md)
- Science queue: [research/robert/next-actions.md](research/robert/next-actions.md)
- Science evidence ledger: [research/robert/evidence-ledger.md](research/robert/evidence-ledger.md)
- Durable decisions: [docs/decisions/](docs/decisions/)

## Milestones

| Milestone | Status | Current Pointer |
|---|---|---|
| Infrastructure stabilization | In progress | See `docs/ops/platform-backlog.md` for Onyx, DeerFlow, Docker, MCP, and deployment tasks |
| Retrieval-stack completion | Alibaba/OpenSearch parity green; retrieval eval next | See `docs/ops/platform-backlog.md` and `docs/ops/onyx-rag-optimization-2026-04-27.md` |
| MCP research-tool auth | Pending OAuth client flow and smoke tests | See `docs/ops/platform-backlog.md` |
| DeerFlow de-vendoring | Pending verification and structural migration decision | See `docs/ops/platform-backlog.md` |
| Science validation readiness | In progress | See `research/robert/next-actions.md`, `research/robert/fit-plan.md`, and `research/robert/evidence-ledger.md` |

## Decision Status

- `2026-04-26-parser-and-rag-choice.md`: active baseline for local Unstructured; updated with the current Alibaba/1536 OpenSearch retrieval direction
- `2026-04-27-mcp-topology.md`: active MCP topology decision for shared local proxy and project-level config
- `2026-04-26-system-boundaries.md`: active boundary between science canon, ops docs, and implementation surfaces
- `2026-04-26-science-evidence-standards.md`: active evidence and claim-promotion rules
