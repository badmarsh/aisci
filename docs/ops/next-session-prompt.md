# Next Session Prompt

_Last updated: 2026-07-12_

Two prompts are maintained here: one for **platform/ops** work, one for **science workflow** work. Use whichever matches your session goal.

---

## Prompt A — Platform / Ops

Use this prompt to continue the AiSci platform/dashboard development in a fresh coding agent session.

```text
You are continuing the AiSci control-plane platform development.
Repo: /home/ubuntu/aisci, GitHub: badmarsh/aisci.

Read first:
- AGENTS.md
- docs/ops/critical-components.md
- docs/ops/platform-backlog.md
- docs/ops/architecture-overview.md
- docs/ops/deployment-reference.md

Current state as of 2026-07-12:
- The system is a Project-Based Research Control Plane. Legacy components (Onyx, DeerFlow, MCP proxies) have been removed.
- Frontend: Vite/TanStack Start React app in `deployment/aisci-dashboard/`.
- Backend: FastAPI Ignition API in `deployment/aisci-dashboard/ignition/`.
- Both are launched via `./start_dashboard.sh`.
- The database is a local SQLite projection in `deployment/aisci-dashboard/data/evidence_graph.db`.
- Projects are registered in `research/projects.toml`.
- All background pipeline jobs are run as asyncio processes owned by the FastAPI server, logging to `research/robert/runs/...`.

Hard constraints:
- Do not add features that break project isolation; all API calls must be scoped to `{project_id}`.
- Do not write scientific conclusions into the dashboard SQLite database; the database is a read-model of the markdown files.
- Ensure the Playwright tests mock the API layer correctly (no live jobs).

Next highest-value work:
- See `docs/ops/platform-backlog.md` for active tasks.

Before closing:
- Run `./start_dashboard.sh` to ensure both services boot successfully.
- Check `curl -fsS http://127.0.0.1:8001/api/health`.
- Report what was changed, what was pushed, and any remaining test gaps.
```

---

## Prompt B — Science Workflow: Data Collection → Model Training → Documentation

Use this prompt to execute the AiSci physics research workflow in a fresh local agent session.

```text
You are continuing the AiSci physics research and documentation workflow.
Repo: /home/ubuntu/aisci, GitHub: badmarsh/aisci.

Read first (in this order):
- AGENTS.md
- agent-skills/git-worktree-guard/SKILL.md
- research/robert/next-actions.md       ← canonical science task queue
- research/robert/evidence-ledger.md    ← canonical claim-status file
- physics/README.md
- docs/ops/critical-components.md

Current state as of 2026-07-12:
- Physics scripts are ready but blocked on data:
  - `libs/physics-core/src/fitting_pipeline.py`        ready; awaiting `libs/physics-core/data/fit_input.csv`
  - `libs/physics-core/src/tsallis_physics_validation.py`  ready; awaiting data
  - `libs/physics-core/src/boson_paper_analysis.py`    green (all symbolic sections pass)
  - `libs/physics-core/src/sympy_validation_agent.py`  ready
  - `libs/physics-core/src/data_loader.py`             ready
- Virtual environment: `libs/physics-core/.venv` — use it for all script runs.
  It already has matplotlib 3.10.9 installed.
- Tests in `libs/physics-core/tests/` — run with `cd physics && pytest` using `physics_env`.
- Science task queue item [B-01] is the primary blocker: Robert must supply the
  per-multiplicity-bin pT spectrum table (bins 21-30 through 126-150) before
  fitting can run. HEPData record `ins1419652` provides only inclusive spectra.
- Science task [O-02] is open and does not require data: Robert to confirm
  whether U2 ≈ 0.011 ± 0.847 is a known instability at high multiplicity.
- Science task [O-03] (train and validate fitting pipeline) is defined and
  ready to execute the moment `libs/physics-core/data/fit_input.csv` exists.

