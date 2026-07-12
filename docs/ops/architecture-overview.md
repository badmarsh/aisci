# AiSci Control-Plane Architecture

_Last verified against the repository and local listeners: 2026-07-12._

AiSci is a project-based research control plane. The dashboard monitors
repository-backed research projects and requests registered work; it does not
own scientific truth or replace the reproducible code and artifacts in the
repository.

The active frontend is a Vite/TanStack Start React application, not a Next.js
application. The active deployment directory contains no Docker Compose file,
Onyx stack, DeerFlow stack, LiteLLM proxy, MCP proxy, or model-provider stack.
Those integrations are historical records only and are not part of the current
runtime.

## System map

```
Browser
  │  http://localhost:5173
  ▼
AiSci Dashboard
  Vite + TanStack Start + React
  deployment/aisci-dashboard/src/
  │  project-scoped API requests
  ▼
Ignition Control API
  FastAPI
  deployment/aisci-dashboard/ignition/
  │
  ├── Project registry ────── research/projects.toml
  │       │
  │       └── ProjectSpec ─── research/robert/ (current registered project)
  │              ├── canonical Markdown
  │              ├── inputs and manuscript material
  │              └── dated run artifacts
  │
  ├── Operational read model / job records
  │       └── deployment/aisci-dashboard/data/evidence_graph.db
  │           (SQLite; WAL, foreign keys, and busy timeout configured)
  │
  └── Registered pipeline requests
          └── project run directory and, when validly configured,
              libs/physics-core/.venv + reusable physics code
```

The local development launcher is [`start_dashboard.sh`](../../start_dashboard.sh).
It starts the frontend on port `5173` and the API on port `8001`; it also stops
existing listeners on those ports before starting replacements.

## Responsibilities and boundaries

| Layer | Responsibility | Source of truth |
|---|---|---|
| Dashboard | Portfolio/project navigation, monitoring, review-request UI, and job controls | API responses; never a scientific authority |
| Ignition | Project-scoped API, projections of canonical files, job/activity records, and pipeline dispatch | Code in `deployment/aisci-dashboard/ignition/` |
| Project workspace | Evidence, task queue, sources, inputs, reports, and reproducible runs | Files under the registered project root |
| Physics core | Reusable model, fit, validation, and data utilities | `libs/physics-core/` |
| Historical integrations | Prior Onyx, DeerFlow, LiteLLM, MCP, and RAG records | Historical documentation and git history only |

Scientific claims remain governed by the evidence-ledger policy. A successful
job or fit is not, by itself, a scientific conclusion. See
[`docs/decisions/2026-04-26-science-evidence-standards.md`](../decisions/2026-04-26-science-evidence-standards.md).

## Projects

[`research/projects.toml`](../../research/projects.toml) is the current
registry. Each `ProjectSpec` supplies an ID, metadata, root directory,
sensitivity, and enabled capabilities. The presently registered project is:

| ID | Root | Type | Enabled capabilities |
|---|---|---|---|
| `robert-boson-manuscript` | `research/robert/` | manuscript validation | evidence, tasks, literature, symbolic validation, fit validation, reports |

The registry permits a future project—such as a PhD audit—to use a different
workspace and capability set. A project with no fitting capability must not be
shown fitting controls merely because Robert's project has them.

## Data flow

### Queries

1. The browser selects a project.
2. The dashboard requests `/api/projects/{project_id}/…` endpoints.
3. Ignition resolves the project through the registry and reads canonical
   Markdown/run artifacts or the project-scoped SQLite projection.
4. The API returns an explicit project-scoped result, empty state, or error.

### Review requests

The dashboard creates a project-scoped review decision rather than directly
rewriting the evidence ledger or task queue. Controlled materialization and
sync endpoints are separately authenticated when `AISCI_DASHBOARD_TOKEN` is
configured. Canonical Markdown remains authoritative.

### Pipeline requests

Ignition records a `JobExecutions` row and starts a registered pipeline command
as an asynchronous child process. Job logs are written under the project run
directory and can be streamed by project and pipeline ID.

This is an initial local control-plane implementation, not a distributed queue:
job execution is owned by the FastAPI process and operational state is SQLite.
It must not be documented as Celery-, Redis-, Docker-, or PostgreSQL-backed.

## Current limitations

- The registry contains only Robert's project; adding a real second project is
  the next proof that project isolation works end-to-end.
- `ignition/pipelines.py` currently contains two hardcoded Robert pipeline
  definitions. Their commands must be verified and moved into project
  configuration before they can be described as a generic pipeline catalogue.
- The API token check is optional when `AISCI_DASHBOARD_TOKEN` is unset; this
  is a local-development posture, not a complete access-control system.
- The SQLite database is suitable for the current local process model. A
  multi-worker/deployed control plane needs a durable worker and database
  design before claiming concurrent-agent scalability.

## Key files

| File | Purpose |
|---|---|
| `research/projects.toml` | Registered project metadata and roots |
| `deployment/aisci-dashboard/ignition/project_registry.py` | `ProjectSpec` loading and path resolution |
| `deployment/aisci-dashboard/ignition/api.py` | Project-scoped control API |
| `deployment/aisci-dashboard/ignition/pipelines.py` | Current pipeline registry implementation |
| `deployment/aisci-dashboard/ignition/database.py` | SQLite read model, activity, review, and job tables |
| `libs/physics-core/` | Reusable physics and fitting implementation |
| `research/robert/` | Current project science canon and dated runs |

## Related documents

- [`deployment-reference.md`](deployment-reference.md) — active local service
  shape and startup instructions.
- [`CURRENT_STATUS.md`](CURRENT_STATUS.md) — verified operational snapshot and
  current limitations.
- [`platform-backlog.md`](platform-backlog.md) — active operational work.
- [`critical-components.md`](critical-components.md) — current component map.
- [`docs/decisions/`](../decisions/) — durable decisions; historical decisions
  are retained without implying that their old deployments remain active.
