# Megaprompt: Sync Architecture Documentation to Repository Reality

**Instructions for the User:** Copy everything below the line and paste it into your target LLM or agent to execute the documentation sync.

---

You are the principal platform documentation engineer for the `/home/ubuntu/aisci` repository.
Your task is to comprehensively audit and update our canonical documentation to reflect the *actual current state* of the repository, not its history. 

Recently, the repository underwent significant architectural changes. Legacy systems such as Onyx, DeerFlow, LiteLLM, and the MCP proxy are no longer present in the `deployment/` directory. The system has transitioned into a simplified Project-Based Research Control Plane composed of the AiSci Dashboard (Next.js) and the Ignition Engine (FastAPI) interacting with `libs/physics-core/`.

## The Task

Update the following canonical documentation files so they accurately describe the system as it exists on disk right now:
1. `docs/ops/architecture-overview.md`
2. `docs/ops/platform-backlog.md`
3. `README.md`
4. `docs/ops/CURRENT_STATUS.md`
5. Any other active `.md` files you find that outline the architecture.

## Strict Rules & Constraints

- **Reality Over History:** If a component (e.g., Onyx, DeerFlow, LiteLLM proxy, `onyx-mcp-proxy`) does not exist in the repository (specifically checking the `deployment/` directory), it **MUST NOT** appear in any system diagram, architecture map, or current status document.
- **Archive Legacy References:** Do not delete historical decision records in `docs/decisions/`, but ensure that the *current* architecture documentation strictly reflects the present.
- **System Diagram Restructuring:** Re-draw the system map in `architecture-overview.md`. It should feature the browser connecting to the AiSci Dashboard (`localhost:5173`), which calls the Ignition Engine (`localhost:8001`), which in turn manages `ProjectSpec` workspaces and executes `PipelineSpec` tasks in `libs/physics-core/.venv`. Remove the entire "Onyx Stack", "LiteLLM Proxy", and "Model Providers" sections if they do not exist locally.
- **Backlog Purge:** Audit `platform-backlog.md`. Any tasks related to Onyx ingestion, Vespa, or LiteLLM routing must be moved to an archive section or removed entirely, as those components are gone.
- **Verification First:** Before modifying any file, perform `list_dir` on `deployment/` and read `deployment/aisci-dashboard/docker-compose.yml` (if it exists) to verify what services are actually running. Base all documentation *only* on what you find.

## Execution Steps

1. **Discovery:** Investigate `deployment/` to confirm the absence of Onyx and presence of `aisci-dashboard`. Understand the current `ignition/api.py` and React frontend structure.
2. **Drafting:** Plan the file modifications in a unified implementation plan.
3. **Execution:** Modify `architecture-overview.md` to establish the new ground-truth system diagram.
4. **Propagation:** Cascade this new reality to `README.md`, `CURRENT_STATUS.md`, and `platform-backlog.md`.
5. **Review:** Ensure no orphaned references to "Onyx RAG" or "Celery workers" remain in the active ops documents.

Do not introduce new features or write code; your singular focus is aligning the documentation with the strict reality of the filesystem.
