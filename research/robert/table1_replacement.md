# Validation Tables (Manuscript Table 1 Cross-Check)

This document provides independent validation values for cross-checking against manuscript Table 1. It replaces or supplements the original table with independently computed χ²/ndf values for multiple models and parameter extracts from the BGBW baseline, ensuring transparency regarding fit quality and parameter degeneracy.

### Chi²/ndf Table

| Bin     | MJ 1c  | MJ 2c  | BE 1c  | BE 2c  | TS 1c  | TS 2c | BW 1c  |
|---------|-------:|-------:|-------:|-------:|-------:|------:|-------:|
| 21-30   | 67.1   | 18.1   | 63.7   | 16.5   | **0.59** | **0.36** | 18.9 |
| 31-40   | 160.4  | 46.4   | 147.4  | 41.4   | 6.57   | **1.03** | 28.8 |
| 41-50   | 157.8  | 46.1   | 142.7  | 40.8   | 9.11   | **1.34** | 25.5 |
| 51-60   | 155.0  | 45.4   | 138.7  | 40.1   | 10.6   | **1.43** | 24.1 |
| 61-70   | 218.5  | 61.3   | 193.5  | 54.1   | 18.4   | 19.8  | 29.8 |
| 71-80   | 211.7  | 57.4   | 186.0  | 50.5   | 19.2   | **2.05** | 26.4 |
| 81-90   | 198.6  | 51.1   | 172.6  | 44.9   | 19.4   | 20.8  | 21.7 |
| 91-100  | 184.3  | —      | 158.3  | —      | 19.6   | —     | —    |
| 101-125 | 169.7  | 37.8   | 144.4  | 33.1   | 19.2   | **1.37** | 12.9 |
| 126-150 | 103.4  | 17.7   | 85.6   | 15.7   | 12.3   | **0.45** | 5.3 |

### AIC/BIC Model Comparison (ΔAIC relative to best model per bin)

> Source: evidence-ledger.md, section "AIC/BIC Model Comparison (Task 8, 2026-06-20)"
> Lower ΔAIC = better. **Bold** = winner per bin.
> n_pts = 47; n_params: 1c = 3 (MJ/BE/TS) or 4 (BW); 2c = 6 (MJ/BE/TS)

| Bin     | MJ 1c | BE 1c | TS 1c  | TS 2c  | BW 1c |
|---------|------:|------:|-------:|-------:|------:|
| 21-30   | 2930  | 2784  | 5      | **0**  | 795   |
| 31-40   | 7008  | 6439  | 241    | **0**  | 1194  |
| 41-50   | 6881  | 6218  | 340    | **0**  | 1036  |
| 51-60   | 6755  | 6039  | 403    | **0**  | 972   |
| 61-70   | 8802  | 7705  | **0**  | 6      | 471   |
| 71-80   | 9225  | 8093  | 754    | **0**  | 1047  |
| 81-90   | 7886  | 6741  | **0**  | 6      | 83    |
| 91-100  | 7246  | 6104  | **0**  | —      | —     |
| 101-125 | 7404  | 6291  | 784    | **0**  | 496   |
| 126-150 | 4526  | 3741  | 517    | **0**  | 207   |

**Overall winner: Tsallis 2c in 7/10 bins; Tsallis 1c in 3 bins (61-70, 81-90, 91-100).**
**ΔAIC(TS2c vs BW1c): TS2c beats BW1c by 83–1194 units across all bins where both present.**
**BIC confirms same winner in all 10 bins.**
⚠️ Tsallis 2c AIC/BIC win does NOT imply physical correctness — see chi²/ndf table and
C1/C2/C3 caveats above. Covariance inspection and parameter stability are required before
physical interpretation.

### BGBW Per-Class Fit Parameters

> ⚠️ **Caveats**: All values below carry three interlocking caveats (C1/C2/C3) and must not be physically interpreted until these are resolved.

| Bin | T_kin [GeV] | ⟨β⟩ | χ²/ndf (diag) | C1 note | C2 note |
|-----|-------------|------|----------------|---------|---------|
| 21-30   | 0.1260 | 0.312 | 18.92 | SPD-tracklets | pion mass |
| 31-40   | 0.1479 | 0.314 | 28.84 | SPD-tracklets | pion mass |
| 41-50   | 0.1606 | 0.315 | 25.46 | SPD-tracklets | pion mass |
| 51-60   | 0.1694 | 0.316 | 24.07 | SPD-tracklets | pion mass |
| 61-70   | 0.1544 | 0.383 | 29.75 | SPD-tracklets | pion mass |
| 71-80   | 0.1457 | 0.426 | 26.39 | SPD-tracklets | pion mass |
| 81-90   | 0.1281 | 0.491 | 21.68 | SPD-tracklets | pion mass |
| 91-100  | 0.1074 | 0.561 | 16.67 | SPD-tracklets | pion mass |
| 101-125 | 0.0973 | 0.600 | 12.94 | SPD-tracklets | pion mass |
| 126-150 | 0.0952 | 0.624 |  5.34 | SPD-tracklets | pion mass |

---
Source: evidence-ledger.md, runs/2026-06-20-phd-level-fits/ and runs/2026-07-08-bgbw-per-class/. Do not edit here — update the ledger first, then regenerate this file.