import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from nch_response_matrix import load_response_matrix, apply_response

def main():
    data_dir = Path(__file__).parent.parent / "data"
    input_csv = data_dir / "fit_input_ins1735345_v0m.csv"
    output_csv = data_dir / "fit_input_ins1735345_v0m_unfolded.csv"
    
    df = pd.read_csv(input_csv)
    R = load_response_matrix()
    R_pinv = np.linalg.pinv(R)
    
    # Bins sorted by multiplicity
    bins = sorted(df["manuscript_bin"].dropna().unique(), key=lambda b: int(str(b).split("-")[0]))
    print(f"Bins: {bins}")
    
    # We must unfold at each pT point.
    pt_centers = sorted(df["pt_center_gev"].unique())
    
    unfolded_rows = []
    
    for pt in pt_centers:
        pt_df = df[df["pt_center_gev"] == pt]
        
        y_meas = np.zeros(len(bins))
        stat_meas = np.zeros(len(bins))
        sys_meas = np.zeros(len(bins))
        
        # Build vectors
        for i, b in enumerate(bins):
            row = pt_df[pt_df["manuscript_bin"] == b]
            if not row.empty:
                y_meas[i] = row["yield_value"].values[0]
                stat_meas[i] = row["stat_error"].values[0]
                sys_meas[i] = row["sys_error"].values[0]
            else:
                y_meas[i] = np.nan
                stat_meas[i] = np.nan
                sys_meas[i] = np.nan
                
        # Unfold
        y_unf = apply_response(np.nan_to_num(y_meas), R)
        
        # Error propagation for stat and sys separately
        V_stat = np.diag(np.nan_to_num(stat_meas)**2)
        V_sys = np.diag(np.nan_to_num(sys_meas)**2)
        
        V_stat_unf = R_pinv @ V_stat @ R_pinv.T
        V_sys_unf = R_pinv @ V_sys @ R_pinv.T
        
        stat_unf = np.sqrt(np.diag(V_stat_unf))
        sys_unf = np.sqrt(np.diag(V_sys_unf))
        
        # Reconstruct rows
        for i, b in enumerate(bins):
            row = pt_df[pt_df["manuscript_bin"] == b]
            if not row.empty:
                row_dict = row.iloc[0].to_dict()
                row_dict["yield_value"] = y_unf[i]
                row_dict["stat_error"] = stat_unf[i]
                row_dict["sys_error"] = sys_unf[i]
                row_dict["total_error"] = np.sqrt(stat_unf[i]**2 + sys_unf[i]**2)
                unfolded_rows.append(row_dict)
                
    unfolded_df = pd.DataFrame(unfolded_rows)
    unfolded_df.to_csv(output_csv, index=False)
    print(f"Wrote {output_csv}")

if __name__ == "__main__":
    main()
