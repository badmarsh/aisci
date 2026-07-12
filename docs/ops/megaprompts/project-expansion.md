# AiSci Project Expansion & Pipeline Registry Megaprompt

**Instructions for the User:** Copy everything below the line and paste it into your target LLM or agent.

---

You are the principal engineer continuing the implementation of AiSci’s project-based research control-plane architecture in `/home/ubuntu/aisci`.

The legacy architecture scrub is complete. You are now tasked with executing **Project Expansion** and **Pipeline Registry Refinement**, which correspond to the highest priority active tasks in our backlog.

## Product Definition & Goals

The AiSci Dashboard is a simple control and monitoring panel for a portfolio of repository-based research projects. The overarching goal for this session is to prove that the architecture supports true multi-project isolation and capabilities routing by onboarding a second "real" project, and to move pipeline definitions out of hardcoded backend files into project-owned configurations.

### Read First
Read and obey in full:
- `AGENTS.md`
- `docs/ops/critical-components.md`
- `docs/ops/platform-backlog.md`
- `docs/ops/architecture-overview.md`
- `docs/ops/deployment-reference.md`
- `research/projects.toml`

**Important Repository Constraints:**
- The legacy components (Onyx, DeerFlow, MCP proxies, etc.) are gone. Do not attempt to revive them or reference them as active.
- Frontend: Vite/TanStack Start React app in `deployment/aisci-dashboard/`.
- Backend: FastAPI Ignition API in `deployment/aisci-dashboard/ignition/`.
- Database: local SQLite projection in `deployment/aisci-dashboard/data/evidence_graph.db`.
- **Do not write scientific conclusions into the dashboard SQLite database; it is merely a read-model.**
- **Do not invent a pipeline or capability if it does not actually exist or work.**

## Required Implementation Phases

### Phase 1 — Project Isolation & Expansion
Currently, the registry (`research/projects.toml`) only defines Robert's manuscript validation. We need to onboard a second genuine project to prove the capability-driven UI, data isolation, and review scoping.

1. **Create the New Project Structure:** Add a new project (e.g., a "PhD Audit" or "Literature Review" project) in the `research/projects.toml` registry.
2. **Setup Canonical Files:** Create the corresponding canonical Markdown files (e.g., `evidence-ledger.md`, `next-actions.md`) within the new project's workspace directory (e.g., `research/phd-audit/`).
3. **Configure Differentiated Capabilities:** Ensure this new project defines a different set of capabilities than Robert's project (e.g., it might have "tasks" and "evidence", but NOT "fit_validation" or "symbolic_validation").
4. **UI Validation:** Ensure the dashboard natively respects these boundaries. If a user routes to the new project, the UI should only render the capabilities declared by its manifest. Cross-contamination between Robert's project and the new project is strictly forbidden.

### Phase 2 — Pipeline Registry Refinement
Pipeline definitions currently live as hardcoded records in `deployment/aisci-dashboard/ignition/pipelines.py`. A dashboard must never advertise a pipeline that cannot run or is hardcoded globally.

1. **Project-Owned Configuration:** Move pipeline definitions from the hardcoded Ignition backend into project-owned configurations (e.g., within `project.toml` or a dedicated `pipelines.toml` within the project root).
2. **Executable Validation:** The backend must validate that the commands for these pipelines are executable, that working directories exist, and that necessary input gates are met at startup.
3. **Truthful Status Expose:** Expose unavailable pipelines truthfully in the API and UI. Do not fake health or pretend a script works if it is broken. 

### Phase 3 — Truthful Job & Pipeline Monitoring
Ensure the frontend accurately represents the new project-owned pipelines and their capabilities. 
1. The UI must only allow a user to launch pipelines registered to their specific, active project.
2. If a pipeline requires inputs (e.g., a `fit_input.csv`), the UI/backend must enforce pre-flight checks and fail clearly if requirements are not met.

## Delivery Process

1. Inspect current state: read the files listed in **Read First**.
2. Analyze how to gracefully move pipeline definitions from `ignition/pipelines.py` into the `ProjectSpec` registry model without breaking existing dashboard functionality for the `robert-boson-manuscript`.
3. Implement the new Pipeline Registry architecture in the Ignition backend.
4. Onboard the second project and set up its directory structure and capabilities.
5. Update tests to cover the project isolation and pipeline parsing logic.
6. Verify locally by running `./start_dashboard.sh` and navigating through both projects in the dashboard.

## Final Response Requirements

When your work is complete, report:
- The exact files modified to support the Pipeline Registry migration.
- The details of the second project onboarded and how it proves capability-driven isolation.
- How you verified that pipelines are properly constrained and executable.
- Any remaining blockers or gaps for the remaining P1 tasks in the `platform-backlog.md` (e.g., Job Execution separation or Authentication).

**Do not claim completion unless the new project renders correctly without bleeding capabilities from Robert's project, and all pipelines are successfully project-owned.**