Step 1 — Data Collection and Preprocessing:
  If Robert has provided a data table, save it as `libs/physics-core/data/fit_input.csv`
  following the format spec in `research/robert/archive/data-onboarding.md`.
  Run `libs/physics-core/src/data_loader.py` to verify integrity. Clean, normalize, and
  check for missing bins or inconsistent uncertainties. Log outcome to
  `research/robert/runs/YYYY-MM-DD-data-load/README.md`.

Step 2 — Model Training and Validation [O-03]:
  Once `fit_input.csv` exists:
  1. Activate `libs/physics-core/.venv` and run `libs/physics-core/src/fitting_pipeline.py`.
  2. Profile execution: time each fitting loop and scipy optimization call;
     save the profile report to `physics/reports/fitting_profile.txt`.
  3. Run `libs/physics-core/src/tsallis_physics_validation.py` — verify T, q, n converge
     within physical bounds; log chi2/ndf anomalies.
  4. Run `libs/physics-core/src/sympy_validation_agent.py` — confirm symbolic derivations
     match numerical outputs within floating-point tolerance.
  5. Cross-validate `boson_paper_analysis.py` outputs against reference values
     in `research/robert/evidence-ledger.md`. Flag deviations beyond tolerance.
  6. Extend `libs/physics-core/tests/test_fitting_pipeline.py` with:
     - Edge-case tests: out-of-bounds parameters, empty dataset inputs.
     - Regression tests: assert chi2/ndf, T, U, n per bin are reproducible.
  7. Save all artifacts (chi2/ndf, covariance, residuals, plots) to
     `research/robert/runs/YYYY-MM-DD-fitting-pipeline-validation/`.
  Do NOT promote any fit result beyond `Sanity checked` in the evidence ledger
  until chi2/ndf, covariance, correlations, residuals, fit-range sensitivity,
  and baseline comparisons are all recorded.

Step 3 — Simulation and Analysis:
  Run a full end-to-end pipeline:
    data_loader → fitting_pipeline → tsallis_physics_validation → boson_paper_analysis
  Capture all stdout/stderr, timing metrics, and output plots.
  Compare against the prior run in `research/robert/runs/2026-05-04-tsallis-validation/`
  to detect regressions. Save to `research/robert/runs/YYYY-MM-DD-full-run/`.

Step 4 — Documentation and Reporting:
  After a successful pipeline run:
  1. Generate a Python-based run report: use `python-executor` to produce a
     Markdown summary of inputs, outputs, chi2/ndf table, parameter table,
     residual plots, and any flagged anomalies. Save to
     `research/robert/runs/YYYY-MM-DD-full-run/report.md`.
  2. Update `research/robert/evidence-ledger.md` — add evidence links and
     update status for any claims that now have run support. Merge with existing
     rows; do not duplicate.
  3. Update `research/robert/next-actions.md` — mark [O-03] completed, add any
     new follow-up tasks that the run reveals.
  4. Do NOT create a new standalone report markdown by default. Prefer updating
     `evidence-ledger.md` and `next-actions.md` with the smallest useful note,
     per AGENTS.md follow-through rules.

Hard constraints:
- All script outputs are "Sanity checks" only until evidence-ledger support exists.
- Do not infer causality from fit behavior alone.
- Keep Bose-Einstein vs Boltzmann/Juttner wording explicit.
- Do not interpret fit parameters physically until chi2/ndf, covariance,
  correlations, residuals, fit-range sensitivity, and baseline comparisons exist.
- Keep platform details (Dashboard, FastAPI, Docker) out of science files.
- Put temporary helper scripts in `deployment/helper/`, not in `libs/physics-core/src/`.
- Do not create empty placeholder run files.
- Preserve unrelated user changes in the working tree.

Before closing:
- Run `cd physics && pytest` and confirm all tests pass.
- Run `git status -sb` — commit only intentional changes.
- Report what was run, what was changed, what was pushed, and any remaining
  blockers or open questions for Robert.
```
