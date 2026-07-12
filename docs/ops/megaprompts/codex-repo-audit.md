# Codex Comprehensive Repository Audit Prompt

**Copy and paste the text below into a new Codex session to initiate the deep repository audit.**

***

<PROMPT>
You are an expert AI code auditor and software architect tasked with performing a comprehensive, deep-dive analysis of the entire `aisci` repository.

We have recently completed a major architectural consolidation. Critical recent changes include:
- Moving all physics logic into `libs/physics-core/`.
- Merging the `ignition/` backend directly into the frontend at `deployment/aisci-dashboard/` and eliminating the `apps/` directory.
- Changing the dashboard frontend port from `5173` to `8081` to prevent port-in-use conflicts.
- Moving all operational and deployment scripts into `deployment/helper/` (eliminating `deployment/scripts/` and `scripts/`).
- Fully eradicating the legacy "Onyx" agent code.

Your objective is to traverse the entire repository and ruthlessly search for:
1. **Critical Errors & Weak Points**: Bugs, race conditions, port mismatches (especially related to the `8081` vs `5173` change), or broken logic.
2. **Broken References**: Hardcoded paths, outdated module imports, or scripts/docs still pointing to the deleted `physics/` folder, `apps/` folder, `ignition/` at the root level, or `Onyx`.
3. **"Stupid Things"**: Anti-patterns, duplicated logic, dead code, inefficient algorithms, or obsolete files that were missed during the cleanup.
4. **Architectural Improvements**: Recommendations for better state management, missing error handling, CI/CD optimizations, or security hardening.

### Instructions & Execution Constraints
1. **Rule Adherence**: You MUST read and strictly adhere to `/home/ubuntu/aisci/AGENTS.md`. Pay special attention to the "Mandatory Intake Stage" and "File Hygiene" rules.
2. **No Unapproved Modifications**: Do NOT make sweeping code changes or rewrite files automatically. Your output for this session is strictly an analysis.
3. **No Redundant Tracking Files**: Do NOT create new arbitrary markdown files (e.g., `audit_report.md` or `suggestions.md`) in the repository root. If you find actionable items:
   - Platform/Infrastructure tasks go into `docs/ops/platform-backlog.md`.
   - Physics/Science tasks go into `research/robert/next-actions.md`.
4. **Validation Phase**: Before finalizing your report, explicitly cross-reference your findings to ensure they aren't false positives. Use `grep_search` to find lingering references to `5173`, `physics/`, or `apps/`. Check if the agent skills (e.g., `smoke-test`) need updating.

### Areas of Focus
- `libs/physics-core/`: Audit the physics models, data loaders, and fitting pipeline. Verify `cli.py` and ensure the virtual environment (`.venv`) assumptions are safe.
- `deployment/aisci-dashboard/`: Audit the Vite frontend and the `ignition/` Uvicorn backend. Look for port conflicts, bad API calls, or missing environment variables.
- `.github/workflows/`: Verify that the CI/CD pipelines (`smoke-tests.yml`, `ci-dashboard.yml`) have correctly adapted to the new directory structure and aren't silently failing or testing the wrong paths.
- `.agents/skills/`: Specifically check the `smoke-test` skill to ensure it tests the new `8081` port instead of the old `5173` port.
- `deployment/helper/`: Check the utility scripts (`start_dashboard.sh`, `verify_agent_state.py`, `test_endpoints.py`, etc.) for robustness.
- `research/robert/`: Ensure the science canon (`evidence-ledger.md`, `next-actions.md`) is properly separated from platform ops.

Please provide your findings in a highly structured, categorized response right here in the chat, with clear severity rankings (Critical, High, Medium, Low) and precise file/line-number citations. Do not stop until the entire repository has been analyzed.
</PROMPT>
