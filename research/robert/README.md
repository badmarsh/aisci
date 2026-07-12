# Robert Physics Validation Workspace

This folder is the durable, tool-agnostic record for Robert's paper validation workflow.

## Goal

Validate the "Boson probability function for the moving system" paper against equations, data behavior, fit stability, and HEP phenomenology literature.

Current local checks are treated as sanity checks until they are tied to exact manuscript equations, full pT data, fit-quality outputs, and literature-matched baselines.

## Files

- `workflow.md` - high-level process independent of Onyx or DeerFlow internals.
- `science-questions.md` - active scientific questions and hypotheses.
- `evidence-ledger.md` - claims, sources, and evidence status.
- `validation-plan.md` - formula, dimensional, numerical, and literature checks.
- `fit-plan.md` - fitting strategy and expected outputs.
- `referee-report-draft.md` - running draft of referee-style critique.
- `next-actions.md` - current work queue.
- `runs/` - dated, reproducible analysis runs.

## Canonical Scripts
- **boson_paper_analysis.py**: The canonical analysis script is located at `libs/physics-core/src/boson_paper_analysis.py`.
