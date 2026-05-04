---
name: robert-physics-validation
description: Validate Robert's HEP physics paper with source-grounded literature checks, symbolic equation review, numerical fitting, plot generation, and referee-style reporting. Use when working on Robert's boson probability function paper, ATLAS 13 TeV data, Tsallis or Blast-Wave comparisons, chi2/ndf checks, or HEP fit diagnostics.
---

# Robert Physics Validation

Use this skill for Robert's paper-validation workflow. The goal is not to produce confident prose first; the goal is to produce traceable evidence, reproducible checks, and clear uncertainty.

## Operating Rules

- Treat `research/robert/` as the durable science workspace.
- Treat `docs/ops/` as platform notes only.
- Use source-grounded evidence for physics claims.
- Mark unsupported claims as open questions.
- Keep code, commands, and generated outputs inside a dated run folder under `research/robert/runs/`.
- Prefer small reproducible scripts over one-off notebook state.
- Do not treat DeerFlow memory as scientific evidence.

## Workflow

1. Define the exact claim, equation, fit result, or manuscript section being checked.
2. Collect sources and update `research/robert/evidence-ledger.md`.
3. Extract equations and assumptions into a short validation note.
4. Run symbolic or numerical checks.
5. For fit work, compute parameter values, uncertainties, covariance/correlation where available, chi2, ndf, and chi2/ndf.
6. Compare against relevant HEP baselines such as Tsallis and Blast-Wave models.
7. Generate figures and tables with clear filenames.
8. Update the run folder with inputs, commands, results, figures, and interpretation.
9. Update `research/robert/referee-report-draft.md` only after evidence and computations are recorded.

## Expected Output Shape

- Short summary of what was checked.
- Evidence table or source references.
- Commands executed.
- Files created or updated.
- Results and limits.
- Open questions.
- Recommended next action.

