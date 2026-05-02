# Evidence Ledger

Use this table as the source of truth for scientific claim status. Do not promote a claim from `Sanity checked` to `Supported` until it is tied to exact manuscript equation/table/figure identifiers, input data, script output, and literature context where relevant.

| Claim | Evidence Required | Current Evidence | Status | Next Gate |
|---|---|---|---|---|
| The main exponential form is Lorentz-covariant | Exact manuscript equation, metric convention, four-velocity definition, and invariant measure handling | `boson_paper_analysis.py` checks `U.p = E cosh(Y) - pz sinh(Y)` and the massless `pT cosh(eta-Y)` identity | Sanity checked | Link to final equation numbers and verify finite-mass/invariant-measure factors |
| The manuscript uses a full Bose-Einstein distribution, not only a Boltzmann/Juttner approximation | Final formula showing either `1/(exp(beta U.p)-1)` or an explicit approximation statement | `research/robert/runs/2026-04-27-baseline-fit/formula_confirmation.json` records `formula_classification`: `juttner_relativistic_boltzmann_exponential` with `f(p) ~ delta(p^2-m^2) Theta(p0) exp(-beta U.p)` and no detected Bose-Einstein denominator | Confirmed approximation: Juttner/Boltzmann exponential — Bose-Einstein denominator not present in retrieved text | Locate or confirm absence in final numbered equation; require explicit approximation statement in manuscript |
| Static limit recovers the expected thermal/Cooper-Frye behavior | Exact eta-cut formula, normalization, Jacobian, and U -> 0 limit | Local symbolic check supports the U -> 0 integrand under current assumptions. Manuscript does not explicitly name Cooper-Frye or explicitly state the U->0 limit; the recovery is implicit. | Sanity checked | Re-run against numbered manuscript equations and finite acceptance limits |
| Massless/pseudorapidity assumptions are valid for the fitted pT range | Particle species, mass treatment, pT range, low-pT exclusion, and sensitivity scan | `research/robert/runs/2026-04-27-baseline-fit/hepdata_mapping_validation.json` shows `ins1419652` does not provide fit-ready manuscript-bin spectra, so no fit-range sensitivity scan could be run yet | Blocked | Get a matched per-bin source table or Robert-provided fit input, then run the fit-range sensitivity scan |
| High-multiplicity bins are poorly constrained | Full pT table, uncertainties, fit model, covariance, correlations, optimizer status, and residuals | Reported parameter uncertainties are much larger than fitted values in retrieved chunks | Suggestive | Refit all bins with covariance and initial-value scans |
| Three-component fit (two moving + one static system) is over-parameterized at high multiplicity | Full pT table, uncertainties, fit model, covariance, correlations, optimizer status, and residuals | Current evidence suggests degeneracy but does not prove root cause; manuscript treats this three-component interpretation as its primary baseline | Suggestive | Stress-test the manuscript's three-component baseline against one- and two-component variants with chi2/ndf, AIC/BIC, and parameter correlations |
| chi2/ndf is missing or insufficiently reported | Manuscript tables/figures and full fit outputs | Figures 7-9 contain explicit χ²/ndf values in their legends for all multiplicity bins, but they are omitted from Table 1. | Sanity checked | Compute independent chi2/ndf to verify the reported values |
| Tsallis/Tsallis-Pareto and Blast-Wave baselines are needed | Literature-matched baseline formulas and comparable pp/p-Pb/AA references | Literature comparison not yet complete; `physics/src/tsallis_physics_validation.py` exists but its outputs are not yet captured as run artifacts | Open | Run the Tsallis validation script into a dated run directory and add at least one baseline comparison entry here |
| Bíró/Paić/Serkin two-component soft/hard baseline matches our model decomposition | DOI 10.48550/arxiv.2510.09692; ALICE pp 2.76–13 TeV pT decomposition; figure-level chi2/ndf and shape parameter comparison against our 3-component fit | **Scite check 2026-04-30**: arXiv Oct 2025 (pre-journal); Scite tally = 0 incoming Smart Citations (paper too recent; `contentDenied` = full text not indexed). Abstract-confirmed claims: (1) Boltzmann fit describes soft component at √s = 2.76, 5.02, 13 TeV ALICE pp; (2) residual hard spectra show **no evolution in shape or peak position with multiplicity**; (3) mean pT for both soft and hard components **remains nearly constant across multiplicity classes**; (4) Pythia 8 MC confirms both trends; (5) authors explicitly frame result as "robust alternative to hydrodynamical interpretations". Third author confirmed: Leonid Serkin. Paper cites Trainor TCM lineage and supports `10.1016/j.physletb.2024.138937` in its methods section. | Sanity checked | (1) Obtain digitised figure data (Figs. 2–4) for direct shape comparison; (2) compute chi2/ndf of Boltzmann soft fit vs our Jüttner soft component per multiplicity bin; (3) check whether their multiplicity-independence result survives at the highest bins (101–125, 126–150) where our fit shows largest parameter uncertainties |
| BGBW freeze-out temperature and flow velocity in ALICE pp multiplicity classes | DOI 10.1140/epja/i2019-12669-6 (Khuntia+2019) and DOI 10.1088/1361-6471/ab783b (Rath+2020) | Literature retrieved via Scite 2026-04-29 | Open | Run BGBW baseline fit against same multiplicity classes; record T_kin and β per class |
| Boltzmann/Jüttner approximation is valid for pT > 120 MeV at LHC temperatures | Literature consensus; DOI 10.3390/universe9020111 (Gupta+2023) | Explicit statement: "B-E and F-D tend to Maxwell-Boltzmann at high T" | Sanity checked | Document low-pT gate applied; add sensitivity scan for pT 120–300 MeV bin |

