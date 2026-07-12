#!/usr/bin/env python3
"""
bgbw_fit.py — Standalone BGBW per-multiplicity-class fit script.

Addresses issue #27: BGBW per-class fit caveats (SPD-tracklets estimator,
pion-mass assumption, missing covariance).

Reads libs/physics-core/data/fit_input_ins1735345.csv (HEPData ins1735345, 10 manuscript
multiplicity classes, SPD-tracklets estimator, |η| < 0.8, pp √s = 13 TeV).

Runs the Boltzmann-Gibbs Blast-Wave (BGBW/SSH) model:
    dN/(pT dpT) ∝ ∫₀¹ r dr · mT · I₀(pT sinh ρ / T) · K₁(mT cosh ρ / T)
with beta_r = beta_s · r^n.

Fitted parameters per class: norm, T_kin [GeV], beta_s (surface flow), n (profile).
Derived: ⟨β⟩ = 2/(n+2) · beta_s  (flat velocity profile moment).

--cov-mode diag (default): standard diagonal χ²
--cov-mode correlated     : GLS χ² with parametric covariance envelope (C3)

Usage
-----
    python libs/physics-core/src/bgbw_fit.py \\
        --run-dir research/robert/runs/2026-07-08-bgbw-per-class \\
        --cov-mode diag

    python libs/physics-core/src/bgbw_fit.py \\
        --run-dir research/robert/runs/2026-07-08-bgbw-gls \\
        --cov-mode correlated --xi 1.0

References
----------
- SSH 1993: Schnedermann, Sollfrank, Heinz, Phys.Rev.C 48:2462 (nucl-th/9307020)
- Khuntia+ 2019: Eur.Phys.J.A (arXiv:1808.02383) — BGBW vs multiplicity pp 7 TeV
- HEPData ins1735345: doi:10.17182/hepdata.91996.v2
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

# Sibling imports
_SRC = Path(__file__).parent
sys.path.insert(0, str(_SRC))
from bgbw_covariance import build_covariance, chi2_envelope, CORRELATION_LENGTHS  # noqa: E402

try:
    import matplotlib.pyplot as plt
    _HAS_MPL = True
except ImportError:
    _HAS_MPL = False

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_DATA_PATH = Path(__file__).parent.parent / "data" / "fit_input_ins1735345.csv"
DEFAULT_MASS_GEV = 0.13957  # pion mass — see C2 caveat in issue #27

BLAST_WAVE_BOUNDS = {
    "temperature": (0.01, 0.80),  # T_kin [GeV]
    "beta_s":      (0.00, 0.99),  # surface flow velocity
    "n":           (0.10, 4.00),  # velocity profile exponent
}

INIT_GRID = [
    (T, b, n)
    for T in (0.10, 0.15, 0.20)
    for b in (0.40, 0.65)
    for n in (0.8, 2.0)
]


# ---------------------------------------------------------------------------
# BGBW model
# ---------------------------------------------------------------------------

def mean_beta(beta_s: float, n: float) -> float:
    """⟨β⟩ = 2/(n+2) · beta_s  (flat linear profile n=1 → ⟨β⟩ = beta_s/1.5)."""
    return 2.0 / (n + 2.0) * beta_s


def bgbw_scalar(
    pt: float,
    norm: float,
    temperature: float,
    beta_s: float,
    n_val: float,
    mass_gev: float = DEFAULT_MASS_GEV,
) -> float:
    """BGBW integrand dN/(pT dpT) for a single pT value."""
    mt = math.sqrt(mass_gev ** 2 + pt ** 2)

    def integrand(r: float) -> float:
        beta_r = min(beta_s * r ** n_val, 0.999999)
        rho = math.atanh(beta_r)
        arg_i = pt * math.sinh(rho) / temperature
        arg_k = mt * math.cosh(rho) / temperature
        return r * mt * i0e(arg_i) * k1e(arg_k) * math.exp(arg_i - arg_k)

    val, _ = quad(integrand, 0.0, 1.0, limit=200)
    return norm * pt * val


def bgbw_vec(
    pt_arr: np.ndarray,
    norm: float,
    temperature: float,
    beta_s: float,
    n_val: float,
    mass_gev: float = DEFAULT_MASS_GEV,
) -> np.ndarray:
    return np.array([bgbw_scalar(float(p), norm, temperature, beta_s, n_val, mass_gev) for p in pt_arr])


# ---------------------------------------------------------------------------
# Fit helpers
# ---------------------------------------------------------------------------

def fit_bin(
    pt: np.ndarray,
    y: np.ndarray,
    err: np.ndarray,
    mass_gev: float = DEFAULT_MASS_GEV,
    cov_mode: str = "diag",
    stat: np.ndarray | None = None,
    sys_err: np.ndarray | None = None,
    xi: float = 1.0,
) -> dict[str, Any]:
    """Fit one multiplicity bin with BGBW.

    Parameters
    ----------
    pt       : pT bin centres [GeV]
    y        : yield values
    err      : total uncertainty (used for diag mode)
    mass_gev : particle mass assumption [GeV]
    cov_mode : 'diag' or 'correlated'
    stat     : statistical uncertainties (needed for correlated mode)
    sys_err  : systematic uncertainties (needed for correlated mode)
    xi       : correlation length for correlated mode
    """
    norm_guess = float(np.nanmax(y))

    try:
        import jax
        import jax.numpy as jnp
        from bgbw_jax_autodiff import bgbw_likelihood
        jax.config.update("jax_enable_x64", True)
        jpt = jnp.array(pt, dtype=jnp.float64)
        jy = jnp.array(y, dtype=jnp.float64)
        jerr = jnp.array(err, dtype=jnp.float64)
        grad_fn = jax.grad(bgbw_likelihood)
        
        def jax_cost(norm: float, temperature: float, beta_s: float, n_val: float) -> float:
            return float(bgbw_likelihood(jnp.array([norm, temperature, beta_s, n_val]), jpt, jy, jerr, mass_gev))
            
        def jax_grad(norm: float, temperature: float, beta_s: float, n_val: float) -> np.ndarray:
            return np.array(grad_fn(jnp.array([norm, temperature, beta_s, n_val]), jpt, jy, jerr, mass_gev))

        cost_func = jax_cost
        grad_func = jax_grad
    except ImportError:
        def model(pt_vals: np.ndarray, norm: float, temperature: float, beta_s: float, n_val: float) -> np.ndarray:
            return bgbw_vec(pt_vals, norm, temperature, beta_s, n_val, mass_gev)
        cost_func = LeastSquares(pt, y, err, model)
        grad_func = None

    best: dict[str, Any] | None = None

    for T0, b0, n0 in INIT_GRID:
        if grad_func is not None:
            m = Minuit(cost_func, norm=norm_guess, temperature=T0, beta_s=b0, n_val=n0, grad=grad_func)
        else:
            m = Minuit(cost_func, norm=norm_guess, temperature=T0, beta_s=b0, n_val=n0)
        m.errordef = Minuit.LEAST_SQUARES
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

        chi2 = float(m.fval)
        ndf = len(pt) - 4
        chi2_ndf = chi2 / ndf if ndf > 0 else None

        result = {
            "success": bool(m.valid),
            "chi2": chi2,
            "ndf": ndf,
            "chi2_ndf": chi2_ndf,
            "norm": float(m.values["norm"]),
            "temperature_gev": float(m.values["temperature"]),
            "beta_s": float(m.values["beta_s"]),
            "n_val": float(m.values["n_val"]),
            "mean_beta": mean_beta(float(m.values["beta_s"]), float(m.values["n_val"])),
            "norm_err": float(m.errors["norm"]),
            "temperature_err_gev": float(m.errors["temperature"]),
            "beta_s_err": float(m.errors["beta_s"]),
            "n_val_err": float(m.errors["n_val"]),
            "valid": bool(m.valid),
        }

        # Augment with GLS envelope if correlated mode
        if cov_mode == "correlated" and stat is not None and sys_err is not None:
            y_pred = bgbw_vec(pt, result["norm"], result["temperature_gev"],
                              result["beta_s"], result["n_val"], mass_gev)
            env = chi2_envelope(pt, stat, sys_err, y, y_pred, n_params=4, xi_values=CORRELATION_LENGTHS)
            result["gls_chi2_ndf_diag"] = env["diag"]
            result["gls_chi2_ndf_envelope"] = env["correlated"]
            result["gls_chi2_ndf_min"] = env["envelope_min"]
            result["gls_chi2_ndf_max"] = env["envelope_max"]

        if best is None or (result["success"] and not best["success"]):
            best = result
            if result["success"]:
                best["minuit_obj"] = m
        elif result["success"] == best["success"] and result["chi2"] < best.get("chi2", math.inf):
            best = result
            best["minuit_obj"] = m

    if best is None:
        return {"success": False, "error": "no convergent seed"}
    return best


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"pt_center_gev", "yield_value", "total_error", "manuscript_bin"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in {path}: {missing}")
    return df


def write_results_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    keys = list(rows[0].keys())
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def plot_bin_fit(
    out_path: Path,
    pt: np.ndarray,
    y: np.ndarray,
    err: np.ndarray,
    result: dict[str, Any],
    bin_label: str,
    mass_gev: float,
) -> None:
    if not _HAS_MPL:
        return
    pt_fine = np.linspace(float(pt.min()), float(pt.max()), 200)
    y_fit = bgbw_vec(pt_fine, result["norm"], result["temperature_gev"],
                     result["beta_s"], result["n_val"], mass_gev)
    fig, axes = plt.subplots(2, 1, figsize=(7, 8))
    axes[0].errorbar(pt, y, yerr=err, fmt="o", ms=4, label="data (ins1735345)")
    axes[0].plot(pt_fine, y_fit, "-", label="BGBW fit")
    axes[0].set_ylabel("dN/(2π pT dpT dη)")
    axes[0].set_title(
        f"BGBW per-class fit — bin {bin_label}\n"
        f"T_kin={result['temperature_gev']:.3f} GeV  ⟨β⟩={result['mean_beta']:.3f}  "
        f"χ²/ndf={result.get('chi2_ndf', '?'):.3f}"
    )
    axes[0].legend(fontsize=8)
    axes[0].set_yscale("log")

    y_pred = bgbw_vec(pt, result["norm"], result["temperature_gev"],
                      result["beta_s"], result["n_val"], mass_gev)
    pulls = (y - y_pred) / np.maximum(err, 1e-30)
    axes[1].axhline(0, color="k", lw=0.8)
    axes[1].axhspan(-1, 1, alpha=0.12, color="green", label="±1σ")
    axes[1].axhspan(-2, 2, alpha=0.06, color="gold", label="±2σ")
    axes[1].scatter(pt, pulls, s=18, zorder=3)
    axes[1].set_ylabel("pull")
    axes[1].set_xlabel("pT [GeV]")
    axes[1].legend(fontsize=7)

    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-dir", type=Path, required=True, help="Output run directory")
    p.add_argument("--data-path", type=Path, default=DEFAULT_DATA_PATH,
                   help="Path to fit_input CSV (default: libs/physics-core/data/fit_input_ins1735345.csv)")
    p.add_argument("--mass-gev", type=float, default=DEFAULT_MASS_GEV,
                   help="Particle mass [GeV] (default: pion mass 0.13957)")
    p.add_argument("--cov-mode", choices=["diag", "correlated"], default="diag",
                   help="Covariance mode: diag=diagonal χ², correlated=GLS envelope (C3)")
    p.add_argument("--contours", action="store_true",
                   help="Generate MINOS contours (slow)")
    p.add_argument("--xi", type=float, default=1.0,
                   help="Correlation length for correlated mode (default: 1.0)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = args.run_dir
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading data from {args.data_path}")
    df = load_data(args.data_path)

    bins = sorted(df["manuscript_bin"].dropna().unique(), key=lambda b: int(str(b).split("-")[0]))
    print(f"Found {len(bins)} multiplicity bins: {bins}")

    fig_contour, ax_contour = None, None
    colors = []
    if _HAS_MPL:
        fig_contour, ax_contour = plt.subplots(figsize=(8, 6))
        colors = plt.cm.viridis(np.linspace(0, 1, len(bins)))

    all_results: list[dict[str, Any]] = []
    csv_path = run_dir / "fit_results.csv"
    written_header = False
    for bin_label in bins:
        sub = df[df["manuscript_bin"] == bin_label].dropna(subset=["pt_center_gev", "yield_value"])
        sub = sub.sort_values("pt_center_gev")

        pt = sub["pt_center_gev"].to_numpy(float)
        y = sub["yield_value"].to_numpy(float)
        err = sub["total_error"].to_numpy(float)
        stat = sub["stat_error"].to_numpy(float) if "stat_error" in sub.columns else err * 0.1
        sys_e = sub["sys_error"].to_numpy(float) if "sys_error" in sub.columns else err * 0.9

        print(f"  Fitting bin {bin_label} ({len(pt)} points) [cov_mode={args.cov_mode}]...", end=" ", flush=True)
        result = fit_bin(pt, y, err, mass_gev=args.mass_gev,
                         cov_mode=args.cov_mode, stat=stat, sys_err=sys_e, xi=args.xi)
        result["bin"] = bin_label
        result["n_points"] = len(pt)
        result["mass_gev"] = args.mass_gev
        result["cov_mode"] = args.cov_mode
        result["estimator"] = "SPD_tracklets"  # C1 caveat
        result["status"] = "substitute-baseline"  # until C1/C2/C3 resolved
        all_results.append(result)

        # Incremental save so partial runs aren't lost
        with open(csv_path, "a", newline="") as fh:
            import csv as _csv
            writer = _csv.DictWriter(fh, fieldnames=list(result.keys()), extrasaction="ignore")
            if not written_header:
                writer.writeheader()
                written_header = True
            writer.writerow(result)

        status = "✓" if result.get("success") else "✗"
        chi2_str = f"χ²/ndf={result.get('chi2_ndf', '?'):.3f}" if result.get("chi2_ndf") else ""
        T_str = f"T={result.get('temperature_gev', '?'):.3f} GeV" if result.get("temperature_gev") else ""
        b_str = f"⟨β⟩={result.get('mean_beta', '?'):.3f}" if result.get("mean_beta") else ""
        print(f"{status}  {T_str}  {b_str}  {chi2_str}")

        # Plot
        if result.get("success"):
            plot_bin_fit(
                run_dir / f"fit_bin_{bin_label.replace('-', '_')}.png",
                pt, y, err, result, bin_label, args.mass_gev,
            )
            
            # MINOS Contour Plot
            if args.contours and _HAS_MPL and ax_contour is not None and "minuit_obj" in result:
                m_best = result["minuit_obj"]
                color = colors[bins.index(bin_label)]
                try:
                    pts_68 = m_best.mncontour("temperature", "beta_s", cl=0.68, size=15)
                    ax_contour.plot(pts_68[:, 0], pts_68[:, 1], "-", color=color, label=f"Bin {bin_label}")
                    pts_95 = m_best.mncontour("temperature", "beta_s", cl=0.95, size=15)
                    ax_contour.plot(pts_95[:, 0], pts_95[:, 1], "--", color=color, alpha=0.7)
                except Exception as e:
                    print(f"\n  [Warning] MINOS contour failed for bin {bin_label}: {e}")
                    
            # Remove minuit obj so it doesn't break JSON serialization later
            result.pop("minuit_obj", None)

    # CSV was written incrementally per bin above
    print(f"\nResults written to {csv_path}")

    if args.contours and fig_contour is not None and ax_contour is not None:
        ax_contour.set_xlabel("T_kin [GeV]")
        ax_contour.set_ylabel("beta_s")
        ax_contour.set_title("BGBW Profile Likelihood Contours (T_kin vs beta_s)")
        ax_contour.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        fig_contour.tight_layout()
        fig_contour.savefig(run_dir / "bgbw_contours.png", dpi=120)
        plt.close(fig_contour)
        print(f"MINOS contour plot written to {run_dir / 'bgbw_contours.png'}")

    # Write JSON summary
    summary = {
        "source": "ins1735345",
        "estimator": "SPD_tracklets",
        "eta_range": "-0.8-0.8",
        "sqrt_s_gev": 13000,
        "model": "BGBW (Schnedermann-Sollfrank-Heinz 1993)",
        "mass_gev": args.mass_gev,
        "mass_assumption": "pion (C2 caveat: biases T low, <beta> high for unidentified hadrons)",
        "cov_mode": args.cov_mode,
        "status": "substitute-baseline",
        "caveats": {
            "C1": "SPD-tracklets estimator != manuscript Nch; identity R matrix used",
            "C2": f"mass={args.mass_gev} GeV (pion); see bgbw_identified_fit.py for species refit",
            "C3": "Full covariance unavailable; chi2/ndf is shape-quality proxy only"
                  + (" — GLS envelope computed" if args.cov_mode == "correlated" else ""),
        },
        "n_bins": len(all_results),
        "n_converged": sum(1 for r in all_results if r.get("success")),
        "bins": all_results,
    }
    json_path = run_dir / "fit_results.json"
    json_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"JSON summary written to {json_path}")

    # Print delta table
    print("\n--- Per-bin results ---")
    print(f"{'Bin':>10}  {'T_kin [GeV]':>12}  {'⟨β⟩':>8}  {'χ²/ndf':>8}  {'OK?':>5}")
    print("-" * 52)
    for r in all_results:
        ok = "✓" if r.get("success") else "✗"
        t = r.get("temperature_gev", float("nan"))
        b = r.get("mean_beta", float("nan"))
        c = r.get("chi2_ndf", float("nan"))
        print(f"{r['bin']:>10}  {t:>12.4f}  {b:>8.4f}  {c:>8.4f}  {ok:>5}")


if __name__ == "__main__":
    main()
