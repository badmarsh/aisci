---
name: reproducible-physics-runner
description: Run or prepare Robert physics validation scripts, fits, plots, and sanity checks with reproducible inputs, assumptions, outputs, and run artifacts under research/robert/runs/YYYY-MM-DD-*.
---

# Reproducible Physics Runner

Use this when executing or preparing physics validation work in `physics/src/` or `research/robert/runs/`.

## Read First

- `AGENTS.md`
- `research/robert/workflow.md`
- `research/robert/fit-plan.md`
- `research/robert/evidence-ledger.md`
- `research/robert/next-actions.md`
- Relevant scripts under `physics/src/`

## Rules

- Treat scripts as sanity checks unless inputs, assumptions, manuscript references, and outputs are recorded.
- Do not create empty placeholder run files.
- Put real artifacts under `research/robert/runs/YYYY-MM-DD-*`.
- For blocked runs, keep requirements and status in the run `README.md` until artifacts exist.
- Do not physically interpret fit parameters without chi2/ndf, covariance, correlations, residuals, fit-range sensitivity, and baseline comparisons.
- Preserve Bose-Einstein versus Boltzmann/Juttner wording.

## Workflow

1. Identify the exact scientific question and evidence gate.
2. Confirm required input data exists, especially Robert's full pT tables when needed.
3. Create or update a dated run folder only when there is a real run or a concrete blocked-run status to record.
4. Run the smallest relevant script or test.
5. Save command, inputs, assumptions, outputs, and interpretation limits.
6. Update `research/robert/evidence-ledger.md` or `research/robert/next-actions.md` only when the user accepts the change.

## Approval Gates

Ask before large parameter sweeps, long compute jobs, installing packages, or changing canonical science status.
