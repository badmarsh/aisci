**Instructions for the User:** Copy everything below the line and paste it into a fresh agent session.

---

You are the Principal Systems Architect for the AiSci repository. Your mission is to execute a final stabilization and sanitation pass on the control-plane architecture.

Do NOT act as a science researcher in this session. You are exclusively modifying infrastructure, deployment, and dashboard boundaries. You must strictly adhere to the `AGENTS.md` guidelines—in particular, do not promote claims without evidence ledger support, respect the single source of truth for platform/science tracking, and do not create placeholder markdown files.

### Phase 1: Sanitize Legacy Configuration & Workspaces
- Investigate `.vscode/` (e.g. `settings.json` or workspaces) for references to non-existent directories, specifically `/home/ubuntu/aisci/deployment/onyx/onyx-mcp-server`, and remove them to resolve IDE workspace errors.
- Scan `/docs/archive/` and the root for remaining DeerFlow, Onyx, LiteLLM, or MCP legacy files that are not active. Retain them only as historical context, ensuring they do not clutter active operational runbooks.
- Ensure no scratch scripts or temporary test files violate repository hygiene rules.

### Phase 2: Stabilize the Control Plane & Worker Architecture
- Harden the database interactions in `deployment/aisci-dashboard/ignition/worker.py`. The current polling mechanism performs a `SELECT` followed by an `UPDATE` in separate steps, which can cause race conditions if multiple workers exist. Implement database locking (`BEGIN EXCLUSIVE` or SQLite transactions with status conditions).
- Add timeout mechanisms and graceful error handling for pipeline child processes in the worker.
- Audit `deployment/aisci-dashboard/ignition/api.py` security boundaries. Ensure token checks and CORS policies are robust for non-local environments, and fail closed if `AISCI_DASHBOARD_TOKEN` is unset in production.

### Phase 3: Complete Dashboard Features (Platform Backlog P1/P2)
- **Science Artifacts Provenance (P1):** Complete the versioned run/artifact provenance mapping. The API currently just uses `get_latest_run_path()`. Implement a complete manifest for fit and audit outputs (including input hashes and validation-gate results) and link them back to canonical claims.
- **Literature Provenance (P2):** Make literature source ingestion project-scoped and idempotent. Enhance `api.py` and the literature parsing logic to explicitly record provider/provenance fields, and enforce idempotent ingestion constraints.

### Execution Plan
Please review these steps and provide a detailed Implementation Plan artifact summarizing how you will execute these three phases. Do not begin execution until I approve the plan.
