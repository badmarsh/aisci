import os
import argparse
from pathlib import Path
import pandas as pd
from scipy.stats import f

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    # chi2/ndf values from evidence ledger
    data = [
        {"bin": "21-30", "chi2_1c": 0.59, "chi2_2c": 0.36},
        {"bin": "31-40", "chi2_1c": 6.57, "chi2_2c": 1.03},
        {"bin": "41-50", "chi2_1c": 9.11, "chi2_2c": 1.34},
        {"bin": "51-60", "chi2_1c": 10.6, "chi2_2c": 1.43},
        {"bin": "61-70", "chi2_1c": 18.4, "chi2_2c": 19.8},
        {"bin": "71-80", "chi2_1c": 19.2, "chi2_2c": 2.05},
        {"bin": "81-90", "chi2_1c": 19.4, "chi2_2c": 20.8},
        {"bin": "91-100", "chi2_1c": 19.6, "chi2_2c": float('nan')},
        {"bin": "101-125", "chi2_1c": 19.2, "chi2_2c": 1.37},
        {"bin": "126-150", "chi2_1c": 12.3, "chi2_2c": 0.45},
    ]

    ndf_1c = 47 - 3
    ndf_2c = 47 - 6
    delta_k = 3

    results = []
    print(f"{'Bin':<10} | {'chi2/ndf_1c':<12} | {'chi2/ndf_2c':<12} | {'F':<10} | {'p-value':<10} | {'Decision'}")
    print("-" * 80)

    for row in data:
        bin_label = row["bin"]
        c1 = row["chi2_1c"]
        c2 = row["chi2_2c"]
        
        if pd.isna(c2) or c2 >= c1:
            F_stat = 0.0
            p_val = 1.0
            decision = "OVERFITTING"
        else:
            # chi2 = (chi2/ndf) * ndf
            abs_chi2_1c = c1 * ndf_1c
            abs_chi2_2c = c2 * ndf_2c
            delta_chi2 = abs_chi2_1c - abs_chi2_2c
            
            F_stat = (delta_chi2 / delta_k) / (abs_chi2_2c / ndf_2c)
            p_val = f.sf(F_stat, dfn=delta_k, dfd=ndf_2c)
            
            if p_val < 0.05:
                decision = "2c STATISTICALLY WARRANTED"
            else:
                decision = "OVERFITTING"

        results.append({
            "bin": bin_label,
            "chi2/ndf_1c": c1,
            "chi2/ndf_2c": c2,
            "F": F_stat,
            "p-value": p_val,
            "decision": decision
        })
        
        print(f"{bin_label:<10} | {c1:<12.2f} | {c2:<12.2f} | {F_stat:<10.2f} | {p_val:<10.2e} | {decision}")

    df_res = pd.DataFrame(results)
    out_path = args.out_dir / "tsallis_ftest.csv"
    df_res.to_csv(out_path, index=False)
    print(f"\nWritten to {out_path}")

if __name__ == "__main__":
    main()
