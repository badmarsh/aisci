# Codex Comprehensive GitHub Actions Audit Prompt

**Copy and paste the text below into a new AI session to initiate a deep-dive audit of our GitHub Actions workflows.**

***

<PROMPT>
You are an expert DevSecOps engineer and CI/CD architect. Your objective is to perform a rigorous audit of the entire `.github/workflows/` directory in the `aisci` repository to improve robustness, security, and performance.

We recently completed a major architectural consolidation, and some of the workflows have been left behind with dead paths, missing timeouts, and inefficient execution strategies.

Please review all `.yml` and `.yaml` files in `.github/workflows/` and implement the following improvements:

1. **Path Corrections & Dead Links**: 
   - Ensure all `working-directory` declarations map correctly to our new architecture:
     - All physics logic is in `libs/physics-core/`.
     - The frontend and ignition backend are in `deployment/aisci-dashboard/`.
     - Operational scripts are in `deployment/helper/`.
   - Update any legacy Dockerfile paths (`backend/Dockerfile` -> `deployment/aisci-dashboard/Dockerfile` etc.).
   - Fix regex logic in PR triage workflows that references legacy `backend/` and `frontend/` folders.

2. **E2E Testing Architecture (CRITICAL)**:
   - The `aisci-dashboard` Playwright tests now depend on the live `ignition` backend API.
   - You MUST ensure `ci-dashboard.yml` installs Python and the backend dependencies.
   - You MUST update the Playwright config's `webServer` command to spin up BOTH the frontend and backend (e.g., using `cd ../../ && bash start_dashboard.sh`) on port `8081` to prevent 5-second `toBeVisible()` timeouts on the tasks table.

3. **Timeouts**:
   - GitHub Actions default to a 6-hour timeout, which drains runner minutes when tests or installations hang.
   - Inject `timeout-minutes: 10` (or 15) into every job.

4. **Dependency Caching**:
   - Implement `actions/setup-node` caching for `npm` in all frontend workflows.
   - Implement `actions/setup-python` caching for `pip` in Python workflows, or ensure `uv` is configured with caching.
   - Cache heavy external dependencies like Playwright browsers.

5. **Tooling Consistency**:
   - Standardize Node.js versions (e.g., Node 20 or Node 22) across all `deployment/aisci-dashboard` workflows.
   - Ensure dependencies are pinned (e.g., using a lockfile or `requirements.txt` rather than naked `pip install` commands).

6. **Security Best Practices**:
   - Audit the usage of `pull_request_target` to ensure no untrusted code is being checked out.
   - Where possible, pin action versions to exact commit SHAs (e.g., `actions/checkout@<SHA>`) to prevent supply-chain attacks.

Output your findings and formulate a clear Implementation Plan to safely apply these changes without breaking active CI.
</PROMPT>
