# Platform Backlog

This is the operational source of truth for active control-plane work. Science
questions and evidence gates remain in each project's canonical workspace.

## Active work

| Priority | Area | Issue | Why it matters | Next action | Status |
|---|---|---|---|---|---|
| P0 | Pipelines | Make pipeline definitions project-owned and executable | `ignition/pipelines.py` still hardcodes two Robert definitions and their commands need verification. A dashboard must never advertise a pipeline that cannot run. | Move validated definitions into the project contract, validate executable/working-directory/input gates at startup, and expose unavailable pipelines truthfully. | Done |
| P1 | Project isolation | Onboard a second real project | The registry has only Robert; a genuine PhD audit or equivalent project is needed to prove capability-driven UI, data isolation, and review scoping. | Add a real project with its own canonical files and exercise it through the dashboard. | Done |
| P1 | Jobs | Separate job execution from the API process | FastAPI currently owns asynchronous child processes and SQLite job records. Process restarts and multi-worker execution need a durable worker design. | Define and implement the approved worker/database deployment boundary before supporting concurrent agents. | Done |
| P1 | Security | Require a production mutation-auth configuration | Mutation protection is optional when `AISCI_DASHBOARD_TOKEN` is unset. | Define deployment authentication and allowed origins; fail closed outside local development. | Done |
| P1 | Science artifacts | Complete versioned run/artifact provenance | Fit and audit outputs need a complete manifest, input hashes, validation-gate results, and links back to canonical claims. | Extend the registered pipelines and artifact readers without promoting science claims automatically. | Done |
| P2 | Literature | Make literature source/provenance ingestion project-scoped and idempotent | Current paper-source inference and duplicate-claim handling are not sufficient for a portfolio of research projects. | Add explicit provider/provenance fields and idempotent ingestion constraints. | Done |
| P2 | Archive hygiene | Classify remaining legacy integration records | Historical Onyx/DeerFlow/MCP documents are retained, but must stay visibly separate from current runbooks. | 2026-07-12: Added historical marker to 12 legacy files (activepieces-integration, k-dense-skills-reference, kdense-agent-skills, literature-corpus-policy, mcp-endpoints, mcp-hep-servers, model-optimization-report, model-selection-guide, rag-evaluation-results, rag-evaluation-set, semantic-scholar-asta-api, subtree-management). | Done |
| P1 | DB Sync | Fix UNIQUE constraint crash in sync_tasks_to_db | Markdown parser produced duplicate Task IDs; second INSERT crashed on UNIQUE constraint. | Use INSERT OR REPLACE, deduplicate in-memory before DB write, harden auto-generated IDs, strip strikethrough text. | Done |

## Completed architecture milestones

| Milestone | Completed | Evidence |
|---|---|---|
| Initial project-scoped dashboard/API migration | 2026-07-12 | `research/projects.toml`, project-scoped API routes, and project route files under `deployment/aisci-dashboard/` |
| Control-plane documentation reality sync | 2026-07-12 | Current architecture, deployment, status, component, and backlog docs rewritten from the present filesystem |

## Historical note

Prior rows concerning Onyx, DeerFlow, LiteLLM, OpenSearch, Vespa, Celery, and
MCP proxy operations were removed from this active backlog because those
deployments are absent from the current repository checkout. Their historical
records remain available in dated documentation and git history; they are not
active operational work.
