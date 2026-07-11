
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
        # dy/deta Jacobian: p_total / (mT * cosh(eta))
        p_total = math.sqrt(pt * pt * math.cosh(eta) ** 2 + mass_gev ** 2 * math.sinh(eta) ** 2)
        jacobian = p_total / (mt * math.cosh(eta))  # = dy/deta = p/E, dimensionless
        return jacobian * math.cosh(eta) * mt * safe_exp(-exponent)

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
            
        # dy/deta Jacobian: p_total / (mT * cosh(eta))
        p_total = math.sqrt(pt * pt * math.cosh(eta) ** 2 + mass_gev ** 2 * math.sinh(eta) ** 2)
        jacobian = p_total / (mt * math.cosh(eta))  # = dy/deta = p/E, dimensionless
        
        return jacobian * math.cosh(eta) * mt / denominator

    result = norm * pt * eta_integral(integrand, -eta_max, eta_max)
    if _underflow_count[0] > 0:
        warnings.warn(
            f"bose_component_scalar: {_underflow_count[0]} integration points had"
            f" denominator <= 0 (pT={pt:.3f} GeV, T={temperature:.3f}, U={U:.3f})."
            " Check parameter bounds — best-fit exponent must be > 0 across full pT range.",
            stacklevel=3,
        )
    return result
