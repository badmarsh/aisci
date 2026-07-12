> [!NOTE]\n> Archived on 2026-07-12: Meta-prompt that successfully generated its target prompt.\n\n# AiSci Stabilization & Completion Analysis Prompt

**Instructions for the User:** Copy everything below the line and paste it into a fresh agent session.

---

You are the Principal Systems Architect for the AiSci repository in `/home/ubuntu/aisci`. 

Your task is to thoroughly analyze the current state of the repository—specifically the `aisci-dashboard`, the `ignition` API, the background worker, and the multi-project registry—and then **produce a comprehensive, actionable Megaprompt**. 

The Megaprompt you produce will be handed off to an agent in a future session to execute the final stabilization, repository sanitation, and dashboard completion tasks.

### Phase 1: Context Gathering & Analysis
Before you write the Megaprompt, you must read and analyze the current state of the repository. Review the following files to build your understanding:
1. **Backlog & Architecture:** Read `docs/ops/platform-backlog.md`, `docs/ops/architecture-overview.md`, and `docs/ops/deployment-reference.md`. Determine what remaining P1 and P2 items are outstanding (e.g., versioned artifacts, literature ingestion, archive hygiene).
2. **Backend & Worker Boundaries:** Read `deployment/aisci-dashboard/ignition/api.py` and `deployment/aisci-dashboard/ignition/worker.py`. Assess if the SQLite job executions table is robust against race conditions, if pipeline logs are properly streamed, and if the security boundaries (CORS, token checks) are complete.
3. **Frontend Integration:** Audit the `aisci-dashboard` source to see if the frontend perfectly matches the backend API changes for the pipeline and project capability routing.
4. **Repository Hygiene:** Check the repository root and `/docs` for legacy files, outdated instructions, scratch scripts, or artifacts that violate the clean state defined in `AGENTS.md`.

### Phase 2: Produce the Megaprompt
Based on your analysis, write the final Megaprompt. It must be formatted clearly (starting with `**Instructions for the User:** Copy everything below the line and paste it...`) and outline strict, safe, incremental phases to accomplish the stabilization and completion.

**The Megaprompt must instruct the target agent to:**
- **Sanitize:** Clean up any dead code, historical artifacts, or outdated markdown docs.
- **Stabilize:** Harden the backend worker architecture (e.g., database locks, timeout mechanisms, graceful error handling).
- **Finish the Dashboard:** Implement the remaining outstanding features defined in the `platform-backlog.md` (e.g., versioned run artifacts, literature provenance).
- **Follow Rules:** Strictly obey `AGENTS.md` regarding science claims and file creation.

Do **not** execute the stabilization changes yourself in this session. Your only deliverable is the thoroughly researched and expertly crafted Megaprompt.
