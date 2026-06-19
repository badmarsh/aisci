#!/usr/bin/env python3
"""
Fit-range sensitivity test for BGBW (blast_wave) model.

Tests whether T_kin and beta_s change significantly when the low-pT data
are excluded, addressing science question Q5 (parameter constraint by pT range).

Method:
  1. Fit BGBW/1c on full range: pT ∈ [0.15, 3.0] GeV
  2. Fit BGBW/1c on restricted range: pT ∈ [0.50, 3.0] GeV (low-pT excluded)
  3. Compare T_kin and beta_s — flag as "fit-range dependent" if they differ by > 2σ.

Usage:
    cd /home/ubuntu/aisci/physics && source physics_env/bin/activate
    python deployment/helper/run_fit_range_sensitivity.py

Output:
    Prints a summary table and writes results to:
    research/robert/runs/2026-06-20-phd-level-fits/fit_range_sensitivity.csv
"""
import csv
import math
import os
import sys

import numpy as np
from iminuit import Minuit
from iminuit.cost import LeastSquares
from scipy.integrate import quad
from scipy.special import ive, kve

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = "/home/ubuntu/aisci"
DATA_PATH = os.path.join(REPO_ROOT, "physics/data/fit_input.csv")
OUT_PATH  = os.path.join(REPO_ROOT, "research/robert/runs/2026-06-20-phd-level-fits/fit_range_sensitivity.csv")

MASS_PION_GEV = 0.13957  # charged pion

# ---------------------------------------------------------------------------
# BGBW model (identical to fitting_pipeline.py)
# ---------------------------------------------------------------------------

def blast_wave_scalar(pt, norm, temperature, beta_s, n_value, mass=MASS_PION_GEV):
    """BGBW integrand over transverse radius using scaled Bessel functions."""
    mt = math.sqrt(mass**2 + pt**2)

    def integrand(r):
        if r == 0.0:
            return 0.0
        beta_r = min(beta_s * r**n_value, 0.999999)
        rho = math.atanh(beta_r)
        arg_i = pt * math.sinh(rho) / temperature
        arg_k = mt * math.cosh(rho) / temperature
        if arg_k <= 0.0:
            return 0.0
        exp_factor = math.exp(arg_i - arg_k)
        val = ive(0, arg_i) * kve(1, arg_k) * exp_factor
        return r * mt * val if math.isfinite(val) else 0.0

    integral, _ = quad(integrand, 0.0, 1.0, limit=100)
    return norm * pt * integral


def blast_wave_vector(pt_array, norm, temperature, beta_s, n_value):
    return np.array([blast_wave_scalar(float(pt), norm, temperature, beta_s, n_value)
                     for pt in pt_array])


# ---------------------------------------------------------------------------
# Fit helper
# ---------------------------------------------------------------------------

def fit_bgbw(pt, y, yerr, label=""):
    """Run iMinuit BGBW fit; return (T_MeV, beta_s, sigma_T_MeV, sigma_beta_s, chi2_ndf, converged)."""
    cost = LeastSquares(pt, y, yerr, blast_wave_vector)

    # Initial values from literature (Khuntia 2019, Rath 2020)
    m = Minuit(cost,
               norm=float(np.max(y) * 10),
               temperature=0.12,
               beta_s=0.6,
               n_value=1.0)
    m.limits['temperature'] = (0.05, 0.30)
    m.limits['beta_s']      = (0.01, 0.99)
    m.limits['n_value']     = (0.5, 5.0)
    m.limits['norm']        = (1e-3, 1e12)

    m.migrad()
    m.hesse()

    converged = m.valid and m.accurate
    ndf = len(pt) - 4
    chi2_ndf = m.fval / ndf if ndf > 0 else float('nan')
    T_MeV   = m.values['temperature'] * 1000.0
    beta_s  = m.values['beta_s']
    try:
        sigma_T_MeV  = math.sqrt(m.errors['temperature']**2) * 1000.0
        sigma_beta_s = m.errors['beta_s']
    except Exception:
        sigma_T_MeV  = float('nan')
        sigma_beta_s = float('nan')

    return T_MeV, beta_s, sigma_T_MeV, sigma_beta_s, chi2_ndf, converged


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

