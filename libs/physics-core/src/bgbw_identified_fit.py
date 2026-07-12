#!/usr/bin/env python3
"""
bgbw_identified_fit.py — C2 scaffold for issue #27.

Addresses the pion-mass assumption caveat: bgbw_fit.py fits unidentified
charged hadrons with m = m_π = 0.13957 GeV, which biases T_kin slightly low
and ⟨β⟩ slightly high because K/p contributions at high pT are under-weighted.

Resolution strategy
-------------------
The ideal fix is a joint π/K/p fit against HEPData ins1682316 (ALICE pp 7 TeV
identified spectra, doi:10.17182/hepdata.64522). Since pp 13 TeV identified
spectra with matching multiplicity classes are not yet public (as of 2026-07),
this script implements a two-level fallback:

  Level 1 (preferred): Load ins1682316 identified spectra (π/K/p), fit each
      species independently with per-species mass, extract (T_kin, ⟨β⟩) pair.

  Level 2 (fallback): Mass-weighted bias estimate from the existing
      unidentified data (ins1735345). Refit the same data three times using
      m_π, m_K, m_p; the spread in T_kin illustrates the pion-mass bias
      without requiring external data.  Labelled "pion-mass bias estimate —
      not a true identified-species refit".

Usage
-----
    # Level 1 (if ins1682316 data available):
    python libs/physics-core/src/bgbw_identified_fit.py \\
        --run-dir research/robert/runs/2026-07-08-bgbw-identified-species \\
        --data-path libs/physics-core/data/fit_input_ins1682316.csv

    # Level 2 fallback (always works):
    python libs/physics-core/src/bgbw_identified_fit.py \\
        --run-dir research/robert/runs/2026-07-08-bgbw-identified-species \\
        --fallback

References
----------
- ins1682316: ALICE pp 7 TeV identified hadrons (arXiv:1601.03658)
- ins1735345: ALICE pp 13 TeV unidentified charged hadrons (arXiv:1905.07208)
- Khuntia+ 2019: BGBW vs multiplicity, pp √s=7 TeV (arXiv:1808.02383)
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from iminuit import Minuit
from iminuit.cost import LeastSquares
from scipy.integrate import quad
from scipy.special import i0e, k1e

_SRC = Path(__file__).parent
sys.path.insert(0, str(_SRC))

try:
    import matplotlib.pyplot as plt
    _HAS_MPL = True
except ImportError:
    _HAS_MPL = False

# ---------------------------------------------------------------------------
# Particle masses [GeV]
# ---------------------------------------------------------------------------
MASSES = {
    "pion":   0.13957,
    "kaon":   0.49368,
    "proton": 0.93827,
}

DEFAULT_DATA_13TEV = Path(__file__).parent.parent / "data" / "fit_input_ins1735345.csv"

BLAST_WAVE_BOUNDS = {
    "temperature": (0.01, 0.80),
    "beta_s":      (0.00, 0.99),
    "n":           (0.10, 4.00),
}

INIT_GRID = [
    (T, b, n)
    for T in (0.09, 0.13, 0.20)
    for b in (0.30, 0.55, 0.75)
    for n in (0.5, 1.0, 2.0)
]


# ---------------------------------------------------------------------------
# BGBW model (copy to keep this script self-contained)
# ---------------------------------------------------------------------------

def bgbw_scalar(pt: float, norm: float, T: float, beta_s: float,
                n_val: float, mass_gev: float) -> float:
    mt = math.sqrt(mass_gev ** 2 + pt ** 2)

    def integrand(r: float) -> float:
        beta_r = min(beta_s * r ** n_val, 0.999999)
        rho = math.atanh(beta_r)
        arg_i = pt * math.sinh(rho) / T
        arg_k = mt * math.cosh(rho) / T
        return r * mt * i0e(arg_i) * k1e(arg_k) * math.exp(arg_i - arg_k)

    val, _ = quad(integrand, 0.0, 1.0, limit=200)
    return norm * pt * val


def bgbw_vec(pt_arr: np.ndarray, norm: float, T: float, beta_s: float,
             n_val: float, mass_gev: float) -> np.ndarray:
    return np.array([bgbw_scalar(float(p), norm, T, beta_s, n_val, mass_gev)
                     for p in pt_arr])


def mean_beta(beta_s: float, n: float) -> float:
    return 2.0 / (n + 2.0) * beta_s


# ---------------------------------------------------------------------------
# Fit function
# ---------------------------------------------------------------------------

def fit_species(
    pt: np.ndarray,
    y: np.ndarray,
    err: np.ndarray,
    mass_gev: float,
    species: str,
) -> dict[str, Any]:
    norm_guess = float(np.nanmax(y))

    def model(pt_vals: np.ndarray, norm: float, temperature: float,
              beta_s: float, n_val: float) -> np.ndarray:
        return bgbw_vec(pt_vals, norm, temperature, beta_s, n_val, mass_gev)

    best: dict[str, Any] | None = None
    for T0, b0, n0 in INIT_GRID:
        cost = LeastSquares(pt, y, err, model)
        m = Minuit(cost, norm=norm_guess, temperature=T0, beta_s=b0, n_val=n0)
        m.strategy = 1
        m.limits["norm"] = (1e-12, None)
        m.limits["temperature"] = BLAST_WAVE_BOUNDS["temperature"]
        m.limits["beta_s"] = BLAST_WAVE_BOUNDS["beta_s"]
        m.limits["n_val"] = BLAST_WAVE_BOUNDS["n"]
        try:
            m.migrad()
            m.hesse()
        except Exception:
            continue

        ndf = len(pt) - 4
        chi2_ndf = float(m.fval) / ndf if ndf > 0 else None
        result = {
            "species": species,
            "mass_gev": mass_gev,
            "success": bool(m.valid),
            "chi2": float(m.fval),
            "ndf": ndf,
            "chi2_ndf": chi2_ndf,
            "norm": float(m.values["norm"]),
            "temperature_gev": float(m.values["temperature"]),
            "beta_s": float(m.values["beta_s"]),
            "n_val": float(m.values["n_val"]),
            "mean_beta": mean_beta(float(m.values["beta_s"]), float(m.values["n_val"])),
        }
        if best is None or (result["success"] and not best["success"]):
            best = result
        elif result["success"] == best["success"] and result["chi2"] < best.get("chi2", math.inf):
            best = result

    return best or {"species": species, "success": False, "error": "no convergence"}


# ---------------------------------------------------------------------------
# Fallback: mass-weighted bias estimate from ins1735345
# ---------------------------------------------------------------------------

def run_fallback(run_dir: Path, data_path: Path) -> list[dict[str, Any]]:
    """Refit ins1735345 with m_π, m_K, m_p per multiplicity bin.

    Produces a delta table showing how T_kin and ⟨β⟩ change with mass
    assumption.  This is a pion-mass BIAS ESTIMATE, not a true identified
    species refit.
    """
    df = pd.read_csv(data_path)
    bins = sorted(df["manuscript_bin"].dropna().unique(),
                  key=lambda b: int(str(b).split("-")[0]))

    rows = []
    for bin_label in bins:
        sub = df[df["manuscript_bin"] == bin_label].sort_values("pt_center_gev")
        pt = sub["pt_center_gev"].to_numpy(float)
        y = sub["yield_value"].to_numpy(float)
        err = sub["total_error"].to_numpy(float)

        bin_row: dict[str, Any] = {"bin": bin_label, "n_points": len(pt)}
        for species, mass in MASSES.items():
            res = fit_species(pt, y, err, mass, species)
            bin_row[f"T_kin_{species}_gev"] = res.get("temperature_gev")
            bin_row[f"mean_beta_{species}"] = res.get("mean_beta")
            bin_row[f"chi2_ndf_{species}"] = res.get("chi2_ndf")
            bin_row[f"success_{species}"] = res.get("success")

        # Bias = difference from pion baseline
        T_pi = bin_row.get("T_kin_pion_gev") or float("nan")
        T_p = bin_row.get("T_kin_proton_gev") or float("nan")
        bin_row["delta_T_kin_proton_vs_pion_gev"] = T_p - T_pi
        rows.append(bin_row)

        print(f"  {bin_label}: T_π={T_pi:.4f}  T_K={bin_row.get('T_kin_kaon_gev', float('nan')):.4f}"
              f"  T_p={T_p:.4f}  ΔT(p-π)={T_p - T_pi:.4f} GeV")

    return rows


# ---------------------------------------------------------------------------
# Level 1: real identified species fit
# ---------------------------------------------------------------------------

def run_identified(run_dir: Path, data_path: Path) -> list[dict[str, Any]]:
    """Fit identified π/K/p spectra from ins1682316 with per-species mass."""
    df = pd.read_csv(data_path)
    species_col = "particle" if "particle" in df.columns else "species"
    if species_col not in df.columns:
        raise ValueError(f"Expected a '{species_col}' column in {data_path}")

    rows = []
    for species in df[species_col].dropna().unique():
        mass = MASSES.get(str(species).lower())
        if mass is None:
            print(f"  Skipping unknown species: {species}")
            continue
        sub = df[df[species_col] == species].sort_values("pt_center_gev")
        pt = sub["pt_center_gev"].to_numpy(float)
        y = sub["yield_value"].to_numpy(float)
        err = sub["total_error"].to_numpy(float)
        res = fit_species(pt, y, err, mass, str(species))
        res["n_points"] = len(pt)
        rows.append(res)
        ok = "✓" if res.get("success") else "✗"
        print(f"  {species}: {ok}  T={res.get('temperature_gev', float('nan')):.4f} GeV"
              f"  ⟨β⟩={res.get('mean_beta', float('nan')):.4f}")
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--data-path", type=Path, default=None,
                   help="Path to identified-species CSV (ins1682316). "
                        "Defaults to fallback mode if not provided.")
    p.add_argument("--fallback", action="store_true",
                   help="Force fallback mode (mass-weighted bias estimate from ins1735345)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = args.run_dir
    run_dir.mkdir(parents=True, exist_ok=True)

    use_fallback = args.fallback or args.data_path is None or not Path(args.data_path).exists()

    if use_fallback:
        mode = "mass-weighted bias estimate (fallback)"
        print(f"\nRunning C2 {mode}")
        print("(ins1682316 not found locally — using ins1735345 with m_π/m_K/m_p)")
        rows = run_fallback(run_dir, DEFAULT_DATA_13TEV)
        data_label = "ins1735345 (unidentified, mass-varied)"
        caveat_c2 = ("Level-2 fallback: refit of unidentified hadrons with three mass "
                     "assumptions. NOT a true identified-species refit. Obtain ins1682316 "
                     "and re-run with --data-path for a Level-1 result.")
    else:
        mode = "identified species (Level 1)"
        print(f"\nRunning C2 {mode}")
        rows = run_identified(run_dir, Path(args.data_path))
        data_label = str(args.data_path)
        caveat_c2 = "Level-1 identified-species refit. Verify against published ALICE results."

    # Write CSV
    csv_path = run_dir / "fit_results.csv"
    if rows:
        with open(csv_path, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
    print(f"\nResults written to {csv_path}")

    # Write JSON summary
    summary = {
        "mode": mode,
        "data": data_label,
        "caveat_c2": caveat_c2,
        "n_rows": len(rows),
        "results": rows,
    }
    (run_dir / "fit_results.json").write_text(json.dumps(summary, indent=2, default=str))

    # Bias summary table (fallback mode)
    if use_fallback and rows:
        print("\n--- Pion-mass bias table ---")
        print(f"{'Bin':>10}  {'T_π [GeV]':>12}  {'T_K [GeV]':>12}  {'T_p [GeV]':>12}  {'ΔT(p-π) [GeV]':>14}")
        print("-" * 66)
        for r in rows:
            print(f"{r['bin']:>10}"
                  f"  {r.get('T_kin_pion_gev', float('nan')):>12.4f}"
                  f"  {r.get('T_kin_kaon_gev', float('nan')):>12.4f}"
                  f"  {r.get('T_kin_proton_gev', float('nan')):>12.4f}"
                  f"  {r.get('delta_T_kin_proton_vs_pion_gev', float('nan')):>14.4f}")


if __name__ == "__main__":
    main()
