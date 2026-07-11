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

def bgbw_scalar(pt: float, norm: float, T: float, beta_s: float,
                n_val: float, mass_gev: float) -> float:
    mt = math.sqrt(mass_gev ** 2 + pt ** 2)

    def integrand(r: np.ndarray) -> np.ndarray:
        beta_r = np.minimum(beta_s * r ** n_val, 0.999999)
        rho = np.arctanh(beta_r)
        arg_i = pt * np.sinh(rho) / T
        arg_k = mt * np.cosh(rho) / T
        return r * mt * i0e(arg_i) * k1e(arg_k) * np.exp(arg_i - arg_k)

    r_arr = np.linspace(0.0, 1.0, 200)
    val = np.trapezoid(integrand(r_arr), r_arr)
    return norm * pt * val

def bgbw_vec(pt_arr: np.ndarray, norm: float, T: float, beta_s: float,
             n_val: float, mass_gev: float) -> np.ndarray:
    return np.array([bgbw_scalar(float(p), norm, T, beta_s, n_val, mass_gev)
                     for p in pt_arr])

def main():
    run_dir = "research/robert/runs/2026-07-11-minos-contours"
    os.makedirs(run_dir, exist_ok=True)
    df = pd.read_csv("physics/data/fit_input_ins1735345.csv")
    mass_gev = 0.13957
    bins = sorted(df["manuscript_bin"].dropna().unique(),
                  key=lambda b: int(str(b).split("-")[0]))

    fig, ax = plt.subplots(figsize=(10, 8))
    
    for b in bins:
        sub = df[df["manuscript_bin"] == b]
        pt = sub["pt_center_gev"].values
        y = sub["yield_value"].values
        err = sub["total_error"].values

        def model(pt_vals, norm, T, beta_s, n_val):
            return bgbw_vec(pt_vals, norm, T, beta_s, n_val, mass_gev)

        cost = LeastSquares(pt, y, err, model)
        m = Minuit(cost, norm=np.max(y), T=0.15, beta_s=0.6, n_val=1.0)
        m.limits["norm"] = (0, None)
        m.limits["T"] = (0.01, 0.8)
        m.limits["beta_s"] = (0.0, 0.99)
        m.limits["n_val"] = (0.1, 4.0)
        
        m.migrad()
        m.hesse()
        
        if m.valid:
            print(f"Drawing contours for bin {b}...")
            # mncontour takes parameter names and confidence level
            try:
                pts_68 = m.mncontour("T", "beta_s", cl=0.68, size=30)
                pts_95 = m.mncontour("T", "beta_s", cl=0.95, size=30)
                
                x68, y68 = zip(*pts_68)
                x95, y95 = zip(*pts_95)
                
                x68 = list(x68) + [x68[0]]
                y68 = list(y68) + [y68[0]]
                x95 = list(x95) + [x95[0]]
                y95 = list(y95) + [y95[0]]
                
                line, = ax.plot(x68, y68, label=f"Bin {b} (68%)")
                ax.plot(x95, y95, color=line.get_color(), linestyle='dashed')
                ax.plot([m.values["T"]], [m.values["beta_s"]], marker='x', color=line.get_color())
            except Exception as e:
                print(f"Failed to draw contour for bin {b}: {e}")

    ax.set_xlabel("$T_{kin}$ [GeV]")
    ax.set_ylabel("$\\beta_s$")
    ax.set_title("BGBW Profile Likelihood MINOS Contours")
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(f"{run_dir}/minos_contours_all_bins.png")
    print(f"Saved {run_dir}/minos_contours_all_bins.png")

if __name__ == "__main__":
    main()
