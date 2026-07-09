import os
from pathlib import Path
import pandas as pd
from scipy.stats import kstest
import numpy as np

def main():
    base_dir = Path("research/robert/runs/2026-06-20-phd-level-fits")
    diag_dir = base_dir / "diagnostics"
    
    if not diag_dir.exists():
        print(f"Directory {diag_dir} does not exist.")
        return

    results = []
    
    for csv_file in diag_dir.glob("*_residuals.csv"):
        # Format: bin__model__n_comp_residuals.csv
        # e.g., 21-30__blast_wave__1c_residuals.csv
        name_parts = csv_file.stem.replace("_residuals", "").split("__")
        if len(name_parts) >= 3:
            bin_label, model, n_comp = name_parts[0], name_parts[1], name_parts[2]
        else:
            continue
            
        df = pd.read_csv(csv_file)
        if "pull" not in df.columns:
            continue
            
        pulls = df["pull"].dropna().to_numpy()
        if len(pulls) == 0:
            continue
            
        mean_pull = np.mean(pulls)
        rms_pull = np.sqrt(np.mean(pulls**2))
        
        # ks test against standard normal
        ks_stat, ks_pvalue = kstest(pulls, 'norm')
        
        well_specified = abs(mean_pull) < 0.5 and ks_pvalue > 0.05
        
        results.append({
            "bin": bin_label,
            "model": model,
            "n_comp": n_comp,
            "mean_pull": mean_pull,
            "rms_pull": rms_pull,
            "ks_pvalue": ks_pvalue,
            "well_specified": well_specified
        })
        
    res_df = pd.DataFrame(results)
    res_df = res_df.sort_values(["model", "n_comp", "bin"])
    out_path = base_dir / "pull_summary.csv"
    res_df.to_csv(out_path, index=False)
    print(f"Wrote {len(res_df)} summary rows to {out_path}")

if __name__ == "__main__":
    main()
