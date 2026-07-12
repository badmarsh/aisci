# Platform Status

_Last verified: 2026-07-12._

## Current platform

AiSci currently runs as a local project-based research control plane:

- Vite/TanStack Start dashboard on port `5173`.
- FastAPI Ignition API on port `8001`.
- One registered project: `robert-boson-manuscript`.
- SQLite operational read model/job store under
  `deployment/aisci-dashboard/data/`.
- Shared physics implementation and environment under `libs/physics-core/`.

The current status of scientific claims is not represented here. Consult the
registered project's evidence ledger and task queue.

## Operational constraints

- The current runner is local to the FastAPI process; it is not a distributed
  queue or a container orchestration service.
- Project pipeline definitions require executable validation before use.
- Mutating API endpoints rely on `AISCI_DASHBOARD_TOKEN` only when it is set.
- Runtime databases, logs, build output, virtual environments, and test output
  are not source-controlled platform state.

## Absent legacy services

No current deployment for Onyx, DeerFlow, LiteLLM, MCP proxy, OpenSearch,
Celery, or model-provider routing exists in this checkout. Previous status
claims for those services are historical and must not be used operationally.

For current work, see [`platform-backlog.md`](platform-backlog.md). For local
startup, see [`deployment-reference.md`](deployment-reference.md).
