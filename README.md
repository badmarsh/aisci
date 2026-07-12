# AiSci Research Workspace

AiSci is a repository-based, project-oriented research control plane. It
combines a dashboard, a FastAPI control API, reusable physics code, and durable
project workspaces. The dashboard monitors and requests registered work; the
repository remains the source of reproducible science.

## Current registered project

| Project | Purpose | Canonical workspace |
|---|---|---|
| Robert — Boson probability function for the moving system | Manuscript validation against equations, data behavior, fitting stability, and HEP phenomenology literature | [`research/robert/`](research/robert/) |

Project registration lives in [`research/projects.toml`](research/projects.toml).
Future work, including a PhD audit, should be added as a separate project with
its own canonical files, inputs, runs, and enabled capabilities—not as a new
Robert-specific dashboard branch.

## Active control plane

```text
Browser → AiSci Dashboard (:5173) → Ignition API (:8001)
                                  ├─ project registry
                                  ├─ project Markdown/read-model data
                                  └─ registered pipeline requests
                                          → libs/physics-core/.venv
```

The active dashboard is a Vite/TanStack Start React application in
`deployment/aisci-dashboard/`; Ignition is its FastAPI backend in
`deployment/aisci-dashboard/ignition/`.

There is no active Onyx, DeerFlow, LiteLLM, MCP proxy, OpenSearch, Celery, or
Docker Compose deployment in this checkout. Historical integration documents
are retained for context and are not current operating instructions.

## Workspace navigation

- [`research/projects.toml`](research/projects.toml) — registered research
  projects and their capability boundaries.
- [`research/robert/`](research/robert/) — Robert's science canon, manuscript,
  evidence ledger, task queue, and dated runs.
- [`libs/physics-core/`](libs/physics-core/) — reusable model, fitting, data,
  and validation code plus its isolated Python environment.
- [`deployment/aisci-dashboard/`](deployment/aisci-dashboard/) — active UI and
  Ignition control API.
- [`docs/ops/architecture-overview.md`](docs/ops/architecture-overview.md) —
  current system shape and constraints.
- [`docs/decisions/`](docs/decisions/) — durable historical and active
  architecture/process decisions.

## Local startup

```bash
bash start_dashboard.sh
```

This starts the dashboard on `http://localhost:5173` and Ignition on
`http://localhost:8001`. It stops existing listeners on those ports first.

## Research rules

Scientific claim status belongs in each project's evidence ledger. Local
scripts and completed jobs are sanity checks unless their assumptions, inputs,
artifacts, fit diagnostics, and literature context satisfy the evidence policy.
For Robert, use:

- [`research/robert/evidence-ledger.md`](research/robert/evidence-ledger.md)
- [`research/robert/next-actions.md`](research/robert/next-actions.md)
- [`research/robert/workflow.md`](research/robert/workflow.md)
