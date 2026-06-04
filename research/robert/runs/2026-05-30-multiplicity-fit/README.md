# Run: 2026-05-30-multiplicity-fit

**Date:** 2026-05-30  
**Script:** `deployment/helper/run_fit_fast.py`  
**Status:** Completed

## Inputs

| Item | Value |
|---|---|
| Data file | `physics/data/fit_input_ins1735345.csv` |
| HEPData record | `ins1735345` (Table 1, DOI `10.17182/hepdata.91996.v2/t1`) |
| Multiplicity bins | 21-30, 31-40, 41-50, 51-60, 61-70, 71-80, 81-90, 91-100, 101-125, 126-150 |
| pT gate | 120–5000 MeV |
| η acceptance | \|η\| < 0.8 |
| Particle mass | 0.13957 GeV (π±) |
| Points per bin | 39 (after pT gate; rows with missing errors dropped) |

## Models Run

- `manuscript_juttner` (1c, 2c, 3c)
- `exact_bose_einstein` (1c, 2c, 3c)
- `tsallis` (1c, 2c, 3c)
- Blast-wave: **deferred** (numerical cost; see `deployment/helper/run_fit_fast.py`)

## Gate Criteria

- chi2/ndf ≤ 5.0 (max acceptable)
- chi2/ndf ≥ 0.1 (minimum, flags over-fitting)
- Minuit `valid=True`
- EDM < 0.1
- No unconstrained parameters (\|err/val\| < 1.0)
- Accurate covariance matrix

**Gate result:** 8 passed / 90 total (8.9%)

## Key Findings

### 1. Manuscript Jüttner 1-component is ruled out
`manuscript_juttner/1c` chi2/ndf ranges from **29 to 75** across all 10 bins. The single moving thermal Jüttner source cannot describe ALICE pp pion spectra at √s = 7 TeV.

### 2. Manuscript's 2-component Jüttner fails to converge in 9/10 bins
`manuscript_juttner/2c` returns `success=False` with EDM > 0.1 or `valid=False` for every bin except `21-30`. This is the primary model from the manuscript. The numerics are unstable with Minuit.

- Only convergence: bin **21-30**, chi2/ndf = 0.686 (gate: passed) — the lowest-multiplicity, lowest-yield bin.
- All higher bins: Minuit fails to find a minimum (EDM >> 0.1 or `valid=False`).

### 3. Exact Bose-Einstein 1c is between Jüttner and Tsallis
`exact_bose_einstein/1c` chi2/ndf ranges from **16 to 37** — significantly worse than Tsallis 1c but better than Jüttner 1c. Bose-Einstein quantum corrections alone do not close the gap.

### 4. Tsallis is the only 1c model with acceptable chi2/ndf in the lowest bin
- Bin 21-30: Tsallis/1c chi2/ndf = **0.153** ✓
- Bins 31-40 through 91-100: Tsallis/1c chi2/ndf = 3.5–12 (mostly fails gate)
- The pT tail at high multiplicity is not described by a single Tsallis component.

### 5. U₂ instability confirmed at high multiplicity
`exact_bose_einstein/3c` and `manuscript_juttner/3c` consistently show `U_2: |err/val| >> 1.0` (values of 2–486 seen). This confirms the [O-02] concern from `next-actions.md`.

### 6. Tsallis 2c wins by AIC but is over-parameterized
`tsallis/2c` achieves chi2/ndf 0.009–0.039 in most bins — **below the 0.1 lower gate threshold**. Unconstrained norm parameters appear (|err/val| ≈ 1.0). These fits are tracking noise, not physics.

### 7. At high multiplicity, no model fully converges
For bins 71-80, 81-90, 91-100:
- Only 1c models converge reliably
- Best 1c for these bins: `tsallis/1c` with chi2/ndf ≈ 11–12 (poor)
- This is consistent with the manuscript's claim of parameter instability at high multiplicity.

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

1. Robert to confirm whether manuscript's 2c Jüttner convergence failure is expected (known fitting instability) — **this is [O-02] in `next-actions.md`**
2. Investigate `manuscript_juttner/2c` numerics: grid scan over (T, U₁, U₂) initial values to test if any starting point converges
3. Run blast-wave baseline for comparison
4. Report chi2/ndf from this run against manuscript Figs 7-9 values
