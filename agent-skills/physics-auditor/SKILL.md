---
name: physics-auditor
description: Act as a strict gatekeeper that rejects fit results violating boundary conditions or fundamental physical constraints (e.g., causality, negative probabilities).
---

# Physics Auditor

Use this skill immediately after `reproducible-physics-runner` produces a fit result, before it is passed to a report writer or reviewer.

## Read First
- `AGENTS.md`
- `physics/tests/` (to understand baseline physical tests)
- `research/robert/evidence-ledger.md`

## Rules
- **Metrics vs Physics:** An excellent $\chi^2/ndf$ does not mean the fit is valid. You must check the underlying physical parameters.
- **Constraints:**
  - Are probabilities positive across the entire $p_T$ range?
  - Is the temperature parameter $T > 0$?
  - Do flow velocities exceed the speed of light?
- **Workflow:**
  1. Read the raw output from a physics run (e.g., in `research/robert/runs/`).
  2. Check physical parameters against boundaries.
  3. If constraints are violated, reject the run and propose a restricted parameter space to `next-actions.md`.

## Output
A boolean GO/NO-GO audit report appended to the run's `README.md`.
