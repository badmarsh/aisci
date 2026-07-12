import os
import pandas as pd
from typing import Dict, Any, List

def parse_model_name(raw_name: str) -> str:
    """Safely map raw model names to component counts."""
    # E.g. "tsallis__2c" or "tsallis_2c" or just "tsallis" (assume 1c if missing?)
    parts = raw_name.replace("__", "_").split("_")
    
    # Try to extract component count if present
    cc = "1c"
    if len(parts) > 1 and parts[-1].endswith("c") and parts[-1][:-1].isdigit():
        cc = parts.pop()
    
    base = "_".join(parts).lower()
    
    if "juttner" in base or "manuscript" in base:
        family = "Jüttner/Boltzmann"
    elif "bgbw" in base or "blast_wave" in base:
        family = "Blast-Wave (BGBW)"
    elif "tsallis" in base:
        family = "Tsallis-Pareto"
    elif "bose_einstein" in base:
        family = "Bose-Einstein"
    else:
        family = base.title()
        
    return f"{family} {cc}"

def parse_fit_artifacts(run_path: str) -> Dict[str, Any]:
    quality_path = os.path.join(run_path, "fit_quality.csv")
    params_path = os.path.join(run_path, "fit_parameters.csv")
    corr_path = os.path.join(run_path, "parameter_correlations.csv")
    
    if not os.path.exists(quality_path):
        raise FileNotFoundError(f"Missing {quality_path}")
        
    quality_df = pd.read_csv(quality_path)
    
    # Optional files
    params_df = pd.read_csv(params_path) if os.path.exists(params_path) else pd.DataFrame()
    corr_df = pd.read_csv(corr_path) if os.path.exists(corr_path) else pd.DataFrame()
    
    corr_lookup: dict = {}
    if not corr_df.empty:
        for _, row in corr_df.iterrows():
            b = row['group_label']
            m_nice = parse_model_name(row['model_name'])
            key = f"{row['parameter_left']}|{row['parameter_right']}"
            corr_lookup.setdefault(b, {}).setdefault(m_nice, {})[key] = round(float(row['correlation']), 4)

    run_name = os.path.basename(run_path)
    run_date = run_name[:10] if len(run_name) >= 10 else "unknown"
    run_timestamp = f"{run_date}T00:00:00Z"
    
    fit_rows = []
    
    for _, row in quality_df.iterrows():
        bin_label = row['group_label']
        model_nice = parse_model_name(row['model_name'])
        
        t_str = "—"
        beta_str = "—"
        
        if not params_df.empty:
            subset = params_df[(params_df['group_label'] == bin_label) & (params_df['model_name'] == row['model_name'])]
            
            t_row = subset[subset['parameter_name'].isin(['temperature_1', 'T_kin', 'T_stat'])]
            if not t_row.empty:
                t_val = t_row.iloc[0]['value']
                t_err = t_row.iloc[0]['error']
                t_str = f"{t_val:.3f} ± {t_err:.3f}"
                
            beta_row = subset[subset['parameter_name'].isin(['beta_1', 'beta_s', 'velocity_1', 'v_1'])]
            if not beta_row.empty:
                b_val = beta_row.iloc[0]['value']
                b_err = beta_row.iloc[0]['error']
                beta_str = f"{b_val:.3f} ± {b_err:.3f}"
            else:
                # Also check for U_1, but we don't mix them up semantically
                u_row = subset[subset['parameter_name'].isin(['U_1', 'u_1'])]
                if not u_row.empty:
                    b_val = u_row.iloc[0]['value']
                    b_err = u_row.iloc[0]['error']
                    beta_str = f"U={b_val:.3f} ± {b_err:.3f}"

        is_success = row.get('success', False)
        quality_flag = str(row.get('fit_quality_flag', 'unknown')).upper()
        
        # Determine "Clean Fit" correctly (must actually converge and have good chi2)
        chi2 = float(row.get('chi2_ndf', 999.0))
        status = "Converged" if is_success else "Failed"
        if is_success and chi2 < 3.0:
            status = "Clean Fit"
        elif not is_success:
            quality_flag = "FAILED"

        fit_rows.append({
            "bin": bin_label,
            "model": model_nice,
            "raw_model": row['model_name'],
            "chi2": round(chi2, 2),
            "quality": quality_flag,
            "T": t_str,
            "beta": beta_str,
            "aic": round(row.get('aic', 0.0), 1),
            "bic": round(row.get('bic', 0.0), 1),
            "status": status,
            "correlations": corr_lookup.get(bin_label, {}).get(model_nice, {}),
            "seedIndex": int(row['seed_index']) if 'seed_index' in row and not pd.isna(row['seed_index']) else None,
            "runTimestamp": run_timestamp,
        })
        
    bins = sorted(list(set(row['group_label'] for _, row in quality_df.iterrows())), key=lambda x: int(x.split('-')[0]) if '-' in x else x)
    
    return {
        "fitRows": fit_rows,
        "bins": bins,
        "runId": run_name,
        "quality_df": quality_df,
        "params_df": params_df,
        "corr_df": corr_df
    }
