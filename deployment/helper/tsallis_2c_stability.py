import os
import argparse
from pathlib import Path
import pandas as pd

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--params-csv", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.params_csv)
    df_tsallis = df[(df['model_name'] == 'tsallis') & (df['component_count'] == 2)]

    results = []
    print(f"{'Bin':<10} | {'T1':<8} | {'T2':<8} | {'dT/T_max':<10} | {'q1':<8} | {'q2':<8} | {'dq/q_max':<10} | {'Status'}")
    print("-" * 90)

    for bin_label, group in df_tsallis.groupby('group_label'):
        p_dict = dict(zip(group['parameter_name'], group['value']))
        
        T1 = p_dict.get('temperature_1', float('nan'))
        T2 = p_dict.get('temperature_2', float('nan'))
        q1 = p_dict.get('q_1', float('nan'))
        q2 = p_dict.get('q_2', float('nan'))
        n1 = p_dict.get('norm_1', float('nan'))
        n2 = p_dict.get('norm_2', float('nan'))
        
        if pd.isna(T1) or pd.isna(T2) or pd.isna(q1) or pd.isna(q2):
            status = "MISSING PARAMS"
            results.append({"bin": bin_label, "status": status})
            print(f"{bin_label:<10} | {status}")
            continue
            
        dt_frac = abs(T1 - T2) / max(T1, T2)
        dq_frac = abs(q1 - q2) / max(q1, q2)
        
        if dt_frac < 0.05 or dq_frac < 0.05:
            status = "COLLAPSED"
        else:
            status = "DISTINCT COMPONENTS"
            
        results.append({
            "bin": bin_label,
            "T1": T1,
            "T2": T2,
            "q1": q1,
            "q2": q2,
            "norm1": n1,
            "norm2": n2,
            "status": status
        })
        
        print(f"{bin_label:<10} | {T1:<8.4f} | {T2:<8.4f} | {dt_frac:<10.2%} | {q1:<8.4f} | {q2:<8.4f} | {dq_frac:<10.2%} | {status}")

    out_path = args.out_dir / "tsallis_2c_stability.csv"
    pd.DataFrame(results).to_csv(out_path, index=False)
    print(f"\nWritten to {out_path}")

if __name__ == "__main__":
    main()
