
from __future__ import annotations
import json
import math
import warnings
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

import numpy as np
import pandas as pd
from iminuit import Minuit
from iminuit.cost import LeastSquares
from scipy.integrate import quad
from scipy.optimize import differential_evolution
from scipy.special import i0, k1, i0e, k1e

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

DEFAULT_MASS_GEV = 0.13957

from models import (
    manuscript_component_scalar, bose_component_scalar, eta_integral, safe_exp,
    tsallis_component_scalar, static_tsallis_limit, blast_wave_component_scalar
)
from fitting.metrics import FormulaConfirmation, confirm_manuscript_formula, write_json

DEFAULT_MANUSCRIPT_BOUNDS = {
    "temperature": (0.01, 2.0),
    "U": (0.0, 3.0),
}
DEFAULT_TSALLIS_BOUNDS = {
    "temperature": (0.01, 1.5),
    "q": (1.001, 2.0),
}
DEFAULT_BLAST_WAVE_BOUNDS = {
    "temperature": (0.01, 0.8),
    "beta_s": (0.0, 0.99),
    "n": (0.1, 4.0),
}
@dataclass(frozen=True)
class FitSpec:
    model_name: str
    component_count: int
    parameter_names: list[str]
    parameter_bounds: dict[str, tuple[float | None, float | None]]
    fixed_metadata: dict[str, Any]
    model_callable: Callable[[np.ndarray, float], np.ndarray]
    initial_grid_builder: Callable[[np.ndarray, np.ndarray], list[tuple[float, ...]]]

def load_mapping_validation(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "hepdata_mapping_validation.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing mapping validation artifact: {path}")
    return json.loads(path.read_text())

def load_fit_input(run_dir: Path) -> pd.DataFrame:
    path = run_dir / "fit_input.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing fit input: {path}")
    return pd.read_csv(path)

def vectorize_scalar_model(
    scalar_model: Callable[..., float],
    parameter_chunks: list[tuple[str, ...]],
    eta_max: float | None,
    mass_gev: float,
) -> Callable[[np.ndarray, float], np.ndarray]:
    def model(pt_values: np.ndarray, *params: float) -> np.ndarray:
        pt_array = np.asarray(pt_values, dtype=float)
        outputs = []
        for pt in pt_array:
            total = 0.0
            param_index = 0
            for chunk in parameter_chunks:
                chunk_values = params[param_index : param_index + len(chunk)]
                param_index += len(chunk)
                if eta_max is None:
                    total += scalar_model(float(pt), *chunk_values, mass_gev)
                else:
                    total += scalar_model(float(pt), *chunk_values, eta_max, mass_gev)
            outputs.append(total)
        return np.asarray(outputs, dtype=float)

    return model

def build_initial_grid(
    component_count: int,
    parameter_order: Iterable[str],
    y_values: np.ndarray,
    temperature_guesses: tuple[float, ...],
    third_parameter_guesses: tuple[float, ...],
) -> list[tuple[float, ...]]:
    max_y = float(np.nanmax(y_values))
    norm_base = max(max_y, 1e-9)
    component_scales = {
        1: (1.0,),
        2: (0.7, 0.3),
        3: (0.55, 0.30, 0.15),
    }[component_count]

    grids: list[tuple[float, ...]] = []
    for base_temperature in temperature_guesses:
        for base_third in third_parameter_guesses:
            candidate: list[float] = []
            for component_index in range(component_count):
                for parameter_name in parameter_order:
                    if parameter_name == "norm":
                        candidate.append(norm_base * component_scales[component_index])
                    elif parameter_name == "temperature":
                        candidate.append(base_temperature * (1.0 + 0.12 * component_index))
                    else:
                        candidate.append(base_third * (1.0 + 0.10 * component_index))
            grids.append(tuple(candidate))

    return grids

