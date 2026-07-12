# AiSci Action Plan

This is a high-level milestone tracker. The operational source of truth is
[`docs/ops/platform-backlog.md`](docs/ops/platform-backlog.md). Scientific work
belongs in the registered project workspace.

## Canonical links

- Project registry: [`research/projects.toml`](research/projects.toml)
- Platform operations: [`docs/ops/platform-backlog.md`](docs/ops/platform-backlog.md)
- Current architecture: [`docs/ops/architecture-overview.md`](docs/ops/architecture-overview.md)
- Deployment reference: [`docs/ops/deployment-reference.md`](docs/ops/deployment-reference.md)
- Robert science queue: [`research/robert/next-actions.md`](research/robert/next-actions.md)
- Robert evidence ledger: [`research/robert/evidence-ledger.md`](research/robert/evidence-ledger.md)
- Durable decisions: [`docs/decisions/`](docs/decisions/)

## Milestones

| Milestone | Status | Current pointer |
|---|---|---|
| Initial project-based control plane | Implemented | One registered Robert project, project-scoped API/UI, and local job records |
| Control-plane reality documentation | Implemented | `docs/ops/architecture-overview.md` and related current runbooks |
| Second real project onboarding | Planned | Validate a PhD audit or equivalent through the project registry |
| Durable multi-worker job execution | Planned | See `docs/ops/platform-backlog.md` |
| Science validation readiness | In progress | `research/robert/next-actions.md`, `fit-plan.md`, and evidence ledger |

## Decision status

- `2026-04-26-system-boundaries.md`: active boundary between repository science
  canon, implementation surfaces, and external execution adapters.
- `2026-04-26-science-evidence-standards.md`: active evidence and
  claim-promotion rules.
- Earlier Onyx/DeerFlow/MCP decisions remain historical records; they do not
  describe an active deployment in the current checkout.
