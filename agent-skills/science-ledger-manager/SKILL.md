---
name: science-ledger-manager
description: Manage Robert science-facing claim status, evidence states, validation gates, and next actions while keeping platform details out of science files.
---

# Science Ledger Manager

Use this for science-facing work under `research/robert/`.

## Read First

- `AGENTS.md`

- Claim status: `research/robert/evidence-ledger.md`
- Science task queue: `research/robert/next-actions.md`
- Workflow: `research/robert/workflow.md`
- Fit method: `research/robert/fit-plan.md`
- Run artifacts: `research/robert/runs/YYYY-MM-DD-*`

## Evidence States

Use the states defined in `docs/decisions/2026-04-26-science-evidence-standards.md`:

- `Open`
- `Sanity checked`
- `Supported`
- `Suggestive`
- `Refuted`
- `Blocked`

Do not promote claims beyond `Sanity checked` unless exact manuscript references, input data, reproducible outputs, and relevant literature are attached.

## Rules

- Keep Bose-Einstein versus Boltzmann/Juttner wording explicit.
- Do not infer causality or root cause from suggestive fits.
- Do not interpret fit parameters physically without fit quality, covariance, correlations, residuals, fit-range sensitivity, and baseline comparisons.
- Compare against literature-matched Tsallis/Tsallis-Pareto and Blast-Wave baselines before novelty or model-quality claims.
- Keep Onyx, DeerFlow, Docker, MCP, and deployment details out of science files unless needed as execution provenance.

## Workflow

1. Read the relevant science files before changing anything.
2. Add or update claim entries with evidence links and status.
3. Add blocked requirements to `next-actions.md`.
4. Put real run artifacts under a dated run folder.
5. Report changes and remaining evidence gaps.
