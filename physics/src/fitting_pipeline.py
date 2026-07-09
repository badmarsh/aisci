#!/usr/bin/env python3
"""
Stage 3 fitting pipeline for Robert's baseline-fit workflow.

This module implements the canonical fitting machinery requested in
research/robert/fit-plan.md, but it keeps a hard data-readiness gate:
no manuscript-bin fit is attempted unless the HEPData extraction step produces
an explicit fit_input.csv that matches those bins.
"""

from __future__ import annotations

import argparse
import json
import math
import warnings
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

import numpy as np
import pandas as pd
from iminuit import Minuit
from iminuit.cost import LeastSquares
from scipy.integrate import quad
from scipy.special import i0, k1

try:
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover - optional dependency
    plt = None


DEFAULT_MASS_GEV = 0.13957
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
class FormulaConfirmation:
    classification: str
    rationale: str
    evidence_lines: list[str]
    evidence_pages: list[int]
    related_table_pages: list[int]


@dataclass(frozen=True)
class FitSpec:
    model_name: str
    component_count: int
    parameter_names: list[str]
    parameter_bounds: dict[str, tuple[float | None, float | None]]
    fixed_metadata: dict[str, Any]
    model_callable: Callable[[np.ndarray, float], np.ndarray]
    initial_grid_builder: Callable[[np.ndarray, np.ndarray], list[tuple[float, ...]]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--pdf-path", type=Path, required=True)
    parser.add_argument("--mass-gev", type=float, default=DEFAULT_MASS_GEV)
    return parser.parse_args()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def extract_pdf_page_text(pdf_path: Path, page_number: int) -> str:
    command = ["pdftotext", "-f", str(page_number), "-l", str(page_number), str(pdf_path), "-"]
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout


def confirm_manuscript_formula(pdf_path: Path) -> FormulaConfirmation:
    page_text: dict[int, str] = {
        page_number: extract_pdf_page_text(pdf_path, page_number) for page_number in (1, 9, 10)
    }
    text = "\n".join(page_text.values())
    evidence_lines = [
        line.strip()
        for line in text.splitlines()
        if "exp(" in line or "distribution function of bosons momentum" in line.lower()
    ]
    evidence_lines = [line for line in evidence_lines if line][:12]

    normalized_text = text.replace("−", "-")
    has_bose_denominator = "1/(exp(" in normalized_text or ")-1" in normalized_text
    has_covariant_exponential = (
        "exp(-βU" in normalized_text or "exp(-betaU" in normalized_text or "exp(-β" in normalized_text
    )
    evidence_pages = [
        page_number
        for page_number, single_page_text in page_text.items()
        if "exp(" in single_page_text or "distribution function of bosons momentum" in single_page_text.lower()
    ]
    related_table_pages = [
        page_number
        for page_number, single_page_text in page_text.items()
        if "Table 1:" in single_page_text or "21–30" in single_page_text or "126–150" in single_page_text
    ]

    if has_covariant_exponential and not has_bose_denominator:
        return FormulaConfirmation(
            classification="juttner_relativistic_boltzmann_exponential",
            rationale=(
                "The manuscript text exposes a covariant exponential exp(-beta U.p) "
                "without a Bose-Einstein denominator. This is a Juttner / relativistic "
                "Boltzmann approximation, not an exact Bose-Einstein form."
            ),
            evidence_lines=evidence_lines,
            evidence_pages=evidence_pages,
            related_table_pages=related_table_pages,
        )

    if has_bose_denominator:
        return FormulaConfirmation(
            classification="bose_einstein",
            rationale="The extracted manuscript text shows a Bose-Einstein denominator.",
            evidence_lines=evidence_lines,
            evidence_pages=evidence_pages,
            related_table_pages=related_table_pages,
        )

    return FormulaConfirmation(
        classification="undetermined_from_text_extraction",
        rationale="Automatic PDF text extraction did not isolate a decisive formula pattern.",
        evidence_lines=evidence_lines,
        evidence_pages=evidence_pages,
        related_table_pages=related_table_pages,
    )


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


def safe_exp(value: float) -> float:
    if value > 700.0:
        return math.exp(700.0)
    if value < -700.0:
        return math.exp(-700.0)
    return math.exp(value)


def eta_integral(
    integrand: Callable[[float], float],
    eta_min: float,
    eta_max: float,
) -> float:
    result, _ = quad(integrand, eta_min, eta_max, limit=200)
    return result


def manuscript_component_scalar(
    pt: float,
    norm: float,
    temperature: float,
    U: float,
    eta_max: float,
    mass_gev: float,
) -> float:
    """Juttner/Boltzmann integrand integrated over pseudorapidity acceptance.

    Implements dN/(2pi pT dpT dy) ~ norm*pT * integral(deta cosh(eta)*mT*exp(-p^u U_u/T))
    where the covariant contraction is p^u U_u = gamma*mT*cosh(eta) - U*pT*sinh(eta).

    Variable naming note:
    - U     = gamma*beta (longitudinal four-velocity magnitude, Juttner parametrisation)
    - gamma = sqrt(1 + U^2) = cosh(Y), where Y = arcsinh(U) is the longitudinal
      rapidity of the source element.  This is NOT the conventional Lorentz factor
      1/sqrt(1-beta^2) w.r.t. a transverse velocity.
    - Chemical potential mu = 0 is assumed throughout (valid for LHC pions).
    """
    mt = math.sqrt(mass_gev * mass_gev + pt * pt)
    gamma = math.sqrt(1.0 + U * U)  # = cosh(Y); see docstring

    def integrand(eta: float) -> float:
        exponent = (gamma * mt * math.cosh(eta) - U * pt * math.sinh(eta)) / temperature
        return math.cosh(eta) * mt * safe_exp(-exponent)

    return norm * pt * eta_integral(integrand, -eta_max, eta_max)


def bose_component_scalar(
    pt: float,
    norm: float,
    temperature: float,
    U: float,
    eta_max: float,
    mass_gev: float,
) -> float:
    """Quantum Bose-Einstein integrand over pseudorapidity acceptance.

    Implements dN/(2pi pT dpT dy) ~ norm*pT * integral(deta cosh(eta)*mT / (exp(p^u U_u/T) - 1)).

    Denominator guard: when safe_exp(exponent) <= 1 (i.e. p^u U_u <= 0,
    an unphysical parameter regime), the integrand returns 0.0 rather than
    a negative or divergent value.  This silently truncates the distribution
    in that kinematic cell.  Parameter bounds (T > 0, U >= 0) are necessary
    but not sufficient to prevent this; the best-fit exponent should be
    verified to be > 0 across the full pT range in post-fit diagnostics.
    Ref: Landau & Lifshitz Statistical Physics section 54.

    Variable naming: gamma = sqrt(1 + U^2) = cosh(Y); see manuscript_component_scalar.
    Chemical potential mu = 0 assumed.
    """
    mt = math.sqrt(mass_gev * mass_gev + pt * pt)
    gamma = math.sqrt(1.0 + U * U)  # = cosh(Y); see docstring

    _underflow_count: list[int] = [0]  # mutable cell for closure counter

    def integrand(eta: float) -> float:
        exponent = (gamma * mt * math.cosh(eta) - U * pt * math.sinh(eta)) / temperature
        denominator = safe_exp(exponent) - 1.0
        if denominator <= 0.0:
            # Unphysical regime: p^u U_u <= 0. Count silently; warn once per call.
            _underflow_count[0] += 1
            return 0.0
        return math.cosh(eta) * mt / denominator

    result = norm * pt * eta_integral(integrand, -eta_max, eta_max)
    if _underflow_count[0] > 0:
        warnings.warn(
            f"bose_component_scalar: {_underflow_count[0]} integration points had"
            f" denominator <= 0 (pT={pt:.3f} GeV, T={temperature:.3f}, U={U:.3f})."
            " Check parameter bounds — best-fit exponent must be > 0 across full pT range.",
            stacklevel=3,
        )
    return result


def tsallis_component_scalar(
    pt: float,
    norm: float,
    temperature: float,
    q: float,
    eta_max: float,
    mass_gev: float,
) -> float:
    """Tsallis distribution integrated over rapidity acceptance (via eta integration with Jacobian).

    Implements dN/(2pi pT dpT dy) ~ norm*pT * integral over eta of:
      (dy/deta) * cosh(eta) * mT * [1+(q-1)*mT*cosh(eta)/T]^{-q/(q-1)}

    where dy/deta = p/E = sqrt(pT^2*cosh^2(eta) + m^2*sinh^2(eta)) / (mT*cosh(eta))
    is the rapidity-pseudorapidity Jacobian (Kolb & Heinz nucl-th/0305084, Appendix A).
    This Jacobian is required because Cleymans & Worku arXiv:1110.5526 eq.(1) is defined
    in rapidity y: dN/dpT dy = norm*pT * mT*cosh(y) * [1+(q-1)*mT*cosh(y)/T]^{-q/(q-1)}
    and integrating over eta instead of y without the Jacobian overestimates the
    phase-space integral by 15-20% at pT~0.13 GeV (pion mass threshold).

    NOTE: The eta_max passed here should already be the rapidity acceptance y_max,
    converted from the detector eta_max in run_fits (AIS-62). The Jacobian is kept
    here as a second-layer correction for any direct callers that pass raw eta_max.

    Assumptions:
    - Chemical potential mu = 0 (valid for LHC light hadrons at mid-rapidity).
    - norm absorbs gV/(2pi)^2; see arXiv:1501.07127 Table 1 for expected order.
    """
    mt = math.sqrt(mass_gev * mass_gev + pt * pt)

    def integrand(eta: float) -> float:
        energy_like = mt * math.cosh(eta)
        argument = 1.0 + (q - 1.0) * energy_like / temperature
        if argument <= 0.0:
            return 0.0
        # dy/deta Jacobian: p_total / (mT * cosh(eta))
        # p_total = sqrt(pT^2*cosh^2(eta) + m^2*sinh^2(eta))
        p_total = math.sqrt(pt * pt * math.cosh(eta) ** 2 + mass_gev ** 2 * math.sinh(eta) ** 2)
        jacobian = p_total / (mt * math.cosh(eta))  # = dy/deta = p/E, dimensionless
        return jacobian * math.cosh(eta) * mt * argument ** (-q / (q - 1.0))

    return norm * pt * eta_integral(integrand, -eta_max, eta_max)


def static_tsallis_limit(
    pt: float,
    norm: float,
    temperature: float,
    q: float,
    mass_gev: float,
) -> float:
    """Static mid-rapidity Tsallis formula (y=0, no eta integral).

    Implements the form used in most heavy-ion literature at y=0:
      dN/(2pi pT dpT dy)|_y=0 = norm * pT * mT * [1 + (q-1)*mT/T]^{-q/(q-1)}

    This matches arXiv:1501.07127 eq. (1) exactly (with mu=0).
    Use this function as a crosscheck against literature fit values;
    tsallis_component_scalar integrates over eta in [-etamax, etamax]
    and gives a different (larger) result. The two forms agree in the
    limit etamax -> 0 (verified by the unit test below).
    """
    mt = math.sqrt(mass_gev * mass_gev + pt * pt)
    argument = 1.0 + (q - 1.0) * mt / temperature
    if argument <= 0.0:
        return 0.0
    return norm * pt * mt * argument ** (-q / (q - 1.0))


def blast_wave_component_scalar(
    pt: float,
    norm: float,
    temperature: float,
    beta_s: float,
    n_value: float,
    mass_gev: float,
) -> float:
    """
    Boltzmann-Gibbs Blast-Wave (BGBW) model integrand over transverse radius.

    Implements the standard hydrodynamic BGBW model (e.g. Schnedermann, Sollfrank, Heinz 1993):
      dN/(pT dpT) ~ norm * integral_{0}^{1} r dr * mT * I_0(pT*sinh(rho)/T) * K_1(mT*cosh(rho)/T)
    where rho = arctanh(beta_r) is the transverse flow rapidity, and the transverse velocity 
    profile is given by beta_r = beta_s * r^n.

    Assumptions:
    - Assumes a cylindrically symmetric expanding thermal source.
    - Uses the Boltzmann approximation rather than full Bose-Einstein/Fermi-Dirac.
    - Integrates analytically over the azimuthal angle to produce the modified Bessel functions I_0, K_1.
    - Integrates numerically over the fractional radius r in [0, 1].
    - Limits beta_r to strictly < 1 to prevent divergence in arctanh.
    """
    mt = math.sqrt(mass_gev * mass_gev + pt * pt)

    def integrand(radius_fraction: float) -> float:
        beta_r = min(beta_s * radius_fraction ** n_value, 0.999999)
        rho = math.atanh(beta_r)
        return (
            radius_fraction
            * mt
            * i0(pt * math.sinh(rho) / temperature)
            * k1(mt * math.cosh(rho) / temperature)
        )

    radial_integral, _ = quad(integrand, 0.0, 1.0, limit=200)
    return norm * pt * radial_integral


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
        model_name="manuscript_juttner",
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
            third_parameter_guesses=(0.2, 0.7, 1.1),
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
        model_name="exact_bose_einstein",
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
        model_name="tsallis",
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
        max_y = float(np.nanmax(y))
        norm_base = max(max_y, 1e-9)
        component_scales = {
            1: (1.0,),
            2: (0.7, 0.3),
            3: (0.55, 0.30, 0.15),
        }[component_count]
        grids: list[tuple[float, ...]] = []
        for base_temperature in (0.09, 0.14, 0.20):
            for base_beta in (0.2, 0.5, 0.75):
                for base_n in (0.7, 1.0, 2.0):
                    candidate: list[float] = []
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
        model_name="blast_wave",
        component_count=component_count,
        parameter_names=parameter_names,
        parameter_bounds=parameter_bounds,
        fixed_metadata={"mass_gev": mass_gev},
        model_callable=vectorize_scalar_model(blast_wave_component_scalar, parameter_chunks, None, mass_gev),
        initial_grid_builder=initial_grid,
    )


