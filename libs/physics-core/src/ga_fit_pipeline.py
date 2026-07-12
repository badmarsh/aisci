import pandas as pd
import numpy as np
from scipy.optimize import differential_evolution
from iminuit import Minuit
from iminuit.cost import LeastSquares
import matplotlib.pyplot as plt

import sys
from pathlib import Path

# Ensure the src folder is in the path
sys.path.append(str(Path(__file__).parent))

from models.juttner import manuscript_component_scalar
from models.powerlaw import powerlaw_component_scalar

DEFAULT_MASS_GEV = 0.13957
ETA_MAX = 0.8

def load_data(file_path: str, bin_name: str):
    df = pd.read_csv(file_path)
    df = df[df['manuscript_bin'] == bin_name]
    # Filter valid pT ranges
    df = df[df['pt_center_gev'] >= 0.15]
    return df['pt_center_gev'].values, df['yield_value'].values, df['total_error'].values

def combined_model(pt, norm_soft, T_soft, U_soft, norm_hard, p0_hard, n_hard):
    soft = manuscript_component_scalar(pt, norm_soft, T_soft, U_soft, ETA_MAX, DEFAULT_MASS_GEV)
    hard = powerlaw_component_scalar(pt, norm_hard, p0_hard, n_hard)
    return soft + hard

def vectorized_model(pt_arr, norm_soft, T_soft, U_soft, norm_hard, p0_hard, n_hard):
    return np.array([combined_model(pt, norm_soft, T_soft, U_soft, norm_hard, p0_hard, n_hard) for pt in pt_arr])

def main():
    data_path = Path(__file__).parent.parent / "data" / "fit_input_ins1735345_v0m.csv"
    bin_name = "101-125"
    print(f"Loading data for bin {bin_name}...")
    pt, y, y_err = load_data(data_path, bin_name)
    print(f"Loaded {len(pt)} data points.")

    # 1. Define objective function for GA
    # LeastSquares returns sum((y - model)**2 / err**2)
    lsq = LeastSquares(pt, y, y_err, vectorized_model)

    def cost_function(params):
        return lsq(*params)

    # 2. Set bounds for Genetic Algorithm
    # params: norm_soft, T_soft, U_soft, norm_hard, p0_hard, n_hard
    bounds = [
        (1e-2, 1e4),      # norm_soft
        (0.05, 0.40),     # T_soft (GeV)
        (0.0, 1.5),       # U_soft
        (1e-4, 1e2),      # norm_hard
        (0.1, 5.0),       # p0_hard
        (2.0, 15.0)       # n_hard
    ]

    print("Running Genetic Algorithm (differential_evolution)...")
    res = differential_evolution(cost_function, bounds, strategy='best1bin', maxiter=1000, popsize=15, tol=1e-3, seed=42, disp=True)

    print("\n=== GA Global Minimum Found ===")
    print(f"chi2 = {res.fun:.2f}")
    print(f"Parameters: {res.x}")

    # 3. Polish with Minuit
    print("\nRunning Minuit to polish and compute covariance...")
    m = Minuit(lsq, norm_soft=res.x[0], T_soft=res.x[1], U_soft=res.x[2], norm_hard=res.x[3], p0_hard=res.x[4], n_hard=res.x[5])
    
    # Set limits based on bounds to prevent Minuit from wandering
    m.limits["norm_soft"] = bounds[0]
    m.limits["T_soft"] = bounds[1]
    m.limits["U_soft"] = bounds[2]
    m.limits["norm_hard"] = bounds[3]
    m.limits["p0_hard"] = bounds[4]
    m.limits["n_hard"] = bounds[5]

    # Run migrad to find minimum and hesse for errors
    m.migrad()
    m.hesse()

    print("\n=== Minuit Final Results ===")
    print(m.params)
    print(f"Final chi2/ndf = {m.fval} / {len(pt) - m.nfit} = {m.fval / (len(pt) - m.nfit):.3f}")

    # 4. Plot results
    print("\nPlotting results...")
    plt.figure(figsize=(10, 6))
    
    # Data
    plt.errorbar(pt, y, yerr=y_err, fmt='ko', label=f'ALICE 13 TeV ({bin_name})')
    
    # Fit
    pt_smooth = np.linspace(min(pt), max(pt), 200)
    y_fit = vectorized_model(pt_smooth, *m.values)
    
    # Components
    y_soft = np.array([manuscript_component_scalar(p, m.values[0], m.values[1], m.values[2], ETA_MAX, DEFAULT_MASS_GEV) for p in pt_smooth])
    y_hard = np.array([powerlaw_component_scalar(p, m.values[3], m.values[4], m.values[5]) for p in pt_smooth])
    
    plt.plot(pt_smooth, y_fit, 'r-', lw=2, label=f'Total Fit (chi2/ndf={m.fval / (len(pt) - m.nfit):.2f})')
    plt.plot(pt_smooth, y_soft, 'b--', lw=1.5, label='Soft Component (Jüttner)')
    plt.plot(pt_smooth, y_hard, 'g-.', lw=1.5, label='Hard Component (Power-law)')
    
    plt.yscale('log')
    plt.xlabel('$p_T$ (GeV)')
    plt.ylabel('Invariant Yield')
    plt.title('Two-Component Soft/Hard Model Fit (GA + Minuit)')
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    out_path = Path("/home/ubuntu/.gemini/antigravity-ide/brain/af192ac4-8931-496f-a302-1ae50e1aac25/fit_plot.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved to {out_path}")

if __name__ == "__main__":
    main()