def manuscript_fit_spec(component_count: int, eta_max: float, mass_gev: float) -> FitSpec:
    parameter_chunks = [("norm", "temperature", "U")] * component_count
    parameter_names = [
        f"{name}_{index + 1}"
        for index in range(component_count)
        for name in ("norm", "temperature", "U")
    ]
    parameter_bounds = {
        # AIS-61: 1e-12 lower bound prevents degenerate norm=0 solution (component collapse).
        # Was 0.0, which allowed Minuit to zero-out a component trivially.
        name: (1e-12, None) if name.startswith("norm_") else DEFAULT_MANUSCRIPT_BOUNDS["temperature"]
        if name.startswith("temperature_")
        else DEFAULT_MANUSCRIPT_BOUNDS["U"]
        for name in parameter_names
    }
    return FitSpec(
        model_name=f"juttner_{component_count}c",
        component_count=component_count,
        parameter_names=parameter_names,
        parameter_bounds=parameter_bounds,
        fixed_metadata={"eta_max": eta_max, "mass_gev": mass_gev},
        model_callable=vectorize_scalar_model(
            manuscript_component_scalar, parameter_chunks, eta_max, mass_gev
        ),
        initial_grid_builder=lambda x, y: build_initial_grid(
            component_count,
            ("norm", "temperature", "U"),
            y,
            temperature_guesses=(0.12, 0.22, 0.45),
            third_parameter_guesses=(0.2, 0.6, 1.2),
        ),
    )

def bose_fit_spec(component_count: int, eta_max: float, mass_gev: float) -> FitSpec:
    parameter_chunks = [("norm", "temperature", "U")] * component_count
    parameter_names = [
        f"{name}_{index + 1}"
        for index in range(component_count)
        for name in ("norm", "temperature", "U")
    ]
    parameter_bounds = {
        # AIS-61: 1e-12 lower bound prevents degenerate norm=0 solution.
        name: (1e-12, None) if name.startswith("norm_") else DEFAULT_MANUSCRIPT_BOUNDS["temperature"]
        if name.startswith("temperature_")
        else DEFAULT_MANUSCRIPT_BOUNDS["U"]
        for name in parameter_names
    }
    return FitSpec(
        model_name=f"bose_{component_count}c",
        component_count=component_count,
        parameter_names=parameter_names,
        parameter_bounds=parameter_bounds,
        fixed_metadata={"eta_max": eta_max, "mass_gev": mass_gev},
        model_callable=vectorize_scalar_model(bose_component_scalar, parameter_chunks, eta_max, mass_gev),
        initial_grid_builder=lambda x, y: build_initial_grid(
            component_count,
            ("norm", "temperature", "U"),
            y,
            temperature_guesses=(0.10, 0.18, 0.35),
            third_parameter_guesses=(0.1, 0.5, 0.9),
        ),
    )

def tsallis_fit_spec(component_count: int, eta_max: float, mass_gev: float) -> FitSpec:
    parameter_chunks = [("norm", "temperature", "q")] * component_count
    parameter_names = [
        f"{name}_{index + 1}"
        for index in range(component_count)
        for name in ("norm", "temperature", "q")
    ]
    parameter_bounds = {
        # AIS-61: 1e-12 lower bound prevents degenerate norm=0 solution.
        name: (1e-12, None) if name.startswith("norm_") else DEFAULT_TSALLIS_BOUNDS["temperature"]
        if name.startswith("temperature_")
        else DEFAULT_TSALLIS_BOUNDS["q"]
        for name in parameter_names
    }
    return FitSpec(
        model_name=f"tsallis_{component_count}c",
        component_count=component_count,
        parameter_names=parameter_names,
        parameter_bounds=parameter_bounds,
        fixed_metadata={"eta_max": eta_max, "mass_gev": mass_gev},
        model_callable=vectorize_scalar_model(tsallis_component_scalar, parameter_chunks, eta_max, mass_gev),
        initial_grid_builder=lambda x, y: build_initial_grid(
            component_count,
            ("norm", "temperature", "q"),
            y,
            temperature_guesses=(0.08, 0.14, 0.22),
            third_parameter_guesses=(1.05, 1.12, 1.20),
        ),
    )

