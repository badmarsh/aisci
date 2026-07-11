# Robert Validation Workflow

## Boundary

This workflow should read like science work, not platform work. Onyx and DeerFlow are execution adapters:

- Evidence retrieval can be done by Onyx, Scite, Consensus, arXiv, or manual reading.
- Computation can be done by local Python, DeerFlow sandbox, notebooks, or scripts.
- Durable results belong in this folder.

## Flow

1. Define the claim or equation to validate.
2. Collect source evidence and record it in `evidence-ledger.md`.
3. Record assumptions before running checks: Boltzmann versus Bose-Einstein form, mass treatment, eta/pT cuts, fit range, normalization, and parameter bounds.
4. Translate equations into symbolic or numerical checks.
5. Run reproducible computations in a dated run folder.
6. Compare the model against HEP baselines such as Tsallis and Blast-Wave fits.
7. Record fit quality, parameter stability, and anomalies.
8. Draft referee-style findings with citations and concrete requests for missing data/tables.

## Evidence Standard

Treat local symbolic and numerical scripts as sanity checks unless they include explicit dimensions, assumptions, data inputs, and reproduced manuscript equation numbers.

The evidence states are defined in `docs/decisions/2026-04-26-science-evidence-standards.md`. The current status for each scientific claim belongs in `evidence-ledger.md`.

## Expected Outputs

- Verified equation notes.
- Assumption ledger for each model variant.
- Reproducible scripts and commands.
- Fit parameter tables.
- chi2/ndf table.
- Covariance and parameter-correlation tables.
- Plots of velocity and temperature versus multiplicity.
- Residual and pull plots per multiplicity bin.
- Literature comparison notes.
- Referee report draft.
