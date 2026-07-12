# Megaprompt: Finalize Dashboard Audit Remediation & Playwright Tests

## Context
We are executing the P0/P1/P2 Implementation to remediate the AiSci Dashboard and Ignition backend audit findings. 

**What we have already accomplished:**
1. **Backend Path Resolution:** Fixed Ignition path resolution to properly locate canonical research files (`research/robert/evidence-ledger.md`, `next-actions.md`).
2. **CQRS & Background Tasks:** Replaced `subprocess.Popen` with safe asyncio-based background task execution.
3. **Frontend Tooling:** Updated `tsconfig.json` and `eslint.config.js` in `deployment/aisci-dashboard` to exclude the backend `ignition` and `.venv` folders, allowing `npm run lint` and `npx tsc --noEmit` to pass with zero errors.
4. **Playwright Mocks:** We identified that `npx playwright test` was failing because the tests were hitting the real backend (which was throwing timeouts or returning unexpected data). We started adding `page.route` intercepts in `evidence.spec.ts`, `overview.spec.ts`, `literature.spec.ts`, and `tasks-agents.spec.ts` to mock backend endpoints as required by the testing rules.

**The Hanging Issue:**
When `npx playwright test` fails, it automatically spins up an HTML reporter on port `9323`, causing the agent's foreground command to hang indefinitely and time out. **You must run Playwright using `CI=true npx playwright test`** to prevent the reporter from blocking execution, and **you must launch it as a background task** (`WaitMsBeforeAsync: 0`).

## Your Task
1. **Verify Playwright Tests:**
   Run the following command as a background task:
   `cd /home/ubuntu/aisci/deployment/aisci-dashboard && CI=true npx playwright test`
   Wait for the background task to complete and inspect its log.
2. **Fix Remaining Mocks:**
   If tests still fail, it is likely because the JSON payload in the `page.route` mock (added in `evidence.spec.ts`, `overview.spec.ts`, `tasks-agents.spec.ts`, etc.) does not perfectly match what the React components (`evidence.tsx`, `overview.tsx`) expect. 
   - *Hint:* `evidence.tsx` expects `claim`, not `statement`. We fixed this, but double check.
   - *Hint:* `overview.tsx` expects `activity` to have at least one element for `ul.space-y-2` to be visible.
   - Adjust the mocks in `tests/e2e/*.spec.ts` until all 7 tests pass.
3. **Final Architecture Alignment:**
   Double check that the ports (Vite on `5173`, Uvicorn on `8001`) are properly aligned and no old `8081` references remain in active code.
4. **Update Documentation (P2 Completion):**
   Update `docs/ops/architecture-overview.md` and `docs/user-manual/USER_MANUAL.md` to reflect the new CQRS and task-management architecture. Add any completed actionable items to `docs/ops/platform-backlog.md`.
5. **Sanity Check:**
   Ensure no temporary scratch files are left in the working directory.

## Strict Rules
- Do not run `npx playwright test` in the foreground. Always use `CI=true npx playwright test` in the background.
- Do not commit, push, or create GitHub Issues unless explicitly requested.
- Read and obey `AGENTS.md` and `deployment/aisci-dashboard/AGENTS.md`.