def blast_wave_fit_spec(component_count: int, mass_gev: float) -> FitSpec:
    parameter_chunks = [("norm", "temperature", "beta_s", "n")] * component_count
    parameter_names = [
        f"{name}_{index + 1}"
        for index in range(component_count)
        for name in ("norm", "temperature", "beta_s", "n")
    ]
    parameter_bounds: dict[str, tuple[float | None, float | None]] = {}
    for name in parameter_names:
        if name.startswith("norm_"):
            parameter_bounds[name] = (1e-12, None)  # AIS-61: was (0.0, None)
        elif name.startswith("temperature_"):
            parameter_bounds[name] = DEFAULT_BLAST_WAVE_BOUNDS["temperature"]
        elif name.startswith("beta_s_"):
            parameter_bounds[name] = DEFAULT_BLAST_WAVE_BOUNDS["beta_s"]
        else:
            parameter_bounds[name] = DEFAULT_BLAST_WAVE_BOUNDS["n"]

    def initial_grid(x: np.ndarray, y: np.ndarray) -> list[tuple[float, ...]]:
        grids = []
        norm_base = float(np.max(y)) if len(y) > 0 else 1.0
        # 1-component uses simpler logic, multi-component applies scales
        if component_count == 1:
            for t_guess in (0.08, 0.12, 0.16):
                for beta_guess in (0.3, 0.6, 0.8):
                    for n_guess in (0.5, 1.0, 2.0):
                        grids.append((norm_base, t_guess, beta_guess, n_guess))
        else:
            base_temperature = 0.10
            base_beta = 0.4
            base_n = 1.0
            component_scales = [1.0, 0.1, 0.01][:component_count]
            for param_idx in range(3):
                for sub_idx in range(3):
                    candidate = []
                    for idx in range(component_count):
                        candidate.extend(
                            [
                                norm_base * component_scales[idx],
                                base_temperature * (1.0 + 0.10 * idx),
                                min(base_beta * (1.0 + 0.08 * idx), 0.95),
                                base_n * (1.0 + 0.20 * idx),
                            ]
                        )
                    grids.append(tuple(candidate))
        return grids

    return FitSpec(
        model_name="bgbw" if component_count == 1 else f"bgbw_{component_count}c",
        component_count=component_count,
        parameter_names=parameter_names,
        parameter_bounds=parameter_bounds,
        fixed_metadata={"mass_gev": mass_gev},
        model_callable=vectorize_scalar_model(blast_wave_component_scalar, parameter_chunks, None, mass_gev),
        initial_grid_builder=initial_grid,
    )

def juttner_powerlaw_fit_spec(eta_max: float, mass_gev: float) -> FitSpec:
    from models.powerlaw import powerlaw_component_scalar
    
    parameter_names = ["norm_1", "temperature_1", "U_1", "norm_2", "p0_2", "n_2"]
    
    parameter_bounds = {
        "norm_1": (1e-12, None),
        "temperature_1": DEFAULT_MANUSCRIPT_BOUNDS["temperature"],
        "U_1": DEFAULT_MANUSCRIPT_BOUNDS["U"],
        "norm_2": (1e-12, None),
        "p0_2": (0.1, 10.0),
        "n_2": (2.0, 20.0),
    }

    def model_callable(pt_values: np.ndarray, *params: float) -> np.ndarray:
        norm_1, t_1, u_1, norm_2, p0_2, n_2 = params
        pt_array = np.asarray(pt_values, dtype=float)
        outputs = []
        for pt in pt_array:
            val1 = manuscript_component_scalar(float(pt), norm_1, t_1, u_1, eta_max, mass_gev)
            val2 = powerlaw_component_scalar(float(pt), norm_2, p0_2, n_2)
            outputs.append(val1 + val2)
        return np.asarray(outputs, dtype=float)

    def initial_grid(x: np.ndarray, y: np.ndarray) -> list[tuple[float, ...]]:
        max_y = float(np.max(y)) if len(y) > 0 else 1.0
        norm_base = max(max_y, 1e-9)
        return [
            (norm_base * 0.8, 0.12, 0.4, norm_base * 0.1, 1.0, 5.0),
            (norm_base * 0.8, 0.16, 0.6, norm_base * 0.1, 1.5, 7.0),
        ]

    return FitSpec(
        model_name="juttner_powerlaw",
        component_count=2,
        parameter_names=parameter_names,
        parameter_bounds=parameter_bounds,
        fixed_metadata={"eta_max": eta_max, "mass_gev": mass_gev},
        model_callable=model_callable,
        initial_grid_builder=initial_grid,
    )

