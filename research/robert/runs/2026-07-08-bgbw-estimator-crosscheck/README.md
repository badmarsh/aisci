# Run: 2026-07-08-bgbw-estimator-crosscheck

## Status: BLOCKED — C1 open

This directory is the acceptance-criteria run for **C1 (estimator mismatch)**
from issue #27.

## What C1 requires

HEPData ins1735345 uses the **SPD-tracklets estimator** over |η| < 0.8,
which does not match the charged-multiplicity definition used in the
manuscript.  The rising T_kin trend (0.11 → 0.40 GeV across the 10 classes)
is partially an estimator artifact.

To close C1 we need:
1. A cross-estimator dataset (V0M %-class or CL1) for pp 13 TeV with matching
   multiplicity classes.
2. A Nch ↔ SPD-tracklets response matrix R (10×10) from ALICE MC or published
   data.
3. Run `libs/physics-core/src/bgbw_fit.py` against both estimators and produce a delta
   table for T_kin, ⟨β⟩ per bin.

## Scaffold available

`libs/physics-core/src/nch_response_matrix.py` provides:
- Identity-matrix placeholder (zero correction)
- `apply_response(nch_measured, R)` for Moore–Penrose unfolding
- `estimator_delta_table(...)` to format the required delta table

## Unblock path

```bash
# 1. Save real response matrix
import numpy as np
np.save("libs/physics-core/data/response_matrix/R_spd_to_nch.npy", R_matrix)

# 2. Obtain V0M or CL1 dataset from HEPData and save as:
#    libs/physics-core/data/fit_input_ins<ID>_v0m.csv

# 3. Run cross-estimator fit
python libs/physics-core/src/bgbw_fit.py \
  --run-dir research/robert/runs/2026-07-08-bgbw-estimator-crosscheck \
  --data-path libs/physics-core/data/fit_input_ins<ID>_v0m.csv \
  --cov-mode diag

# 4. Compare with SPD-tracklet results from 2026-07-08-bgbw-per-class/
#    and populate this directory with the delta table.
```

## References
- Issue #27: https://github.com/badmarsh/aisci/issues/27
- Script: `libs/physics-core/src/nch_response_matrix.py`
- SPD-tracklet fit: `research/robert/runs/2026-07-08-bgbw-per-class/`