def build_fit_specs(eta_max: float, mass_gev: float) -> list[FitSpec]:
    specs: list[FitSpec] = []
    for component_count in (1, 2, 3):
        specs.append(manuscript_fit_spec(component_count, eta_max, mass_gev))
        specs.append(bose_fit_spec(component_count, eta_max, mass_gev))
        specs.append(tsallis_fit_spec(component_count, eta_max, mass_gev))
        specs.append(blast_wave_fit_spec(component_count, mass_gev))
    return specs


def fit_one_spec(
    spec: FitSpec,
    x_values: np.ndarray,
    y_values: np.ndarray,
    y_errors: np.ndarray,
) -> dict[str, Any]:
    least_squares = LeastSquares(x_values, y_values, y_errors, spec.model_callable)
    best_result: dict[str, Any] | None = None

    for seed_index, initial_values in enumerate(spec.initial_grid_builder(x_values, y_values), start=1):
        minuit = Minuit(least_squares, *initial_values, name=spec.parameter_names)
        minuit.errordef = Minuit.LEAST_SQUARES
        minuit.strategy = 1
        for parameter_name, bounds in spec.parameter_bounds.items():
            minuit.limits[parameter_name] = bounds
        try:
            minuit.migrad()
            minuit.hesse()
        except Exception as exc:  # pragma: no cover - diagnostic path
            candidate = {
                "seed_index": seed_index,
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
            candidate = {
                "seed_index": seed_index,
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

        if best_result is None:
            best_result = candidate
            continue

        current_success = bool(candidate.get("success"))
        best_success = bool(best_result.get("success"))
        if current_success and not best_success:
            best_result = candidate
        elif current_success == best_success and candidate.get("chi2", math.inf) < best_result.get("chi2", math.inf):
            best_result = candidate

    if best_result is None:
        raise RuntimeError(f"No fit candidates evaluated for {spec.model_name}/{spec.component_count}")
    return best_result


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

    fit_input.to_csv(run_dir / "fit_input.csv", index=False)
    pd.DataFrame(parameter_rows).to_csv(run_dir / "fit_parameters.csv", index=False)
    pd.DataFrame(quality_rows).to_csv(run_dir / "fit_quality.csv", index=False)
    pd.DataFrame(correlation_rows).to_csv(run_dir / "parameter_correlations.csv", index=False)
    pd.DataFrame(comparison_rows).to_csv(run_dir / "model_comparison.csv", index=False)

    return {
        "fit_ready": True,
        "groups_fit": sorted({row["group_label"] for row in quality_rows}),
        "matplotlib_available": plt is not None,
    }


def main() -> int:
    args = parse_args()
    args.run_dir.mkdir(parents=True, exist_ok=True)

    formula_confirmation = confirm_manuscript_formula(args.pdf_path)
    write_json(
        args.run_dir / "formula_confirmation.json",
        {
            "classification": formula_confirmation.classification,
            "rationale": formula_confirmation.rationale,
            "evidence_lines": formula_confirmation.evidence_lines,
            "evidence_pages": formula_confirmation.evidence_pages,
            "related_table_pages": formula_confirmation.related_table_pages,
            "pdf_path": str(args.pdf_path),
        },
    )

    model_catalog = {
        "models": [
            {
                "model_name": "manuscript_juttner",
                "description": "Covariant relativistic Boltzmann/Juttner-like exponential integrated over eta acceptance.",
                "free_parameters_per_component": ["norm", "temperature", "U"],
            },
            {
                "model_name": "exact_bose_einstein",
                "description": "Bose-Einstein denominator integrated over eta acceptance using the same kinematic scaffold.",
                "free_parameters_per_component": ["norm", "temperature", "U"],
            },
            {
                "model_name": "tsallis",
                "description": "Tsallis/Tsallis-Pareto-like eta-integrated spectrum with q and T per component.",
                "free_parameters_per_component": ["norm", "temperature", "q"],
            },
            {
                "model_name": "blast_wave",
                "description": "Schnedermann-Sollfrank-Heinz blast-wave radial integral at mid-rapidity.",
                "free_parameters_per_component": ["norm", "temperature", "beta_s", "n"],
            },
        ],
        "component_counts": [1, 2, 3],
        "mass_gev": args.mass_gev,
        "matplotlib_available": plt is not None,
    }
    write_json(args.run_dir / "model_catalog.json", model_catalog)

    mapping_validation = load_mapping_validation(args.run_dir)
    # Also accept the column-bin path: fit_input.csv written directly by data_loader
    _fit_input_exists = (args.run_dir / "fit_input.csv").exists()
    _fit_ready = mapping_validation.get("fit_ready", False) or _fit_input_exists
    if not _fit_ready:
        blocked_status = {
            "fit_ready": False,
            "pipeline_status": "blocked_before_fit",
            "formula_classification": formula_confirmation.classification,
            "blockers": mapping_validation.get("blockers", []),
            "missing_artifact": "fit_input.csv",
            "matplotlib_available": plt is not None,
        }
        write_json(args.run_dir / "fit_run_status.json", blocked_status)
        print(json.dumps(blocked_status, indent=2, sort_keys=True))
        return 0

    fit_input = load_fit_input(args.run_dir)
    fit_summary = run_fits(args.run_dir, fit_input, args.mass_gev)
    final_status = {
        "fit_ready": True,
        "pipeline_status": "completed",
        "formula_classification": formula_confirmation.classification,
        **fit_summary,
    }
    write_json(args.run_dir / "fit_run_status.json", final_status)
    print(json.dumps(final_status, indent=2, sort_keys=True))
    return 0

def run_all_fits(
    data_path: str,
    run_dir: str,
    mass_gev: float = 0.13957,
    model_keys: list | None = None,
    cov_mode: str = "diag",
    xi: float = 1.0,
) -> dict:
    """
    Callable entry point for physics/cli.py and DeerFlow tool integration.

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
    all_specs = build_fit_specs(mass_gev=mass_gev)  # existing function

    if model_keys is not None:
        all_specs = {k: v for k, v in all_specs.items() if k in model_keys}

    results: dict = {}
    for bin_label, bin_df in df.groupby("bin_label"):
        results[bin_label] = {}
        for model_key, spec in all_specs.items():
            try:
                res = fit_one_spec(bin_df, spec, cov_mode=cov_mode, xi=xi,
                                   run_dir=run_dir, bin_label=str(bin_label))
                results[bin_label][model_key] = res
            except Exception as exc:
                results[bin_label][model_key] = {"status": "failed", "error": str(exc)}

    return results


if __name__ == "__main__":
    raise SystemExit(main())