def build_fit_specs(eta_max: float, mass_gev: float) -> list[FitSpec]:
    specs: list[FitSpec] = []
    for component_count in (1, 2):
        specs.append(manuscript_fit_spec(component_count, eta_max, mass_gev))
        specs.append(bose_fit_spec(component_count, eta_max, mass_gev))
        specs.append(tsallis_fit_spec(component_count, eta_max, mass_gev))
        specs.append(blast_wave_fit_spec(component_count, mass_gev))
    specs.append(juttner_powerlaw_fit_spec(eta_max, mass_gev))
    return specs

def fit_one_spec(
    spec: FitSpec,
    x_values: np.ndarray,
    y_values: np.ndarray,
    y_errors: np.ndarray,
) -> dict[str, Any]:
    least_squares = LeastSquares(x_values, y_values, y_errors, spec.model_callable)
    # 1. Prepare finite bounds for differential_evolution
    finite_bounds = []
    max_y = float(np.max(y_values)) if len(y_values) > 0 else 1.0
    for name in spec.parameter_names:
        low, high = spec.parameter_bounds.get(name, (0.0, None))
        if low is None:
            low = 0.0
        if high is None:
            if name.startswith("norm_"):
                high = max(max_y * 100.0, 1.0)
            else:
                high = 100.0
        finite_bounds.append((low, high))

    # 2. Run Global Optimization (Genetic Algorithm)
    try:
        ga_result = differential_evolution(
            lambda x: least_squares(*x),
            bounds=finite_bounds,
            strategy='best1bin',
            maxiter=100,
            popsize=15,
            tol=0.01,
        )
        best_initial = ga_result.x
    except Exception as exc:
        return {
            "seed_index": 1,
            "success": False,
            "error": f"GA failed: {str(exc)}",
        }

    # 3. Local Refinement with Minuit
    minuit = Minuit(least_squares, *best_initial, name=spec.parameter_names)
    minuit.strategy = 1
    for parameter_name, bounds in spec.parameter_bounds.items():
        minuit.limits[parameter_name] = bounds
    try:
        minuit.migrad()
        minuit.hesse()
    except Exception as exc:  # pragma: no cover - diagnostic path
        return {
            "seed_index": 1,
            "success": False,
            "error": str(exc),
        }
    else:
        parameter_values = {name: float(minuit.values[name]) for name in spec.parameter_names}
        parameter_errors = {
            name: float(minuit.errors[name]) if math.isfinite(minuit.errors[name]) else None
            for name in spec.parameter_names
        }
        covariance_matrix = None
        correlation_matrix = None
        has_covariance = bool(minuit.covariance is not None)
        if has_covariance:
            covariance_matrix = np.asarray(minuit.covariance, dtype=float)
            diag = np.sqrt(np.clip(np.diag(covariance_matrix), a_min=0.0, a_max=None))
            outer = np.outer(diag, diag)
            with np.errstate(divide="ignore", invalid="ignore"):
                correlation_matrix = np.divide(
                    covariance_matrix,
                    outer,
                    out=np.zeros_like(covariance_matrix),
                    where=outer != 0.0,
                )

        chi2 = float(minuit.fval)
        n_parameters = len(spec.parameter_names)
        ndf = int(len(x_values) - n_parameters)
        chi2_ndf = chi2 / ndf if ndf > 0 else None

        # FIX 2: flag unconstrained parameters including those converged to zero.
        # Also flag when err is None — Minuit failed to estimate the uncertainty,
        # which means the parameter is unconstrained / the fit is degenerate.
        fit_quality_flag = "ok"
        if chi2_ndf is not None and chi2_ndf > 5:
            fit_quality_flag = "poor"
        for k in spec.parameter_names:
            err = parameter_errors.get(k)
            val = parameter_values.get(k)
            if err is None:
                # Minuit could not estimate the error: degenerate fit
                fit_quality_flag = "poor"
                break
            if val is not None:
                if val == 0.0 or err / abs(val) > 1:
                    fit_quality_flag = "poor"
                    break

        aic = chi2 + 2 * n_parameters
        bic = chi2 + n_parameters * math.log(len(x_values))
        return {
            "seed_index": 1,
            "success": bool(minuit.valid),
            "chi2": chi2,
            "ndf": ndf,
            "chi2_ndf": chi2_ndf,
            "fit_quality_flag": fit_quality_flag,
            "aic": aic,
            "bic": bic,
            "edm": float(minuit.fmin.edm) if minuit.fmin else None,
            "has_accurate_covar": bool(minuit.fmin.has_accurate_covar) if minuit.fmin else False,
            "parameter_values": parameter_values,
            "parameter_errors": parameter_errors,
            "covariance_matrix": covariance_matrix.tolist() if covariance_matrix is not None else None,
            "correlation_matrix": correlation_matrix.tolist() if correlation_matrix is not None else None,
            "residuals": (y_values - spec.model_callable(x_values, *minuit.values)).tolist(),
            "pulls": (
                (y_values - spec.model_callable(x_values, *minuit.values)) / y_errors
            ).tolist(),
            "model_predictions": spec.model_callable(x_values, *minuit.values).tolist(),
        }

