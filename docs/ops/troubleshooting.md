# Troubleshooting the AiSci Control Plane

This runbook covers the active Vite/TanStack Start dashboard, FastAPI Ignition
API, project registry, canonical projections, and local pipeline handling.

## Dashboard or API is unavailable

1. Check listeners:

   ```bash
   ss -ltnp '( sport = :5173 or sport = :8001 )'
   ```

2. Inspect `deployment/aisci-dashboard/frontend.log` and `backend.log`.
3. Start the local pair only if stopping existing listeners is acceptable:

   ```bash
   bash start_dashboard.sh
   ```

## A project route returns not found or no data

1. Verify the ID and root in `research/projects.toml`.
2. Confirm the project root contains the configured canonical files and `runs/`
   directory.
3. Inspect `ignition/project_registry.py` path-containment validation.
4. Trigger the authenticated project sync only after canonical files have been
   checked; the Markdown files remain authoritative.

## A pipeline is unavailable or fails immediately

1. Inspect the registered `PipelineSpec` and its command/working directory.
2. Verify the command exists and its input gates are satisfied before retrying.
3. Read the job's project-scoped log under the relevant run directory.
4. Treat a failed command as a failed job, not a scientific anomaly or claim.

## Fits or anomalies are missing

1. Check the selected project's `runs/` directory for the required artifacts.
2. Confirm `fit_quality.csv` and optional parameter/correlation files conform
   to the parser contract.
3. Inspect the run's provenance and validation gates before interpreting any
   returned metric.

## Historical integrations

This checkout has no active Onyx, DeerFlow, LiteLLM, MCP proxy, OpenSearch, or
Celery deployment. Do not apply old container/RAG instructions as a fix for a
current dashboard problem.
