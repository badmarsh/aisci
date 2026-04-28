# Robert Next Actions

## Now

1. Confirm and document the manuscript's use of a Juttner/relativistic Boltzmann exponential rather than a full Bose-Einstein form by tying the `juttner_relativistic_boltzmann_exponential` classification from `research/robert/runs/2026-04-27-baseline-fit/fit_run_status.json` and `formula_confirmation.json` to a stable page/equation identifier in the manuscript export, and adding an explicit approximation statement to the manuscript text.
2. Get a fit-ready source table matching the manuscript multiplicity bins `21-30`, `31-40`, `41-50`, `51-60`, `61-70`, `71-80`, `81-90`, `91-100`, `101-125`, and `126-150`; `research/robert/runs/2026-04-27-baseline-fit/hepdata_mapping_validation.json` shows `ins1419652` only provides inclusive `pT` spectra with `N(P=3) >= 1`.
3. Re-run `physics/src/fitting_pipeline.py` after `fit_input.csv` exists, then compute chi2/ndf, covariance, parameter correlations, residuals, and model-comparison tables.
4. Install a plotting backend such as `matplotlib` before the first fit-ready rerun so residual and pull plots can be emitted with the rest of the run artifacts.
5. Create U versus multiplicity and temperature versus multiplicity plots only after fit quality gates pass.
6. Ingest and attach validation-method and literature-matched HEP baseline sources to the Onyx physics personas.

## Next

1. Ingest literature-matched Tsallis/Tsallis-Pareto and Blast-Wave comparison papers.
2. Run the drafted Onyx retrieval evaluation set in `docs/ops/onyx-rag-optimization-2026-04-27.md` and record observed citations, misses, and source-coverage gaps before tuning.
3. Run Scite/Consensus/arXiv/INSPIRE/HEPData checks in the literature workflow and record citation/source outcomes; the Onyx tools are attached, but the checks are not yet logged.
4. Generate the first full referee-style report.

## Nice To Have

1. Automated LaTeX equation extraction.
2. Reproducible paper-to-report pipeline through DeerFlow.
3. Visual RAG checks for figures and captions.
4. A small dashboard summarizing fit quality and anomalous bins.
