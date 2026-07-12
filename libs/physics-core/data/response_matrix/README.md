# Response Matrix Directory

This directory holds the Nch ↔ SPD-tracklets migration/response matrices
used by `libs/physics-core/src/nch_response_matrix.py`.

## Status: BLOCKED

`R_spd_to_nch.npy` is not yet populated.  See issue #27 C1 and
`research/robert/runs/2026-07-08-bgbw-estimator-crosscheck/README.md`
for the unblock path.

## Expected file

- `R_spd_to_nch.npy` — (10, 10) float64 numpy array.
  Row i = SPD-tracklet class, column j = true Nch class.
  R_ij = P(measured SPD class i | true Nch class j).

## How to generate (MC path)

1. Generate pp 13 TeV events with PYTHIA8
2. Run through GEANT4 ALICE detector simulation
3. Apply SPD-tracklet reconstruction and Nch counting
4. Fill 2D histogram: x-axis = Nch class, y-axis = SPD-tracklet class
5. Normalise columns to unit sum → R matrix
6. Save: `np.save("R_spd_to_nch.npy", R)`
