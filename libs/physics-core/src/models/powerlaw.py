from __future__ import annotations
import math

def powerlaw_component_scalar(
    pt: float,
    norm: float,
    p0: float,
    n: float,
) -> float:
    """Power-law tail component for hard QCD scattering.
    
    Implements dN/(2pi pT dpT dy) ~ norm * pT * (1 + pT/p0)^(-n)
    """
    return norm * pt * math.pow(1.0 + pt / p0, -n)
