#!/usr/bin/env python3
import numpy as np
import pandas as pd
from iminuit import Minuit
from iminuit.cost import LeastSquares
import matplotlib.pyplot as plt
import os
import math
from scipy.integrate import quad
from scipy.special import i0e, k1e

def bose_component_scalar(pt: float, norm: float, T: float, U: float, mass_gev: float, eta_max: float) -> float:
    mt = math.sqrt(mass_gev ** 2 + pt ** 2)

    def integrand(eta: float) -> float:
        cosh_eta = math.cosh(eta)
        E = mt * cosh_eta
        p_long = mt * math.sinh(eta)
        U_vec = U
        U0 = math.sqrt(1 + U_vec**2)
        # scalar product U * p = U0*E - U_vec*p_long (assuming parallel to z)
        # Wait, the manuscript says U.p = U0 E - U_T p_T cos(phi) ? 
        # Actually I should just use what the fitting_pipeline has.
        # Let's import it from fitting_pipeline!
        pass
    return 0.0

# Actually, I should just import it from fitting_pipeline
import sys
sys.path.insert(0, os.path.dirname(__file__))
from fitting_pipeline import bose_fit_spec

def main():
    run_dir = "research/robert/runs/2026-07-11-exact-be-fit-range-scan"
    os.makedirs(run_dir, exist_ok=True)
    
    df = pd.read_csv("libs/physics-core/data/fit_input_ins1735345.csv")
    b = "21-30"
    df_bin = df[df["manuscript_bin"] == b].sort_values("pt_center_gev")
    
    spec = bose_fit_spec(component_count=2, eta_max=0.8, mass_gev=0.13957)
    
    cutoffs = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
    
    results = []
    
    for cutoff in cutoffs:
        sub = df_bin[df_bin["pt_center_gev"] >= cutoff]
        pt = sub["pt_center_gev"].values
        y = sub["yield_value"].values
        err = sub["total_error"].values
        
        cost = LeastSquares(pt, y, err, spec.model_callable)
        
        initial = [np.max(y), 0.15, 0.5, np.max(y)/10, 0.25, 0.8]
        m = Minuit(cost, *initial, name=spec.parameter_names)
        
        for p in spec.parameter_names:
            m.limits[p] = spec.parameter_bounds[p]
            
        m.migrad()
        if m.valid:
            results.append({
                "cutoff": cutoff,
                "T_1": m.values["temperature_1"],
                "T_2": m.values["temperature_2"],
                "U_1": m.values["U_1"],
                "U_2": m.values["U_2"],
                "chi2_ndf": m.fval / (len(pt) - 6)
            })
            print(f"Cutoff {cutoff} GeV -> chi2/ndf: {m.fval / (len(pt) - 6):.2f}, T_1: {m.values['temperature_1']:.3f}, T_2: {m.values['temperature_2']:.3f}")
        else:
            print(f"Cutoff {cutoff} GeV -> MIGRAD failed")

    if results:
        import csv
        with open(f"{run_dir}/fit_range_scan.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
            
        res_df = pd.DataFrame(results)
        
        plt.figure(figsize=(10, 6))
        plt.plot(res_df["cutoff"], res_df["T_1"], marker='o', label="$T_1$")
        plt.plot(res_df["cutoff"], res_df["T_2"], marker='s', label="$T_2$")
        plt.xlabel("Low-$p_T$ Cutoff [GeV]")
        plt.ylabel("Temperature [GeV]")
        plt.title("Exact BE Fit Range Sensitivity ($T$) - Bin 21-30")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"{run_dir}/T_vs_cutoff.png")
        
        plt.figure(figsize=(10, 6))
        plt.plot(res_df["cutoff"], res_df["U_1"], marker='o', label="$U_1$")
        plt.plot(res_df["cutoff"], res_df["U_2"], marker='s', label="$U_2$")
        plt.xlabel("Low-$p_T$ Cutoff [GeV]")
        plt.ylabel("Flow Velocity $U$")
        plt.title("Exact BE Fit Range Sensitivity ($U$) - Bin 21-30")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"{run_dir}/U_vs_cutoff.png")
        
        print(f"Saved plots to {run_dir}/")
        
if __name__ == "__main__":
    main()
