# Current System Status

**Last verified:** 2026-07-12  
**Maintainer:** Platform Operations

This is a repository-and-listener snapshot. Durable open work belongs in
[`platform-backlog.md`](platform-backlog.md); scientific status belongs in the
registered project's evidence ledger and task queue.

## Verified local runtime

| Component | Observed state | Location / URL |
|---|---|---|
| AiSci Dashboard | Listening locally | `http://localhost:5173` |
| Ignition API | Listening locally | `http://localhost:8001` |
| Frontend implementation | Vite + TanStack Start + React | `deployment/aisci-dashboard/` |
| Backend implementation | FastAPI | `deployment/aisci-dashboard/ignition/` |
| Project registry | One registered project | `research/projects.toml` |
| Shared physics environment | Present in repository | `libs/physics-core/.venv` |

No Docker Compose file was found under `deployment/`. No `deployment/onyx/`
or `deployment/deer-flow/` directory is present. Onyx, DeerFlow, LiteLLM,
OpenSearch, Celery, MCP proxy, and model-provider services are therefore not
current local deployment components.

## Control-plane state

The current registry contains `robert-boson-manuscript`, rooted at
`research/robert/`. The dashboard and API use project-scoped paths such as:

```text
/api/projects/{project_id}/evidence
/api/projects/{project_id}/tasks
/api/projects/{project_id}/fits
/api/projects/{project_id}/activity
```

Ignition stores projections, activity, review decisions, and job records in
the dashboard SQLite database. Canonical scientific evidence and tasks remain
in the project workspace Markdown files.

## Important limitations

- The project registry has only one real project. A second, real project is
  required to validate multi-project onboarding and UI capability gating.
- The current pipeline registry is hardcoded for Robert and its command paths
  require validation before operators use them as a general job catalogue.
- Job execution currently runs as asynchronous child processes owned by the
  FastAPI service. It is not an external queue or worker deployment.
- Authentication for mutations is only enforced when
  `AISCI_DASHBOARD_TOKEN` is configured.
- SQLite is the current local operational store. It is not a claim of
  multi-worker production scalability.

## Current researcher-facing source of truth

| Need | Canonical location |
|---|---|
| Project registration | `research/projects.toml` |
| Robert evidence status | `research/robert/evidence-ledger.md` |
| Robert science queue | `research/robert/next-actions.md` |
| Robert reproducible runs | `research/robert/runs/` |
| Shared physics code and tests | `libs/physics-core/` |

## Historical integration records

Historical documentation about Onyx, DeerFlow, LiteLLM, MCP, and RAG remains
in the repository for context and git-history traceability. It does not
describe services that are present in this checkout or should be used as an
active runbook.
