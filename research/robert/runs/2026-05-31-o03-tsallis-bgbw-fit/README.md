# O-03 Tsallis vs BGBW Fitting Run

**Date:** 2026-05-31 (Completed 2026-06-14)
**Status:** COMPLETED
**Data:** ins1735345 (ALICE pp 13 TeV, multiplicity bins 21-150)

## Run Configuration

- Input: `libs/physics-core/data/fit_input.csv` (using `fit_input_ins1735345.csv`)
- Models: `blast_wave`, `tsallis`, `manuscript_juttner`
- Component counts: 1, 2, 3

## Key Findings

1. **Blast-Wave Baseline Validated**: `blast_wave/1c` successfully passed the validation gates ($\chi^2$/ndf $\approx 1.1 - 2.0$) across multiple bins, confirming its status as a robust physical baseline.
2. **Jüttner Convergence Failure**: The primary manuscript model (`manuscript_juttner/2c`) consistently failed to converge across higher multiplicity bins, achieving a valid minimum only in the lowest multiplicity bin (`21-30`).
3. **Over-parameterization of 3c Models**: All 3-component models (`blast_wave/3c`, `tsallis/3c`, `manuscript_juttner/3c`) exhibited extremely small $\chi^2$/ndf values ($< 0.1$) accompanied by optimizer failures, clearly demonstrating over-parameterization and tracking of statistical noise rather than underlying physics.

## Outputs

| File | Description |
|---|---|
| `fit_quality.csv` | chi2, ndf, chi2/ndf, AIC, BIC, gate verdicts for all 90 fits |
| `model_comparison.csv` | Ranked successful fits per bin (by AIC) |
| `fit_parameters.csv` | All parameter values and errors |
| `parameter_correlations.csv` | Full correlation matrices |
| `covariance/` | Per-fit covariance matrices |
| `diagnostics/` | Residual CSVs and fit plots for successful fits |
| `fit_run_status.json` | Machine-readable run summary |

## Next Steps

1. Promote these findings to `evidence-ledger.md` (Completed).
2. Use the `model_comparison.csv` metrics for the final thesis chapter comparing the phenomenological fits.
