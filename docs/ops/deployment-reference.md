# Deployment Reference

_Last verified against the repository and local listeners: 2026-07-12._

## Active local services

| Service | URL | Implementation |
|---|---|---|
| AiSci Dashboard | `http://localhost:5173` | Vite / TanStack Router / @tanstack/react-start React app in `deployment/aisci-dashboard/` |
| Ignition API | `http://localhost:8001` | FastAPI app in `deployment/aisci-dashboard/ignition/` |

Start both with:

```bash
bash start_dashboard.sh
```

The script terminates existing listeners on ports `5173` and `8001` before it
starts replacements. Do not use it when those processes belong to another
operator unless that interruption is intended.

## Deployment shape

There is no `docker-compose.yml` or `docker-compose.yaml` under `deployment/`
in this checkout. The current control plane is a local Node/Vite frontend plus
a local Python/FastAPI backend.

| Path | Role |
|---|---|
| `deployment/aisci-dashboard/` | Active dashboard application |
| `deployment/aisci-dashboard/ignition/` | Project-scoped control API and local job handling |
| `deployment/aisci-dashboard/data/` | Runtime SQLite data; ignored from git |
| `deployment/helper/` | Operational helper scripts; not a deployed service |
| `deployment/hep-physics/` | Archived v0 concept, not active runtime |
| `libs/physics-core/` | Shared physics code and isolated Python environment |
| `research/projects.toml` | Project registry |

## Operational commands

```bash
# Frontend static/type checks
cd deployment/aisci-dashboard
npm run lint
npx tsc --noEmit

# Physics tests use the project-specific virtual environment
cd /home/ubuntu/aisci
libs/physics-core/.venv/bin/python -m pytest libs/physics-core/tests

# Inspect active local listeners
ss -ltnp '( sport = :5173 or sport = :8001 )'
```

## Not part of the current deployment

Do not use this document to operate Onyx, DeerFlow, LiteLLM, OpenSearch,
Celery, an MCP proxy, Ollama, or any previous Docker stack. None has a
corresponding deployment directory or Compose file in this checkout.

Historical integration documentation is retained for context only. Current
architecture is documented in [`architecture-overview.md`](architecture-overview.md).
