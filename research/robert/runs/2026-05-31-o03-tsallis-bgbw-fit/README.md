# O-03 Tsallis vs BGBW Fitting Run

**Date:** 2026-05-31
**Status:** IN PROGRESS
**Data:** ins1735345 (ALICE pp 13 TeV, multiplicity bins 21-150)

## Run Configuration

- Input: `physics/data/fit_input_ins1735345.csv`
- Manuscript: `PhD Thesis 2.pdf`
- Models: manuscript_juttner, exact_bose_einstein, tsallis, blast_wave
- Component counts: 1, 2, 3

## Current Status

Fitting pipeline started 2026-05-31. Process is running through all multiplicity bins.
Integration warnings observed for blast_wave model (expected for complex radial integrals).

Partial results generated for bin 101-125:
- Covariance matrices: 3 models × 1 component
- Residuals: 3 models × 1 component

## Next Steps

1. Wait for fitting to complete all 10 multiplicity bins
2. Extract chi²/ndf, best-fit parameters (T, q, U, β_s, n)
3. Compare Tsallis vs BGBW performance
4. Check subluminality constraint (v < c)
5. Record results in evidence-ledger.md

## Blocker

Long computation time - fitting is CPU-intensive for 10 bins × 4 models × 3 component counts.
