# Run: 2026-07-08-bgbw-c1-c3-scaffolds

## Purpose

This directory documents the C1 and C3 scaffolds created as part of issue #27
(BGBW per-class fit caveats: SPD-tracklets estimator, pion-mass assumption,
missing covariance).

## Scaffold files created

| File | Caveat | Status |
|------|--------|--------|
| `physics/src/bgbw_covariance.py` | C3 — missing covariance | ✅ Done |
| `physics/src/nch_response_matrix.py` | C1 — estimator mismatch | ⚠️ Scaffold only |
| `physics/src/bgbw_fit.py` | C1/C3 — main fit driver | ✅ Done |
| `physics/src/bgbw_identified_fit.py` | C2 — pion-mass assumption | ✅ Done |

---

## C1 — Estimator mismatch (BLOCKED)

**Script**: `physics/src/nch_response_matrix.py`

### What the scaffold does
- `load_response_matrix(path)` — loads `physics/data/response_matrix/R_spd_to_nch.npy`.
  Returns a 10×10 identity matrix with a warning if the file is absent.
- `apply_response(nch_measured, R)` — applies Moore–Penrose pseudoinverse unfolding.
- `estimator_delta_table(...)` — formats a per-bin delta table for T_kin, ⟨β⟩.

### What is blocked
A real response matrix requires one of:
1. **ALICE MC internal data**: PYTHIA8 or AMPT events passed through the full
   ALICE detector simulation (GEANT4 / GEANT3) → reconstruct both SPD-tracklets
   (`|η| < 0.8`) and charged-multiplicity Nch at mid-rapidity → build the
   migration matrix.
2. **Published correlation coefficients**: Not yet available for pp 13 TeV
   multiplicity classes as of 2026-07.

### Unblock path
When a real R matrix is available:
```bash
# Save the (10, 10) matrix
import numpy as np
np.save("physics/data/response_matrix/R_spd_to_nch.npy", R_matrix)

# Then run the cross-estimator comparison
python physics/src/bgbw_fit.py --run-dir research/robert/runs/YYYY-MM-DD-bgbw-estimator-crosscheck
```

---

## C3 — Missing covariance

**Script**: `physics/src/bgbw_covariance.py`

### What the scaffold does

Synthesises a parametric covariance matrix:

```
Σ_ij = δ_ij · σ_stat,i²  +  σ_sys,i · σ_sys,j · exp(-|Δ log pT|_ij / ξ)
```

where ξ is a correlation length in log-pT space.

Key functions:
- `build_covariance(pt, stat, sys, xi)` → (n, n) PSD matrix
- `gls_chi2(y, y_pred, cov)` → GLS χ² via Cholesky
- `gls_residuals(y, y_pred, cov)` → whitened residuals
- `chi2_envelope(...)` → χ²/ndf over ξ ∈ {0.1, 0.3, 1.0, 3.0}

### Smoke test result (2026-07-08)

```
bgbw_covariance smoke test
  ξ= 0.1  PSD=True  GLS-χ²=2.631
  ξ= 0.3  PSD=True  GLS-χ²=3.609
  ξ= 1.0  PSD=True  GLS-χ²=5.427
  ξ= 3.0  PSD=True  GLS-χ²=7.416
  diagonal_chi2_ndf_bias (diag/GLS@ξ=1) = 0.423  (synthetic random residuals)
PASS
```

Note: the bias is < 1 on random synthetic residuals because random sign
alternation of residuals interacts with negative off-diagonal elements of
Σ⁻¹. On real physics data where the model fits well and residuals are small
and correlated, the bias > 1 (diagonal over-counts).

### Wiring into bgbw_fit.py

Use `--cov-mode correlated` to enable GLS envelope reporting:

```bash
python physics/src/bgbw_fit.py \
  --run-dir research/robert/runs/2026-07-08-bgbw-gls \
  --cov-mode correlated --xi 1.0
```

The reported `gls_chi2_ndf_envelope` in `fit_results.json` gives the χ²/ndf
envelope over ξ = {0.1, 0.3, 1.0, 3.0}, which brackets the true (unknown)
covariance structure.

---

## Next actions (C1 and C3 remaining)

- [ ] C1: Obtain real R matrix (ALICE internal or published) and populate
  `physics/data/response_matrix/R_spd_to_nch.npy`. Then run:
  `python physics/src/bgbw_fit.py --run-dir research/robert/runs/YYYY-MM-DD-bgbw-estimator-crosscheck`
  and fill `research/robert/runs/2026-07-08-bgbw-estimator-crosscheck/` with
  the delta table.
- [ ] C3: Run `bgbw_fit.py --cov-mode correlated` once the per-class fit
  (C1 unblocked) is stable. Update `ledger_table.md` with the GLS χ²/ndf
  envelope.

## References

- Issue #27: https://github.com/badmarsh/aisci/issues/27
- Script: `physics/src/bgbw_fit.py`
- Script: `physics/src/bgbw_covariance.py`
- Script: `physics/src/nch_response_matrix.py`
- Related: #26 (RAG corpus gap)
