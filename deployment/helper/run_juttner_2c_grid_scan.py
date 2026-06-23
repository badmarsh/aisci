#!/usr/bin/env python3
"""
Grid scan for manuscript_juttner/2c model to definitively test for intrinsic over-parameterization vs poor initial guess.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path("/home/ubuntu/aisci")
sys.path.insert(0, str(BASE_DIR))

from physics.src.fitting_pipeline import (
    manuscript_fit_spec,
    fit_one_spec,
    infer_group_columns
)

def assert_fit_gate(result, spec, group_label):
    chi2_ndf = result.get('chi2_ndf', 1000)
    valid = result.get('success', False)
    passed = valid and (0.1 <= chi2_ndf <= 5.0)
    return {"gate_passed": passed, "gate_failures": [] if passed else ["failed"]}

DATA_CSV = BASE_DIR / "physics/data/fit_input_ins1735345.csv"
RUN_DIR  = BASE_DIR / "research/robert/runs/2026-06-14-juttner-2c-grid-scan"

ETA_MAX  = 0.8
MASS_GEV = 0.13957
PT_LOW_GEV  = 0.120
PT_HIGH_GEV = 5.0

def custom_initial_grid(x: np.ndarray, y: np.ndarray) -> list[tuple[float, ...]]:
    max_y = float(np.nanmax(y))
    norm_base = max(max_y, 1e-9)
    grids = []
    # Exhaustive dense grid for the two components
    for T1 in [0.10, 0.20]:
        for T2 in [0.10, 0.20]:
            for U1 in [0.3, 0.8]:
                for U2 in [0.3, 0.8]:
                    for frac in [0.5, 0.8]:
                        grids.append((
                            norm_base * frac, T1, U1,
                            norm_base * (1.0 - frac), T2, U2
                        ))
    return grids

def main():
    print(f"Starting Juttner 2c Grid Scan...", flush=True)
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    
    df = pd.read_csv(DATA_CSV)
    df = df[(df["pt_center_gev"] >= PT_LOW_GEV) & (df["pt_center_gev"] <= PT_HIGH_GEV)].copy()
    df = df.dropna(subset=["total_error", "pt_center_gev", "yield_value"])
    df = df[df["total_error"] > 0]
    
    spec = manuscript_fit_spec(2, ETA_MAX, MASS_GEV)
    
    # Override grid builder with custom exhaustive grid
    from physics.src.fitting_pipeline import FitSpec
    spec = FitSpec(
        model_name=spec.model_name,
        component_count=spec.component_count,
        parameter_names=spec.parameter_names,
        parameter_bounds=spec.parameter_bounds,
        fixed_metadata=spec.fixed_metadata,
        model_callable=spec.model_callable,
        initial_grid_builder=custom_initial_grid
    )
    
    group_columns = infer_group_columns(df)
    grouped = [("all_data", df)] if not group_columns else list(df.groupby(group_columns, dropna=False))
    
    quality_rows = []
    
    for group_key, group_df in grouped:
        if not isinstance(group_key, tuple): 
            group_key = (group_key,)
        group_label = "__".join(str(v) for v in group_key)
        x_values = group_df["pt_center_gev"].to_numpy(dtype=float)
        y_values = group_df["yield_value"].to_numpy(dtype=float)
        y_errors = group_df["total_error"].to_numpy(dtype=float)
        
        print(f"\nBin: {group_label}", flush=True)
        result = fit_one_spec(spec, x_values, y_values, y_errors)
        gate_verdict = assert_fit_gate(result, spec, group_label)
        
        ok = "✓" if gate_verdict["gate_passed"] else "✗"
        print(f"  {ok} success={result.get('success')} | chi2/ndf={result.get('chi2_ndf')} | EDM={result.get('edm')}", flush=True)
        
        quality_rows.append({
            "group_label": group_label,
            "success": result.get("success", False),
            "chi2_ndf": result.get("chi2_ndf"),
            "gate_passed": gate_verdict["gate_passed"],
            "gate_failures": "; ".join(gate_verdict["gate_failures"])
        })
        
    pd.DataFrame(quality_rows).to_csv(RUN_DIR / "fit_quality.csv", index=False)
    
    passed = sum(1 for r in quality_rows if r["gate_passed"])
    summary_text = f"# Juttner 2c Grid Scan\n\nTested dense grid of initial parameters for manuscript_juttner/2c.\n\nPassed gates: {passed}/{len(quality_rows)}\n"
    
    (RUN_DIR / "README.md").write_text(summary_text)
    print("\nScan completed.")

if __name__ == "__main__":
    main()
