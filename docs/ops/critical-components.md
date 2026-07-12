# AiSci Control Plane — Critical Components

Scientific conclusions remain in project evidence ledgers. This document maps
the current implementation components that make those workflows observable and
reproducible.

## 1. Project control plane

| Component | Location | Responsibility |
|---|---|---|
| Dashboard | `deployment/aisci-dashboard/src/` | Project portfolio and capability-scoped research UI |
| Ignition API | `deployment/aisci-dashboard/ignition/api.py` | Project-scoped queries, review requests, job dispatch, activity, and logs |
| Project registry | `research/projects.toml`, `ignition/project_registry.py` | Maps a project ID to its repository workspace and capabilities |
| Pipeline registry | `ignition/pipelines.py` | Current local pipeline definitions; commands require verification before use |
| Operational store | `ignition/database.py` | SQLite projections, activity, review decisions, and job records |
| Canonical sync | `ignition/sync_markdown.py` | Projects canonical Markdown into the dashboard read model |

## 2. Current research workspace

`research/robert/` is the sole registered project workspace. It contains the
evidence ledger, next-action queue, manuscript materials, and dated run
artifacts for Robert's manuscript validation.

## 3. Shared physics core

| Component | Location | Role |
|---|---|---|
| Model functions | `libs/physics-core/src/models/` | Jüttner/Boltzmann, Bose-Einstein, Tsallis, and Blast-Wave functions |
| Fitting engine | `libs/physics-core/src/fitting/` | Reusable fitting, metrics, and diagnostic artifacts |
| Project adapters | scripts such as `data_loader.py` and `boson_paper_analysis.py` | Robert-specific data mapping and manuscript validation |
| Test environment | `libs/physics-core/.venv` | Isolated dependencies for physics tests and execution |

The model/fitting modules are the reusable seed. Manuscript-specific data,
assumptions, and scientific interpretation remain project-specific.

## 4. Deliberately absent components

The repository currently has no deployment directory or Compose definition for
Onyx, DeerFlow, LiteLLM, MCP proxy, OpenSearch, Celery, or model providers.
They are not critical components of the active local control plane.
