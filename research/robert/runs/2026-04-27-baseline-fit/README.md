# Baseline Fit Run - 2026-04-27

## Objective

Validate whether HEPData record `ins1419652` provides fit-ready `pT` spectra for the manuscript multiplicity bins, confirm the manuscript formula variant from the local PDF, and run the Stage 3 baseline fitting pipeline only if the source mapping passes.

## Commands Run

```bash
cd /home/ubuntu/aisci
python3 physics/src/data_loader.py --run-dir research/robert/runs/2026-04-27-baseline-fit
python3 physics/src/fitting_pipeline.py --run-dir research/robert/runs/2026-04-27-baseline-fit --pdf-path 'research/robert/manuscript/boson-probability-function-moving-system.pdf'
```

## Formula Confirmation

- `formula_confirmation.json` classifies the manuscript formula as `juttner_relativistic_boltzmann_exponential`.
- The run now records exact manuscript page anchors: page `1` for the covariant exponential formula text and page `10` for `Table 1` with the fitted multiplicity bins and parameters.
- Evidence lines come from the local manuscript PDF text, including `f (p) ~ delta(p^2 - m^2) Theta(p0) exp(-beta U^mu p_mu)`.
- No Bose-Einstein denominator was detected in the extracted manuscript text used for this run.

## HEPData Validation Result

- `hepdata_table_index.csv` indexes all 18 tables in `ins1419652`.
- `hepdata_pt_spectra.csv` contains the canonical extracted `pT` rows for Tables `4`, `8`, `12`, and `16`, including `pT` bin edges, observed yields, `stat`, `sys`, and quadrature-summed `total_error`.
- `hepdata_mapping_validation.json` shows that every available `pT` spectrum table is inclusive with qualifier `N(P=3) >= 1`.
- The manuscript multiplicity intervals `21-30`, `31-40`, `41-50`, `51-60`, `61-70`, `71-80`, `81-90`, `91-100`, `101-125`, and `126-150` do not appear as `pT`-spectrum qualifiers in `ins1419652`.
- Multiplicity tables exist, but they are event-count distributions, not conditional `pT` spectra for those bins.

## Additional Source Audit

The following public and repo-local source paths were checked after the initial `ins1419652` gate failed:

1. Local manuscript PDF and repo-local materials
   - `research/robert/manuscript/boson-probability-function-moving-system.pdf`
   - repo-wide searches for `track_p`, manuscript multiplicity-bin labels, and additional local PDFs/extracted materials
   - Result: no repo-local fit-ready source table or extracted per-bin histogram data beyond the existing run artifacts

2. ATLAS conference-note public page and CDS record
   - ATLAS public page: `https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/CONFNOTES/ATLAS-CONF-2015-028/`
   - CDS record `2037701`: `https://cds.cern.ch/record/2037701?ln=en`
   - CDS files page: `https://cds.cern.ch/record/2037701/files?ln=en`
   - Result: public material exposes the note PDF and figure assets only; no downloadable table package, histogram file, or auxiliary data file containing per-bin `track_p` spectra

3. Published ATLAS paper pages and CDS record
   - ATLAS paper page: `https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/STDM-2015-02/`
   - CDS record `2128621`: `https://cds.cern.ch/record/2128621?ln=en`
   - CDS plots page: `https://cds.cern.ch/record/2128621/plots?ln=en`
   - CDS files page: `https://cds.cern.ch/record/2128621/files?ln=en`
   - Result: the published-paper CDS record exposes only PDFs; the `ATLPUB_SOURCEF` entry is another PDF (`MinBias13TeV-stdm-2015-02.pdf`), not a source tarball or data archive; the ATLAS paper page exposes page tables plus figure/auxiliary figure assets, not fit-ready histogram tables

4. Current 13 TeV HEPData record and linked resources
   - HEPData `ins1419652` / `10.17182/hepdata.72491`: `https://www.hepdata.net/record/ins1419652`
   - INSPIRE literature record `1419652`: `https://inspirehep.net/literature/1419652`
   - Result: only corrected `pseudorapidity`, inclusive `pT`, multiplicity-distribution, and `<pT>(n_ch)` tables are present; INSPIRE adds PDF/figure links and a Rivet reference, but no separate public attachment with manuscript-bin momentum histograms

5. Public Rivet reference-data packages linked to the ATLAS records
   - Rivet project default branch: `release-4-1-x`
   - `ATLAS_2016_I1419652.plot`: `https://gitlab.com/hepcedar/rivet/-/blob/release-4-1-x/analyses/pluginATLAS/ATLAS_2016_I1419652.plot`
   - `ATLAS_2016_I1419652.info`: `https://gitlab.com/hepcedar/rivet/-/blob/release-4-1-x/analyses/pluginATLAS/ATLAS_2016_I1419652.info`
   - `ATLAS_2016_I1419652.yoda.gz`: `https://gitlab.com/hepcedar/rivet/-/blob/release-4-1-x/analyses/pluginATLAS/ATLAS_2016_I1419652.yoda.gz`
   - Related analysis packages checked:
     - `ATLAS_2016_I1426695` on `release-4-1-x`
     - `ATLAS_2016_I1467230` on `release-4-1-x`
   - Result: the public Rivet package for `ins1419652` exposes `16` reference objects whose plot metadata are limited to charged-particle `pT`, `eta`, multiplicity, and `<pT>(n_ch)` observables; no `track_p` object, no momentum-`p` histogram, and no manuscript multiplicity-bin labels were found. The related `ATLAS_2016_I1426695` and `ATLAS_2016_I1467230` packages likewise expose only `pT`, `eta`, multiplicity, and `<pT>(n_ch)` style observables, even where high-multiplicity selections such as `n_ch >= 6`, `>= 20`, and `>= 50` appear.

