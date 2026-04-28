# Fit Plan

## Inputs Needed

- Full pT data table for all multiplicity bins.
- Measurement uncertainties.
- Bin definitions and fit ranges.
- Exact model equations and parameter constraints.
- Published initial guesses or fitted parameters, if available.
- Normalization convention for each spectrum.
- Collision system, event selection, particle definition, and acceptance cuts.

## Data Acquisition

The fitting pipeline is currently blocked before fit (`fit_run_status.json` reports `pipeline_status = "blocked_before_fit"`) because `ins1419652` only provides inclusive pT spectra with `N(P=3) >= 1`, not spectra conditioned on the manuscript multiplicity intervals. Resolving this requires one of the following:

1. **Primary path (preferred):** Robert provides per-bin pT tables (yields and total uncertainties) for the manuscript multiplicity bins `21-30`, `31-40`, `41-50`, `51-60`, `61-70`, `71-80`, `81-90`, `91-100`, `101-125`, and `126-150` in a fit-ready format.
2. **Alternate path:** Identify an open-data or HEPData record (ATLAS, CMS, ALICE, or ATLAS open data) that contains pT spectra conditioned on the same multiplicity intervals and acceptance as the manuscript.
3. **Synthetic cross-check (not primary evidence):** Use the manuscript's published fit parameters (e.g., Table 1) to generate synthetic spectra for each multiplicity bin for limited cross-checks only. These spectra can be used to validate the fitting machinery and baseline comparisons but must not replace real data in the primary evidence chain.

Until path (1) or (2) is satisfied, no manuscript-bin fits should be treated as physical evidence.

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

- `fit_input.csv`
- `fit_parameters.csv`
- `fit_quality.csv`
- `parameter_correlations.csv`
- `model_comparison.csv`
- residual plots per bin
- pull plots per bin
- U versus multiplicity plot
- temperature versus multiplicity plot
- short interpretation note