def load_data(path):
    """Load fit_input.csv; return dict bin_label -> list of (pt, yield, err)."""
    data = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = row['multiplicity_selection']
            pt    = float(row['pt_center_gev'])
            y     = float(row['yield_value'])
            err   = float(row['total_error'])
            if label not in data:
                data[label] = []
            data[label].append((pt, y, err))
    return data


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== BGBW Fit-Range Sensitivity Test ===")
    print(f"Data: {DATA_PATH}")
    print(f"Model: blast_wave/1c  Mass: {MASS_PION_GEV*1000:.1f} MeV (pion)")
    print()

    if not os.path.exists(DATA_PATH):
        print(f"ERROR: Data file not found: {DATA_PATH}")
        sys.exit(1)

    raw = load_data(DATA_PATH)

    FULL_PT_MIN  = 0.15  # GeV
    TRUNC_PT_MIN = 0.50  # GeV
    PT_MAX       = 3.00  # GeV

    results = []

    header = ("bin_label,n_full,n_trunc,"
              "T_full_MeV,beta_s_full,sigma_T_full,sigma_beta_s_full,chi2_ndf_full,conv_full,"
              "T_trunc_MeV,beta_s_trunc,sigma_T_trunc,sigma_beta_s_trunc,chi2_ndf_trunc,conv_trunc,"
              "delta_T_MeV,delta_T_nsigma,delta_beta_s,delta_beta_s_nsigma,flag")

    rows_out = []

    bins_order = sorted(raw.keys())

    for bin_label in bins_order:
        pts_data = raw[bin_label]

        full  = [(pt, y, e) for pt, y, e in pts_data if FULL_PT_MIN  <= pt <= PT_MAX]
        trunc = [(pt, y, e) for pt, y, e in pts_data if TRUNC_PT_MIN <= pt <= PT_MAX]

        if len(full) < 5 or len(trunc) < 5:
            print(f"  {bin_label}: skipped (too few points)")
            continue

        pt_f, y_f, e_f = zip(*full)
        pt_t, y_t, e_t = zip(*trunc)

        pt_f  = np.array(pt_f);  y_f = np.array(y_f);  e_f = np.array(e_f)
        pt_t  = np.array(pt_t);  y_t = np.array(y_t);  e_t = np.array(e_t)

        print(f"  {bin_label}: fitting full ({len(full)} pts) ...", end="", flush=True)
        T_full, b_full, sT_full, sb_full, c2_full, ok_full = fit_bgbw(pt_f, y_f, e_f, "full")
        print(f" T={T_full:.1f} MeV, beta_s={b_full:.3f}, chi2/ndf={c2_full:.1f}")

        print(f"  {bin_label}: fitting trunc ({len(trunc)} pts) ...", end="", flush=True)
        T_truc, b_truc, sT_truc, sb_truc, c2_truc, ok_truc = fit_bgbw(pt_t, y_t, e_t, "trunc")
        print(f" T={T_truc:.1f} MeV, beta_s={b_truc:.3f}, chi2/ndf={c2_truc:.1f}")

        delta_T = T_truc - T_full
        sigma_combined_T = math.sqrt(sT_full**2 + sT_truc**2) if (math.isfinite(sT_full) and math.isfinite(sT_truc)) else float('nan')
        nsigma_T = abs(delta_T) / sigma_combined_T if sigma_combined_T > 0 else float('nan')

        delta_bs = b_truc - b_full
        sigma_combined_bs = math.sqrt(sb_full**2 + sb_truc**2) if (math.isfinite(sb_full) and math.isfinite(sb_truc)) else float('nan')
        nsigma_bs = abs(delta_bs) / sigma_combined_bs if sigma_combined_bs > 0 else float('nan')

        flagged = (not math.isnan(nsigma_T)  and nsigma_T  > 2.0) or \
                  (not math.isnan(nsigma_bs) and nsigma_bs > 2.0)
        flag = "FIT-RANGE-DEPENDENT" if flagged else "stable"

        if flagged:
            print(f"    *** FLAG: {flag} — ΔT={delta_T:+.1f} MeV ({nsigma_T:.1f}σ), "
                  f"Δβ_s={delta_bs:+.3f} ({nsigma_bs:.1f}σ)")

        rows_out.append({
            'bin_label': bin_label,
            'n_full': len(full), 'n_trunc': len(trunc),
            'T_full_MeV': f"{T_full:.2f}", 'beta_s_full': f"{b_full:.4f}",
            'sigma_T_full': f"{sT_full:.2f}", 'sigma_beta_s_full': f"{sb_full:.4f}",
            'chi2_ndf_full': f"{c2_full:.3f}", 'conv_full': int(ok_full),
            'T_trunc_MeV': f"{T_truc:.2f}", 'beta_s_trunc': f"{b_truc:.4f}",
            'sigma_T_trunc': f"{sT_truc:.2f}", 'sigma_beta_s_trunc': f"{sb_truc:.4f}",
            'chi2_ndf_trunc': f"{c2_truc:.3f}", 'conv_trunc': int(ok_truc),
            'delta_T_MeV': f"{delta_T:+.2f}", 'delta_T_nsigma': f"{nsigma_T:.2f}",
            'delta_beta_s': f"{delta_bs:+.4f}", 'delta_beta_s_nsigma': f"{nsigma_bs:.2f}",
            'flag': flag,
        })

    # Write CSV
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    fieldnames = header.split(',')
    with open(OUT_PATH, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"\n=== SUMMARY ===")
    print(f"Results written to: {OUT_PATH}")
    print()
    n_flagged = sum(1 for r in rows_out if r['flag'] == 'FIT-RANGE-DEPENDENT')
    print(f"Bins flagged as fit-range dependent: {n_flagged}/{len(rows_out)}")
    print()
    print(f"{'Bin':<12} {'T_full':>8} {'T_trunc':>8} {'ΔT':>8} {'nσ_T':>6} {'β_full':>8} {'β_trunc':>8} {'Δβ':>8} {'nσ_β':>6} {'Flag'}")
    print("-"*90)
    for r in rows_out:
        print(f"{r['bin_label']:<12} {r['T_full_MeV']:>8} {r['T_trunc_MeV']:>8} "
              f"{r['delta_T_MeV']:>8} {r['delta_T_nsigma']:>6} "
              f"{r['beta_s_full']:>8} {r['beta_s_trunc']:>8} "
              f"{r['delta_beta_s']:>8} {r['delta_beta_s_nsigma']:>6} "
              f"  {r['flag']}")


if __name__ == '__main__':
    main()
