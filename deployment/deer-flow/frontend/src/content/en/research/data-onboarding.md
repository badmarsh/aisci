# Data Onboarding Guide: $p_T$ Spectra

This guide explains how to provide the required $p_T$ data tables for the "Boson probability function" validation.

## 🔴 Current Blocker
The scientific analysis is currently blocked by the need for full $p_T$ data tables matching the manuscript multiplicity bins:
`21-30, 31-40, 41-50, 51-60, 61-70, 71-80, 81-90, 91-100, 101-125, 126-150`.

## 📥 Where to Put Data
Save all new data files in: `physics/data/`

## 📄 Expected Format (CSV Preferred)
To ensure the `fitting_pipeline.py` can read your data automatically, please use the following CSV structure:

| bin_id | multiplicity_range | pt_center | cross_section | stat_err | syst_err |
|---|---|---|---|---|---|
| 21-30 | 21-30 | 0.15 | 1.23e-01 | 0.01e-01 | 0.05e-01 |
| ... | ... | ... | ... | ... | ... |

*Note: If data is in a different format (JSON, Excel, or raw text), please save it to `physics/data/raw/` and add a note in `research/robert/next-actions.md`.*

## ⚙️ How to Validate the Upload
After saving the file, you can run the data loader test to ensure the system recognizes the new bins:

```bash
cd physics
python3 src/data_loader.py --verify data/your_filename.csv
```

## ✅ Next Steps After Upload
Once the data is verified, the following tasks will be unblocked:
1. Chi-squared ($ \chi^2/ndf $) computation.
2. Parameter covariance and correlation analysis.
3. Temperature ($T$) vs. Multiplicity trend plotting.
