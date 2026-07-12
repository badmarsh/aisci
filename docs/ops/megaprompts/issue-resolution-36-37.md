# Megaprompt: Verify and Close Control-Plane Stabilization Issues

You are an ops-focused AI agent responsible for verifying and resolving the recent Control-Plane Stabilization work tracked in GitHub. Your mission is to confirm the fixes are stable and close the corresponding issues.

## Objectives
1. **Context:** Read GitHub Issues #36 and #37 to understand the scope of the completed stabilization work.
2. **Verification:** Verify that the stabilization changes (DB Sync Resilience, API Hardening, Frontend Completion, and Ops Hygiene) are intact and functioning correctly on the `main` branch.
3. **Remediation:** If any discrepancies or regressions are found, fix them immediately.
4. **Resolution:** Use the GitHub CLI (`gh issue close`) to close Issue #36 and Issue #37 with an appropriate closing comment.

## Step-by-Step Instructions

### Step 1: Review the Issues
Run the following commands to ingest the context:
```bash
gh issue view 36
gh issue view 37
```

### Step 2: System Verification
1. Check that the required services are running (Dashboard on 5173, API on 8001). If they are not running, start them using `./start_dashboard.sh`.
2. Confirm API hardening by testing an invalid project ID:
   ```bash
   curl -s -i http://localhost:8001/api/projects/NONEXISTENT/tasks
   ```
   *Expected result: HTTP 404 Not Found.*
3. Ensure no scratch `.py` files exist at the repo root and that `docs/ops/platform-backlog.md` shows the DB Sync crash as `Done`.

### Step 3: Close the Issues
Once verification is complete, post a comment and close the issues:
```bash
gh issue close 36 -c "Stabilization passes reviewed and verified against the main branch. All P1 and P2 items have been confirmed implemented successfully. Closing."

gh issue close 37 -c "Stabilization work verified. Sync crash fixed, API hardened, and frontend completed. Closing issue."
```

### Step 4: Final Reporting
Provide a final summary to the user indicating that the verification is complete and both issues have been successfully closed.
