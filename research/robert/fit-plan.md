# Fit Plan

## Inputs Needed

- Full pT data table for all multiplicity bins.
- Measurement uncertainties.
- Bin definitions and fit ranges.
- Exact model equations and parameter constraints.
- Published initial guesses or fitted parameters, if available.
- Normalization convention for each spectrum.
- Collision system, event selection, particle definition, and acceptance cuts.

## Fitting Stance

Do not treat fit convergence as physical evidence by itself. A parameter trend is interpretable only if the fit quality, covariance, correlations, and sensitivity to fit range and initial values are acceptable.

## Pipeline

1. Load data into a canonical table.
2. Implement manuscript model variants as pure Python functions with explicit assumptions.
3. Implement literature-matched Tsallis/Tsallis-Pareto and Blast-Wave baselines.
4. Fit each bin with `iminuit` or equivalent robust optimizer.
5. Compute chi2, ndf, chi2/ndf, covariance, parameter correlations, and Minuit status.
6. Scan initial values and parameter bounds to detect local minima and unconstrained directions.
7. Compare one-, two-, and three-component variants using residuals and information criteria where appropriate.
8. Plot fitted curves, residuals, and pulls.
9. Plot parameter trends versus multiplicity only after fit quality gates pass.
10. Compare baseline and manuscript models in a single table.

## Outputs

- `fit_parameters.csv`
- `fit_quality.csv`
- `parameter_correlations.csv`
- `model_comparison.csv`
- residual plots per bin
- pull plots per bin
- U versus multiplicity plot
- temperature versus multiplicity plot
- short interpretation note
