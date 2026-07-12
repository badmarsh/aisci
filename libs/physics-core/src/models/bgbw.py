
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
        x = pt * math.sinh(rho) / temperature
        y = mt * math.cosh(rho) / temperature
        # Use exponentially scaled Bessel functions to prevent overflow/segfaults
        # i0(x) * k1(y) = i0e(x) * k1e(y) * exp(x - y)
        return (
            radius_fraction
            * mt
            * i0e(x)
            * k1e(y)
            * math.exp(x - y)
        )

    radial_integral, _ = quad(integrand, 0.0, 1.0, limit=200)
    return norm * pt * radial_integral
