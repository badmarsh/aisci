#!/usr/bin/env python3
import numpy as np
import pandas as pd
from iminuit import Minuit
from iminuit.cost import LeastSquares
import matplotlib.pyplot as plt
import os
import sys

# Import model from fitting_pipeline
sys.path.insert(0, os.path.dirname(__file__))
from fitting_pipeline import bose_fit_spec

def main():
    run_dir = "research/robert/runs/2026-07-11-exact-be-grid-scan"
    os.makedirs(run_dir, exist_ok=True)
    
    df = pd.read_csv("physics/data/fit_input_ins1735345.csv")
    b = "126-150"
    df_bin = df[df["manuscript_bin"] == b].sort_values("pt_center_gev")
    
    spec = bose_fit_spec(component_count=2, eta_max=0.8, mass_gev=0.13957)
    
    pt = df_bin["pt_center_gev"].values
    y = df_bin["yield_value"].values
    err = df_bin["total_error"].values
    
    cost = LeastSquares(pt, y, err, spec.model_callable)
    
    T_guesses = [0.12, 0.16, 0.20, 0.24]
    U_guesses = [0.4, 0.6, 0.8, 1.0]
    
    norm_guess = np.max(y)
    
    results = []
    
    print(f"Starting Grid Scan for Exact BE 2-component on Bin {b}...")
    for t1 in T_guesses:
        for u1 in U_guesses:
            for t2 in T_guesses:
                for u2 in U_guesses:
                    # Skip symmetric duplicates or unphysical orderings
                    if t1 > t2:
                        continue
                    initial = [norm_guess, t1, u1, norm_guess/10, t2, u2]
                    m = Minuit(cost, *initial, name=spec.parameter_names)
                    for p in spec.parameter_names:
                        m.limits[p] = spec.parameter_bounds[p]
                    m.migrad()
                    
                    res = {
                        "t1_init": t1, "u1_init": u1, "t2_init": t2, "u2_init": u2,
                        "valid": m.valid,
                        "chi2": m.fval,
                        "chi2_ndf": m.fval / (len(pt) - 6),
                        "t1_fit": m.values["temperature_1"] if m.valid else np.nan,
                        "t2_fit": m.values["temperature_2"] if m.valid else np.nan,
                        "u1_fit": m.values["U_1"] if m.valid else np.nan,
                        "u2_fit": m.values["U_2"] if m.valid else np.nan
                    }
                    results.append(res)
                    if m.valid:
                        print(f"Init: T1={t1}, U1={u1}, T2={t2}, U2={u2} -> Converged! chi2/ndf={res['chi2_ndf']:.2f}")
                    else:
                        print(f"Init: T1={t1}, U1={u1}, T2={t2}, U2={u2} -> Failed")
                        
    res_df = pd.DataFrame(results)
    res_df.to_csv(f"{run_dir}/grid_scan_results.csv", index=False)
    
    valid_df = res_df[res_df["valid"]]
    if not valid_df.empty:
        best = valid_df.loc[valid_df["chi2_ndf"].idxmin()]
        print("\n--- BEST FIT ---")
        print(best)
        
        plt.figure(figsize=(8, 6))
        plt.hist(valid_df["chi2_ndf"], bins=20, color='blue', alpha=0.7)
        plt.xlabel("$\chi^2$/ndf")
        plt.ylabel("Frequency")
        plt.title("Grid Scan Convergence Distribution (Exact BE)")
        plt.axvline(best["chi2_ndf"], color='red', linestyle='dashed', label='Global Minimum')
        plt.legend()
        plt.savefig(f"{run_dir}/chi2_distribution.png")
        print(f"Saved plots to {run_dir}/")

if __name__ == "__main__":
    main()
