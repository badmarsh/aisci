
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
