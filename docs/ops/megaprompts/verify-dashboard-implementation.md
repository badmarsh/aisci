# Megaprompt: Comprehensive Dashboard Implementation Verification

**Instructions:** Copy and paste the prompt below into a new agent session to perform a final, comprehensive audit of the `aisci-dashboard` application. This ensures the successful integration of the last three major architectural phases: the v0 aesthetic redesign, the physics fits robustness updates, and the full backend/frontend control plane completion.

---

### The Prompt

**Role**: You are a Principal Software QA and Audit Engineer. 

**Context**: Over the last several sessions, the `aisci-dashboard` underwent three major transformations:
1. **v0 Dashboard Redesign**: A complete frontend overhaul moving to Vite + TanStack Router with a premium, high-density scientific aesthetic (Tailwind, shadcn/ui, Recharts).
2. **Fits Robustness & Anomalies**: Deep theoretical alignments to the fitting pipeline, ensuring proper Jacobian ($dy/d\eta$) warnings, Jüttner singularity flagging, and robust edge-case handling for minuit failures.
3. **Dashboard Completion**: Full integration of the FastAPI `ignition` backend with the frontend, moving to explicit project-scoped routes (`/projects/$projectId/`), implementing strict TypeScript constraints, and adding capability-based route gating.

**Your Task**: 
Conduct a thorough verification of the system to ensure no regressions occurred during the integration of these three megaprompts. You must verify the application's correctness, aesthetic compliance, theoretical alignment, and test coverage.

**Step 1: Frontend Architecture & Aesthetic Verification**
- Verify that the frontend exclusively uses Vite and TanStack Router (`src/routeTree.gen.ts`). Ensure there are no lingering Next.js or TanStack Start artifacts.
- Check that the UI components (e.g., `MetricCard.tsx`, `PageShell.tsx`) adhere to the requested premium scientific aesthetic (dark mode palette, glassmorphism).
- Ensure there are no unused `@ts-expect-error` directives or implicit `any` types in critical data fetching and routing paths.

**Step 2: Physics Fits & Theoretical Alignment Verification**
- Inspect `src/routes/projects.$projectId.fits.tsx` and `ignition/api.py`.
- Verify that the API and UI dynamically extract and filter the correct physics models (e.g., `Jüttner/Boltzmann 1c`, `Tsallis-Pareto 2c`).
- Ensure the UI explicitly renders the **Jacobian Correction Required** warning and handles missing/singular covariance matrices gracefully without crashing.

**Step 3: Control Plane & Capability Gating Verification**
- Inspect the TanStack routes in `src/routes/`. Verify that all routes are project-scoped (e.g., `/projects/$projectId/evidence`).
- Check that `beforeLoad` capability gating is strictly enforced (e.g., the `fits` route requires the `fit_validation` capability in `projects.toml`).
- Verify that the SQLite database migrations in `ignition/database.py` are correct and support job executions and activity logs.

**Step 4: End-to-End Testing and Linting**
1. Run `npm run lint` in `deployment/aisci-dashboard` and verify there are zero errors.
2. Run `npm run test:e2e` using Playwright. All tests (Overview, Fits, Evidence, Tasks, Literature) must pass. Ensure the tests are correctly querying the project-scoped routes.

**Step 5: Documentation Reconciliation**
- Read `docs/ops/architecture-overview.md` and `docs/ops/CURRENT_STATUS.md`.
- Verify they accurately state that the frontend uses Vite + TanStack Router, that project isolation is fully implemented, and that the SQLite operational store is functioning as expected.

**Output:**
Once complete, produce a final `audit_report.md` artifact summarizing your findings for each of the 5 steps. If you find any discrepancies, fix them immediately before concluding your report. Do not stop until the system is 100% verified.
