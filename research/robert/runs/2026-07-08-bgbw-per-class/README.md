# Run: 2026-07-08-bgbw-per-class

## Summary

BGBW per-multiplicity-class fit against HEPData ins1735345 (ALICE pp 13 TeV,
SPD-tracklets estimator, |η| < 0.8, 10 manuscript multiplicity classes).

**Status: Substitute-baseline** — three interlocking caveats (C1/C2/C3) apply.
See issue #27: https://github.com/badmarsh/aisci/issues/27

## Input

- Data: `physics/data/fit_input_ins1735345.csv` (470 rows, 10 bins × 47 pT points)
- Script: `physics/src/bgbw_fit.py --cov-mode diag`
- Model: BGBW / SSH 1993 (nucl-th/9307020)
- Mass assumption: m = m_π = 0.13957 GeV (C2 caveat — see below)
- Estimator: SPD-tracklets (C1 caveat — see below)

## Results

| Bin | T_kin [GeV] | ⟨β⟩ | χ²/ndf | Minuit valid? |
|-----|-------------|------|--------|---------------|
| 21-30   | 0.1260 | 0.312 | 18.92 | ✓ |
| 31-40   | 0.1479 | 0.314 | 28.84 | ✓ |
| 41-50   | 0.1606 | 0.315 | 25.46 | ✓ |
| 51-60   | 0.1694 | 0.316 | 24.07 | ✓ |
| 61-70   | 0.1544 | 0.383 | 29.75 | ✓ |
| 71-80   | 0.1457 | 0.426 | 26.39 | ✓ |
| 81-90   | 0.1281 | 0.491 | 21.68 | ✓ |
| 91-100  | 0.1074 | 0.561 | 16.67 | ✓ |
| 101-125 | 0.0973 | 0.600 | 12.94 | ✗ |
| 126-150 | 0.0952 | 0.624 |  5.34 | ✗ |

8/10 bins: Minuit `valid=True`.
101-125, 126-150: Minuit did not certify convergence — consistent with the
T–β degeneracy (|ρ| > 0.99) documented in `2026-06-20-phd-level-fits/`.

## Numerical note

The fix applied by the parallel agent replaced `i0(x)·k1(y)` with the
exponentially scaled forms `i0e(x)·k1e(y)·exp(x−y)` (scipy), preventing
overflow in the Bessel function arguments at large pT or high flow velocity.

## Artifacts

- `fit_results.csv` — per-bin fit parameters and quality flags
- `fit_results.json` — full summary with caveat metadata
- `fit_bin_<bin>.png` — 2-panel diagnostic (data+fit, pulls) per converged bin

## Caveats

### C1 — Estimator mismatch (OPEN — blocked)
ins1735345 uses the SPD-tracklets estimator over |η| < 0.8, not the
charged-multiplicity Nch used in the manuscript. The non-monotonic T_kin
trend (peaks at 0.169 GeV in bin 51-60 rather than monotonically decreasing
as in Khuntia+2019) is plausibly an estimator artifact.

**Action required:** `research/robert/runs/2026-07-08-bgbw-estimator-crosscheck/`
(blocked until real response matrix or V0M dataset available).

### C2 — Pion-mass assumption (PARTIAL)
`bgbw_fit.py` fits unidentified charged hadrons with m = m_π = 0.13957 GeV.
K/p contributions at high pT are under-weighted → T_kin biased low, ⟨β⟩ biased high.
The observed ⟨β⟩ = 0.31–0.62 likely overestimates the true flow by ~10–20%.

**Partial mitigation:** `research/robert/runs/2026-07-08-bgbw-identified-species/`
contains a mass-weighted bias estimate (level-2 fallback). Full resolution
requires ins1682316 (ALICE pp 7 TeV π/K/p identified spectra).

### C3 — Missing covariance (PARTIAL — GLS scaffold done)
ins1735345 publishes stat + sys added in quadrature per pT bin. No full
covariance matrix is available. The χ²/ndf values (5–30) use diagonal
weighting only and are **shape-quality proxies**, not confidence-interval
drivers.

**GLS wiring done:** Run `--cov-mode correlated` in `bgbw_fit.py` to obtain
the GLS χ²/ndf envelope over ξ ∈ {0.1, 0.3, 1.0, 3.0}.

## References

- Issue #27: https://github.com/badmarsh/aisci/issues/27
- Script: `physics/src/bgbw_fit.py`
- Covariance scaffold: `physics/src/bgbw_covariance.py`
- Response matrix scaffold: `physics/src/nch_response_matrix.py`
- Identified species: `physics/src/bgbw_identified_fit.py`
- Evidence ledger: `research/robert/evidence-ledger.md` (§ 2026-07-08 BGBW Per-Class Fits)
- BGBW literature: Schnedermann, Sollfrank, Heinz (1993) nucl-th/9307020
- Multiplicity dependence: Khuntia+ 2019 (arXiv:1808.02383)
- HEPData source: doi:10.17182/hepdata.91996.v2