def infer_group_columns(dataframe: pd.DataFrame) -> list[str]:
    for candidate in ("manuscript_bin", "source_table", "eta_range"):
        if candidate in dataframe.columns and dataframe[candidate].notna().any():
            return [candidate]
    return []

def plot_fit_diagnostics(
    output_path: Path,
    x_values: np.ndarray,
    y_values: np.ndarray,
    y_errors: np.ndarray,
    predictions: np.ndarray,
    residuals: np.ndarray,
    pulls: np.ndarray,
    title: str,
) -> None:
    """4-panel diagnostic figure: data+fit, residuals, pulls vs pT, pull histogram."""
    if plt is None:
        raise RuntimeError("matplotlib is not installed")

    from scipy.stats import norm as _sp_norm

    figure, axes = plt.subplots(4, 1, figsize=(8, 13))

    # Panel 0: data + fit
    axes[0].errorbar(x_values, y_values, yerr=y_errors, fmt="o", label="data")
    axes[0].plot(x_values, predictions, label="fit")
    axes[0].set_ylabel("yield")
    axes[0].legend()
    axes[0].set_title(title)

    # Panel 1: residuals
    axes[1].axhline(0.0, color="black", linewidth=0.8)
    axes[1].plot(x_values, residuals, marker="o")
    axes[1].set_ylabel("residual")
    axes[1].set_xlabel("pT [GeV]")

    # Panel 2: pulls vs pT with sigma bands
    axes[2].axhline(0.0, color="black", linewidth=0.8)
    axes[2].axhspan(-1.0, 1.0, alpha=0.12, color="green", label=u"\u00b11\u03c3")
    axes[2].axhspan(-2.0, 2.0, alpha=0.06, color="gold", label=u"\u00b12\u03c3")
    axes[2].scatter(x_values, pulls, s=18, zorder=3)
    axes[2].set_ylabel("pull")
    axes[2].set_xlabel("pT [GeV]")
    axes[2].legend(fontsize=7)

    # Panel 3: 1-D pull histogram + N(0,1) overlay
    if len(pulls) > 1:
        mu_p  = float(np.mean(pulls))
        sig_p = float(np.std(pulls, ddof=1))
        n_bins = max(5, int(np.ceil(np.sqrt(len(pulls)))))
        _, edges, _ = axes[3].hist(
            pulls, bins=n_bins, density=True, alpha=0.65, color="steelblue",
            edgecolor="white", label="pulls"
        )
        x_lin = np.linspace(edges[0] - 0.5, edges[-1] + 0.5, 200)
        axes[3].plot(x_lin, _sp_norm.pdf(x_lin, 0, 1), "k-", lw=1.6, label=r"$\mathcal{N}(0,1)$")
        axes[3].plot(x_lin, _sp_norm.pdf(x_lin, mu_p, max(sig_p, 1e-6)), "r--", lw=1.3,
                     label=rf"fit $\mathcal{{N}}$({mu_p:.2f},{sig_p:.2f})")
        axes[3].set_title(f"Pull histogram  \u03bc={mu_p:.2f}  \u03c3={sig_p:.2f}")
    axes[3].legend(fontsize=7)
    axes[3].set_xlabel("pull")
    axes[3].set_ylabel("density")

    figure.tight_layout()
    figure.savefig(output_path)
    plt.close(figure)

