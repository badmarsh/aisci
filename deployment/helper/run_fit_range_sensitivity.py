#!/usr/bin/env python3
"""
Fit-range sensitivity scan for tsallis and blast_wave models.
Drops low-pT bins systematically to test the sensitivity of extracted parameters to the low-pT region.
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
    tsallis_fit_spec,
    blast_wave_fit_spec,
    fit_one_spec
)

DATA_CSV = BASE_DIR / "physics/data/fit_input_ins1735345.csv"
RUN_DIR  = BASE_DIR / "research/robert/runs/2026-06-14-fit-range-scan"

ETA_MAX  = 0.8
MASS_GEV = 0.13957
PT_HIGH_GEV = 5.0
BIN_LABEL = "21-30"

# The pT cuts to test
PT_CUTS = [0.120, 0.200, 0.300, 0.450]

def main():
    print("Starting Fit-Range Sensitivity Scan...")
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    
    df_full = pd.read_csv(DATA_CSV)
    df_bin = df_full[df_full["manuscript_bin"] == BIN_LABEL].copy()
    
    results = []
    
    for pt_low in PT_CUTS:
        print(f"\n--- Fitting with pT > {pt_low} GeV ---")
        df = df_bin[(df_bin["pt_center_gev"] >= pt_low) & (df_bin["pt_center_gev"] <= PT_HIGH_GEV)].copy()
        df = df.dropna(subset=["total_error", "pt_center_gev", "yield_value"])
        df = df[df["total_error"] > 0]
        
        x_values = df["pt_center_gev"].to_numpy(dtype=float)
        y_values = df["yield_value"].to_numpy(dtype=float)
        y_errors = df["total_error"].to_numpy(dtype=float)
        
        specs = [
            tsallis_fit_spec(1, ETA_MAX, MASS_GEV),
            blast_wave_fit_spec(1, MASS_GEV)
        ]
        
        for spec in specs:
            res = fit_one_spec(spec, x_values, y_values, y_errors)
            chi2_ndf = res.get("chi2_ndf")
            params = res.get("parameter_values", {})
            print(f"  {spec.model_name:12s} | chi2/ndf={chi2_ndf:5.2f} | Params: {params}")
            
            row = {
                "pt_cut": pt_low,
                "model_name": spec.model_name,
                "chi2_ndf": chi2_ndf,
                "temperature": params.get("temperature_1"),
                "q": params.get("q_1"),
                "beta_s": params.get("beta_s_1"),
                "n": params.get("n_1")
            }
            results.append(row)
            
    pd.DataFrame(results).to_csv(RUN_DIR / "sensitivity_results.csv", index=False)
    
    with open(RUN_DIR / "README.md", "w") as f:
        f.write("# Fit-Range Sensitivity Scan\n\nTested tsallis/1c and blast_wave/1c on bin 21-30 with varying low-pT cuts to observe parameter drift.\n")
    print("\nScan completed.")

if __name__ == "__main__":
    main()
