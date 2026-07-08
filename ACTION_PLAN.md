# AiSci Action Plan

This file is a milestone tracker only. The operational source of truth for tasks is the Multica Issue board (`multica issue list`). Concise platform state lives in [docs/ops/platform-status.md](docs/ops/platform-status.md). The science task queue is [research/robert/next-actions.md](research/robert/next-actions.md). The science claim-status canon is [research/robert/evidence-ledger.md](research/robert/evidence-ledger.md). `docs/archive/` is preserved as historical-only context.

## Canonical Links

- Platform tasks: Multica Issue board (`multica issue list`)
- Platform state: [docs/ops/platform-status.md](docs/ops/platform-status.md)
- Deployment reference: [docs/ops/deployment-reference.md](docs/ops/deployment-reference.md)
- Critical component map: [docs/ops/critical-components.md](docs/ops/critical-components.md)
- Science queue: [research/robert/next-actions.md](research/robert/next-actions.md)
- Science evidence ledger: [research/robert/evidence-ledger.md](research/robert/evidence-ledger.md)
- Durable decisions: [docs/decisions/](docs/decisions/)

## Milestones

| Milestone | Status | Current Pointer |
|---|---|---|
| Infrastructure stabilization | In progress | Multica Issues (infra squad) and `docs/ops/platform-status.md` |
| Retrieval-stack completion | Alibaba/OpenSearch parity green; retrieval eval next | Multica Issues and `docs/ops/onyx-rag-optimization-2026-04-27.md` |
| MCP research-tool auth | Done | Multica Issues (closed) |
| DeerFlow de-vendoring | Pending verification and structural migration decision | Multica Issues |
| Science validation readiness | In progress | See `research/robert/next-actions.md`, `research/robert/fit-plan.md`, and `research/robert/evidence-ledger.md` |

## Decision Status

- `2026-04-26-parser-and-rag-choice.md`: active baseline for local Unstructured; updated with the current Alibaba/1536 OpenSearch retrieval direction
- `2026-04-27-mcp-topology.md`: active MCP topology decision for shared local proxy and project-level config
- `2026-04-26-system-boundaries.md`: active boundary between science canon, ops docs, and implementation surfaces
- `2026-04-26-science-evidence-standards.md`: active evidence and claim-promotion rules