def run_fits(run_dir: Path, fit_input: pd.DataFrame, mass_gev: float) -> dict[str, Any]:
    fit_input = fit_input.copy()
    if "eta_range" not in fit_input.columns:
        raise ValueError("fit_input.csv must include an eta_range column")

    # FIX 1: harden eta_range parser — raise a clear error if fewer than 2
    # numeric tokens are found instead of silently producing a wrong eta_max.
    eta_range_value = str(fit_input["eta_range"].dropna().iloc[0])
    eta_bounds = [float(v) for v in re.findall(r'[-+]?\d+\.?\d*', eta_range_value)]
    if len(eta_bounds) < 2:
        raise ValueError(
            f"Cannot parse eta_range '{eta_range_value}': expected two numeric bounds "
            f"(e.g. '-2.5-2.5' or '0-2.5'); got tokens {eta_bounds}."
        )
    eta_max = max(abs(eta_bounds[0]), abs(eta_bounds[1]))

    # AIS-62: Convert detector pseudorapidity acceptance eta_max to an effective
    # rapidity acceptance y_max for the median pT of the dataset.
    # All three model integrands (Jüttner, Bose-Einstein, Tsallis) are defined
    # in rapidity space — Cleymans & Worku arXiv:1110.5526 eq.(1) is explicitly
    # dN/dpT dy. For finite-mass pions at the ALICE acceptance |eta|<1, the
    # rapidity acceptance |y_max| < |eta_max| by ~5-10% at pT~0.5 GeV.
    # Relationship: sinh(y_max) = sinh(eta_max) * pT / mT
    #               => y_max = arcsinh(sinh(eta_max) * pT / sqrt(pT^2 + m^2))
    # Evaluated at the median pT of all data to get a single representative y_max.
    _pt_values = fit_input["pt_center_gev"].dropna().to_numpy(dtype=float)
    _pt_median = float(np.median(_pt_values)) if len(_pt_values) > 0 else 1.0
    _mt_median = math.sqrt(mass_gev**2 + _pt_median**2)
    # sinh(y_max) = sinh(eta_max) * pT/mT (Kolb & Heinz nucl-th/0305084 Appendix A)
    y_max = math.asinh(math.sinh(eta_max) * _pt_median / _mt_median)
    fit_specs = build_fit_specs(eta_max=y_max, mass_gev=mass_gev)

    group_columns = infer_group_columns(fit_input)
    grouped = [(("all_data",), fit_input)] if not group_columns else fit_input.groupby(group_columns, dropna=False)

    parameter_rows: list[dict[str, Any]] = []
    quality_rows: list[dict[str, Any]] = []
    correlation_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []

    covariance_dir = run_dir / "covariance"
    diagnostics_dir = run_dir / "diagnostics"
    covariance_dir.mkdir(exist_ok=True)
    diagnostics_dir.mkdir(exist_ok=True)

    for group_key, group_df in grouped:
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        group_label = "__".join(str(value) for value in group_key)
        x_values = group_df["pt_center_gev"].to_numpy(dtype=float)
        y_values = group_df["yield_value"].to_numpy(dtype=float)
        y_errors = group_df["total_error"].to_numpy(dtype=float)

        best_for_group: list[dict[str, Any]] = []
        for spec in fit_specs:
            result = fit_one_spec(spec, x_values, y_values, y_errors)
            quality_rows.append(
                {
                    "group_label": group_label,
                    "model_name": spec.model_name,
                    "component_count": spec.component_count,
                    "success": result.get("success", False),
                    "chi2": result.get("chi2"),
                    "ndf": result.get("ndf"),
                    "chi2_ndf": result.get("chi2_ndf"),
                    "fit_quality_flag": result.get("fit_quality_flag", "ok"),
                    "aic": result.get("aic"),
                    "bic": result.get("bic"),
                    "edm": result.get("edm"),
                    "has_accurate_covar": result.get("has_accurate_covar"),
                    "seed_index": result.get("seed_index"),
                }
            )

            parameter_values = result.get("parameter_values", {})
            parameter_errors = result.get("parameter_errors", {})
            for parameter_name, parameter_value in parameter_values.items():
                parameter_rows.append(
                    {
                        "group_label": group_label,
                        "model_name": spec.model_name,
                        "component_count": spec.component_count,
                        "parameter_name": parameter_name,
                        "value": parameter_value,
                        "error": parameter_errors.get(parameter_name),
                    }
                )

            correlation_matrix = result.get("correlation_matrix")
            if correlation_matrix is not None:
                correlation_array = np.asarray(correlation_matrix, dtype=float)
                covariance_array = np.asarray(result["covariance_matrix"], dtype=float)
                covariance_df = pd.DataFrame(
                    covariance_array,
                    index=spec.parameter_names,
                    columns=spec.parameter_names,
                )
                covariance_df.to_csv(
                    covariance_dir / f"{group_label}__{spec.model_name}__{spec.component_count}c.csv"
                )
                for row_index, left_name in enumerate(spec.parameter_names):
                    for col_index, right_name in enumerate(spec.parameter_names):
                        correlation_rows.append(
                            {
                                "group_label": group_label,
                                "model_name": spec.model_name,
                                "component_count": spec.component_count,
                                "parameter_left": left_name,
                                "parameter_right": right_name,
                                "correlation": correlation_array[row_index, col_index],
                            }
                        )

            residuals = np.asarray(result.get("residuals", []), dtype=float)
            pulls = np.asarray(result.get("pulls", []), dtype=float)
            predictions = np.asarray(result.get("model_predictions", []), dtype=float)
            residual_df = pd.DataFrame(
                {
                    "pt_center_gev": x_values,
                    "yield_value": y_values,
                    "total_error": y_errors,
                    "prediction": predictions,
                    "residual": residuals,
                    "pull": pulls,
                }
            )
            residual_df.to_csv(
                diagnostics_dir / f"{group_label}__{spec.model_name}__{spec.component_count}c_residuals.csv",
                index=False,
            )
            if plt is not None and result.get("success"):
                plot_fit_diagnostics(
                    diagnostics_dir / f"{group_label}__{spec.model_name}__{spec.component_count}c.png",
                    x_values,
                    y_values,
                    y_errors,
                    predictions,
                    residuals,
                    pulls,
                    title=f"{group_label} | {spec.model_name} | {spec.component_count} components",
                )

            best_for_group.append(
                {
                    "group_label": group_label,
                    "model_name": spec.model_name,
                    "component_count": spec.component_count,
                    "success": result.get("success", False),
                    "chi2_ndf": result.get("chi2_ndf"),
                    "aic": result.get("aic"),
                    "bic": result.get("bic"),
                }
            )

        successful = [row for row in best_for_group if row["success"]]
        successful.sort(key=lambda item: (item["aic"], item["bic"]))
        for rank, row in enumerate(successful, start=1):
            comparison_rows.append({"rank_in_group": rank, **row})

    import csv
    def write_csv(df, path):
        records = df.to_dict("records")
        if not records:
            with open(path, "w", newline="") as f:
                pass
            return
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)

    write_csv(fit_input, run_dir / "fit_input.csv")
    write_csv(pd.DataFrame(parameter_rows), run_dir / "fit_parameters.csv")
    write_csv(pd.DataFrame(quality_rows), run_dir / "fit_quality.csv")
    write_csv(pd.DataFrame(correlation_rows), run_dir / "parameter_correlations.csv")
    write_csv(pd.DataFrame(comparison_rows), run_dir / "model_comparison.csv")

    return {
        "fit_ready": True,
        "groups_fit": sorted({row["group_label"] for row in quality_rows}),
        "matplotlib_available": plt is not None,
    }