6. Related ATLAS charged-particle HEPData records
   - Low-`pT` 13 TeV ATLAS record `ins1467230` / `10.17182/hepdata.73907.v2`: `https://www.hepdata.net/record/ins1467230`
   - Corresponding ATLAS page: `https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/STDM-2015-17/`
   - 8 TeV ATLAS record `ins1426695` / `10.17182/hepdata.73012.v1`: `https://www.hepdata.net/record/ins1426695`
   - Corresponding ATLAS page: `https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/STDM-2014-19/`
   - Result: these related records still expose only `pT`, `eta`, multiplicity, and `<pT>(n_ch)` style observables, even where high-multiplicity final states are discussed; no public `track_p` momentum-histogram tables matching manuscript bins were found

7. Journal article pages for related ATLAS charged-particle papers
   - `https://link.springer.com/article/10.1140/epjc/s10052-016-4335-y`
   - `https://link.springer.com/article/10.1140/epjc/s10052-016-4203-9`
   - Result: no supplementary/source-data links or HEPData links were surfaced by direct HTML inspection

## Variable Check: `p` Versus `pT`

- The manuscript source path is genuinely a momentum-`p` fit, not a `pT` fit.
- Local PDF text extraction shows the derived probability function is written as `f(p)` after applying `pT` and `|eta|` cuts.
- The fit figures are labeled `track_p` with x-axis `p [GeV]`, and `Table 1` is explicitly titled as results of the momentum-distribution fits.
- Therefore the mismatch with ATLAS public `pT` tables is a real data-model mismatch, not a naming ambiguity that can be repaired by relabeling `pT` as `p`.

## Status

Blocked before fitting.

The pipeline intentionally did not create `fit_input.csv`, `fit_parameters.csv`, `fit_quality.csv`, covariance matrices, parameter-correlation matrices, residual CSVs, or residual plots because the data-readiness gate failed.

## Blocking Conditions

1. `ins1419652` exposes only inclusive `pT` spectra with `N(P=3) >= 1`, not spectra split by the manuscript multiplicity bins.
2. The manuscript fit target is the momentum variable `p` with `pT` and `|eta|` cuts applied, while all checked public ATLAS tables expose corrected `pT`, `eta`, multiplicity, or `<pT>(n_ch)` observables instead of per-bin momentum histograms.
3. No public fit-ready table was found for the manuscript multiplicity bins `21-30` through `126-150`, and no public attachment containing `track_p` histograms for those bins was found in the checked ATLAS/CDS/INSPIRE/HEPData/Rivet/journal paths.
4. `matplotlib` is not installed in the current environment, so plot generation would still need a dependency fix after the source-table blocker is resolved.

## Artifacts Produced

- `hepdata_record_ins1419652.json`
- `hepdata_table_index.csv`
- `hepdata_pt_spectra.csv`
- `hepdata_mapping_validation.json`
- `hepdata_extraction_summary.json`
- `formula_confirmation.json`
- `model_catalog.json`
- `fit_run_status.json`

## Secondary Audit Confirmation

An independent automated audit of the listed sources confirms the following blockers:
- A repo-local search yielded no unindexed per-multiplicity-bin `track_p` data (no supplementary `.csv`, `.json`, `.txt`, or data archive).
- The `p` vs `pT` mismatch is a genuine physical variable mismatch. The manuscript fits the total momentum variable $p$ derived after $p_{\mathrm{T}}$ and $|\eta|$ cuts. Public ATLAS tables provide only transverse momentum $p_{\mathrm{T}}$.
- The CDS pages for `2128621` and `2037701` were directly queried. They serve exclusively PDF artifacts (`arXiv:1602.01633.pdf`, `plb-758-067.pdf`, `scoap3-fulltext.pdf`, `MinBias13TeV-stdm-2015-02.pdf`, `ATLAS-CONF-2015-028.pdf`) and no `.root`, `.csv`, `.tar`, or `.zip` data archives.
- The public Rivet reference package `ATLAS_2016_I1419652` on `release-4-1-x` exposes only `eta`, inclusive `p_{\mathrm{T}}`, multiplicity, and `<p_{\mathrm{T}}>(N_{\mathrm{ch}})` objects; related Rivet packages `ATLAS_2016_I1426695` and `ATLAS_2016_I1467230` show the same observable family and no `track_p` momentum histogram.
- The Stage 3 pipeline remains correctly blocked pending provision of the fit-ready `track_p` histogram table for bins `21-30` through `126-150`.