---

## Next Actions

### Now (Blockers)

1. **Juttner approximation — manuscript anchor**: Tie `formula_classification: juttner_relativistic_boltzmann_exponential` from `runs/2026-04-27-baseline-fit/formula_confirmation.json` to a stable page/equation identifier in the manuscript export. Add explicit approximation statement to manuscript text.
2. **Fit-ready data table**: Obtain per-bin pT spectra matching multiplicity bins `21-30, 31-40, 41-50, 51-60, 61-70, 71-80, 81-90, 91-100, 101-125, 126-150`. `hepdata_mapping_validation.json` confirms `ins1419652` only provides inclusive spectra. Save to `physics/data/` as CSV per `research/robert/archive/data-onboarding.md` format spec.
3. **Run fitting pipeline**: After `fit_input.csv` exists, re-run `physics/src/fitting_pipeline.py`. Separate acceptance-cut formulas (η, pT, combined), apply region-specific low-pT gates from Figure 5. Emit chi2/ndf, covariance, parameter correlations, residuals, and model-comparison tables as run artifacts.
4. **Use physics_env**: Use the existing virtual environment in `physics/physics_env` which already has `matplotlib` 3.10.9 installed; this unblocks the emission of residual and pull plots.
5. **Trend plots**: Generate U vs multiplicity and T vs multiplicity only after fit quality gates pass.
6. **Literature ingestion**: Ingest Tsallis/Blast-Wave comparison papers into Onyx physics persona. Run `physics/src/tsallis_physics_validation.py` and save outputs as a dated run directory.

### Next

1. ~~Run Scite/Consensus/arXiv/INSPIRE/HEPData citation checks and log outcomes in a new run artifact.~~ **Partial — done 2026-04-30**: Bíró/Paić/Serkin (`10.48550/arxiv.2510.09692`) Scite check complete; ledger row updated to `Sanity checked`. Remaining: BGBW baseline papers (Khuntia+2019, Rath+2020), Tsallis baseline DOIs, and full HEPData/INSPIRE pass still outstanding.
2. Generate first full referee-style report using `research/robert/referee-report-draft.md` as the template.
3. Evaluate Onyx RAG retrieval against the physics question set; record citation hits, misses, and source-coverage gaps.

### Nice To Have

1. Automated LaTeX equation extraction from manuscript PDFs.
2. Reproducible paper-to-report pipeline through DeerFlow.
3. Visual RAG for figures and captions (requires `qwen2.5-vl` in Ollama).
4. Dashboard summarizing fit quality and anomalous bins per multiplicity class.
