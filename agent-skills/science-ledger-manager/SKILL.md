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

## Rules

- Keep Bose-Einstein versus Boltzmann/Jüttner wording explicit in every claim entry.
- Do not infer causality or root cause from suggestive fits.
- Do not interpret fit parameters physically without fit quality, covariance, correlations, residuals, fit-range sensitivity, and baseline comparisons attached.
- Do not promote a claim beyond `Sanity checked` unless exact manuscript equation/table/figure identifiers, input data, reproducible outputs, and relevant literature are attached.
- Compare against literature-matched Tsallis/Tsallis-Pareto and Blast-Wave baselines before any novelty or model-quality claims.
- Keep Onyx, DeerFlow, Docker, MCP, and deployment details out of science files unless needed as execution provenance.
- Evidence states are defined in `docs/decisions/2026-04-26-science-evidence-standards.md`: `Open`, `Sanity checked`, `Supported`, `Suggestive`, `Refuted`, `Blocked`.

## Workflow

1. Read the relevant science files listed in **Read First** before changing anything.
2. Add or update claim entries in `evidence-ledger.md` with evidence links, run artifact paths, and status.
3. Add any blocked requirements or missing gates to `next-actions.md`.
4. Put real run artifacts under a dated run folder (`runs/YYYY-MM-DD-<slug>/`).
5. Verify that promoted claims meet the gate criteria for their target state before writing.
6. Report all changes made and remaining evidence gaps.

## Output & Approval Gates

- Present all ledger changes as a diff-style summary (claim · old status → new status · evidence added).
- Do not promote any claim to `Supported` without explicit user confirmation that all gate criteria are met.
- After updating, list remaining `Open` and `Blocked` claims with their next required gate action.
- Ask for approval before writing any claim that involves a new physical interpretation (not just status bookkeeping).