def run_all_fits(
    data_path: str,
    run_dir: str,
    mass_gev: float = 0.13957,
    model_keys: list | None = None,
    cov_mode: str = "diag",
    xi: float = 1.0,
) -> dict:
    """
    Callable entry point for libs/physics-core/cli.py.

    Parameters
    ----------
    data_path : str
        Path to per-bin pT spectrum CSV.
    run_dir : str
        Output directory (must exist).
    mass_gev : float
        Particle mass in GeV.
    model_keys : list[str] | None
        Model identifiers to run. None = run all defined FitSpecs.
    cov_mode : str
        'diag' or 'correlated'.
    xi : float
        Log-pT correlation length for GLS covariance.

    Returns
    -------
    dict
        Nested dict: {bin_label: {model_key: {chi2_ndf, aic, bic, params}}}.
    """
    import pandas as pd

    df = pd.read_csv(data_path)

    if "eta_range" not in df.columns:
        raise ValueError("fit_input.csv must include an eta_range column")

    eta_range_value = str(df["eta_range"].dropna().iloc[0])
    eta_bounds = [float(v) for v in re.findall(r'[-+]?\d+\.?\d*', eta_range_value)]
    if len(eta_bounds) < 2:
        raise ValueError(f"Cannot parse eta_range '{eta_range_value}'")

    eta_max = max(abs(eta_bounds[0]), abs(eta_bounds[1]))
    _pt_values = df["pt_center_gev"].dropna().to_numpy(dtype=float)
    _pt_median = float(np.median(_pt_values)) if len(_pt_values) > 0 else 1.0
    _mt_median = math.sqrt(mass_gev**2 + _pt_median**2)
    y_max = math.asinh(math.sinh(eta_max) * _pt_median / _mt_median)

    specs_list = build_fit_specs(eta_max=y_max, mass_gev=mass_gev)
    all_specs = {s.model_name: s for s in specs_list}

    if model_keys is not None:
        all_specs = {k: v for k, v in all_specs.items() if k in model_keys}

    results: dict = {}
    group_columns = infer_group_columns(df)
    grouped = [(("all_data",), df)] if not group_columns else df.groupby(group_columns, dropna=False)
    for bin_tuple, bin_df in grouped:
        # If group_columns exists, pandas groupby returns a tuple (or scalar if 1 column). Ensure it's a tuple.
        if not isinstance(bin_tuple, tuple):
            bin_tuple = (bin_tuple,)
        bin_label = "-".join(str(x) for x in bin_tuple)
        results[bin_label] = {}
        for model_key, spec in all_specs.items():
            try:
                x_values = bin_df["pt_center_gev"].to_numpy(dtype=float)
                y_values = bin_df["yield_value"].to_numpy(dtype=float) if "yield_value" in bin_df.columns else bin_df["yield"].to_numpy(dtype=float)
                y_errors = bin_df["total_error"].to_numpy(dtype=float) if "total_error" in bin_df.columns else bin_df["stat_error"].to_numpy(dtype=float)
                res = fit_one_spec(spec, x_values, y_values, y_errors)
                results[bin_label][model_key] = res
            except Exception as exc:
                results[bin_label][model_key] = {"status": "failed", "error": str(exc)}

    return results
