import os
import sys
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from iminuit import Minuit
from iminuit.cost import LeastSquares
import matplotlib.pyplot as plt
from multiprocessing import Pool
from functools import partial

sys.path.append(os.getcwd())
from physics.src.bgbw_fit import bgbw_vec

def fit_fixed_beta(bs_pt_y_err, mass_gev=0.13957):
    bs, pt, y, err = bs_pt_y_err
    def model(pt_vals, norm, temperature, n_val):
        return bgbw_vec(pt_vals, norm, temperature, bs, n_val, mass_gev)

    norm_guess = float(np.nanmax(y))
    best = None
    for T0, n0 in [(0.10, 0.8), (0.15, 1.5), (0.20, 2.5)]:
        cost = LeastSquares(pt, y, err, model)
        m = Minuit(cost, norm=norm_guess, temperature=T0, n_val=n0)
        m.limits["norm"] = (1e-12, None)
        m.limits["temperature"] = (0.01, 0.80)
        m.limits["n_val"] = (0.10, 4.00)
        try:
            m.migrad()
            if m.valid:
                chi2 = m.fval
                if best is None or chi2 < best['chi2']:
                    best = {
                        'chi2': chi2,
                        'norm': m.values["norm"],
                        'temperature': m.values["temperature"],
                        'n_val': m.values["n_val"]
                    }
        except Exception:
            pass
    
    if best is None:
        return {'beta_s': bs, 'T_kin_gev': float('nan'), 'chi2': np.inf, 'norm': float('nan'), 'n_val': float('nan')}
    else:
        return {'beta_s': bs, 'T_kin_gev': best['temperature'], 'chi2': best['chi2'], 'norm': best['norm'], 'n_val': best['n_val']}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--data-path", type=Path, required=True)
    args = parser.parse_args()

    args.run_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.data_path)
    bins = sorted(df["manuscript_bin"].dropna().unique(), key=lambda b: int(str(b).split("-")[0]))

    fig, axes = plt.subplots(2, 5, figsize=(20, 8))
    axes = axes.flatten()

    beta_s_grid = np.linspace(0.10, 0.95, 25)

    for i, bin_label in enumerate(bins):
        print(f"Running profile scan for bin {bin_label}...")
        sub = df[df["manuscript_bin"] == bin_label].dropna(subset=["pt_center_gev", "yield_value"])
        pt = sub["pt_center_gev"].to_numpy(float)
        y = sub["yield_value"].to_numpy(float)
        err = sub["total_error"].to_numpy(float)
        
        args_list = [(bs, pt, y, err) for bs in beta_s_grid]
        with Pool() as pool:
            results = pool.map(fit_fixed_beta, args_list)
            
        min_chi2 = min([r['chi2'] for r in results])
        
        for r in results:
            r['delta_chi2'] = r['chi2'] - min_chi2
            r['inside_68cl'] = r['delta_chi2'] < 1.0
            
        res_df = pd.DataFrame(results)
        res_df.to_csv(args.run_dir / f"contour_bin_{bin_label}.csv", index=False)
        
        ax = axes[i]
        cl95 = res_df[res_df['delta_chi2'] < 3.84]
        ax.fill_between(cl95['beta_s'], cl95['T_kin_gev'] - 0.005, cl95['T_kin_gev'] + 0.005, color='lightblue', alpha=0.5, label='95% CL')
        cl68 = res_df[res_df['delta_chi2'] < 1.0]
        ax.fill_between(cl68['beta_s'], cl68['T_kin_gev'] - 0.002, cl68['T_kin_gev'] + 0.002, color='blue', alpha=0.7, label='68% CL')
        
        ax.plot(res_df['beta_s'], res_df['T_kin_gev'], 'k--', alpha=0.5, label='Profile Valley')
        
        min_row = res_df.loc[res_df['chi2'].idxmin()]
        ax.plot(min_row['beta_s'], min_row['T_kin_gev'], 'r*', markersize=12, label='Global Min')
        
        ndf = len(pt) - 4
        ax.set_title(f"{bin_label} (min chi2/ndf = {min_chi2/ndf:.2f})")
        ax.set_xlabel(r"$\beta_s$")
        ax.set_ylabel(r"$T_{\mathrm{kin}}$ [GeV]")
        if i == 0:
            ax.legend()
            
    plt.tight_layout()
    plt.savefig(args.run_dir / "profile_contours_all_bins.png")

if __name__ == "__main__":
    main()
