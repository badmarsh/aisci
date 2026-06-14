#!/usr/bin/env python3
from __future__ import annotations
"""
Prototype physics validation helpers for ATLAS-like pT spectra.

This module is for baseline exploration, not publication-grade validation by itself.
The Tsallis-like function below uses simplified assumptions and must be checked
against the exact literature formula chosen for comparison.

This script provides:
1. Simplified Tsallis-like fitting function
2. Candidate kinematic boundary constraint logic
3. Safe fit range enforcement (p_T > 600 MeV)
4. Velocity validation checks

Working parameterization:
- Temperature T (GeV)
- Flow velocity beta_T 
- Non-extensive parameter q
"""

import numpy as np
from scipy.optimize import curve_fit
from typing import Tuple, Optional


def tsallis_distribution(pT: np.ndarray, T: float, q: float, m0: float = 0.13957) -> np.ndarray:
    """
    Thermodynamically consistent Tsallis distribution function.
    
    Formula:
    dN/(dpT dy) = gV * (pT * mT) / (2*pi)^2 * [1 + (q-1)*(mT - mu)/T]^(-q/(q-1))
    
    Parameters:
    -----------
    pT : array-like
        Transverse momentum values (GeV/c)
    T : float
        Temperature parameter (GeV)
    q : float
        Non-extensive parameter (q > 1)
    m0 : float
        Rest mass of the particle (GeV/c^2), default is pion mass.
        
    Returns:
    --------
    array-like
        Differential yield dN/dpT (normalized arbitrarily for fitting)
    """
    # Ensure physical constraints
    if T <= 0 or q <= 1.0:
        return np.zeros_like(pT)
    
    mT = np.sqrt(pT**2 + m0**2)
    
    # Tsallis factor: [1 + (q-1)*mT/T]^(-q/(q-1))
    tsallis_arg = 1.0 + (q - 1.0) * (mT) / T
    tsallis_arg = np.maximum(tsallis_arg, 1e-10)
    
    # Combined distribution (ignoring g, V, and (2pi)^2 as overall normalization)
    result = pT * mT * np.power(tsallis_arg, -q / (q - 1.0))
    
    return result


def bgbw_distribution(pT: np.ndarray, T: float, beta_avg: float, n: float, m0: float = 0.13957) -> np.ndarray:
    """
    Boltzmann-Gibbs Blast-Wave (BGBW) distribution.
    
    Parameters:
    -----------
    pT : array-like
        Transverse momentum (GeV/c)
    T : float
        Kinetic freeze-out temperature (GeV)
    beta_avg : float
        Average radial flow velocity (0 <= beta_avg < 1)
    n : float
        Velocity profile exponent
    m0 : float
        Rest mass (GeV/c^2)
    """
    from scipy.integrate import quad
    from scipy.special import iv, kn
    
    def integrand(r, pT_val, T_val, beta_max_val, n_val, m0_val):
        beta_r = beta_max_val * (r**n_val)
        rho = np.arctanh(beta_r)
        mT = np.sqrt(pT_val**2 + m0_val**2)
        
        arg_iv = (pT_val * np.sinh(rho)) / T_val
        arg_kn = (mT * np.cosh(rho)) / T_val
        
        # Modified Bessel functions I0 and K1
        return r * mT * iv(0, arg_iv) * kn(1, arg_kn)

    beta_max = beta_avg * (n + 2) / 2.0
    if beta_max >= 1.0: return np.zeros_like(pT)
    
    results = []
    for p in pT:
        res, _ = quad(integrand, 0, 1, args=(p, T, beta_max, n, m0))
        results.append(res * p)
        
    return np.array(results)


def apply_kinematic_boundaries(p: float, pT_cut: float, theta_cut: float) -> float:
    """
    Apply candidate kinematic boundary constraints for combined cuts.
    
    Working hypothesis for the more restrictive limit:
    limit = min(sqrt(p^2 - pT_cut^2), p * cos(theta_cut))
    
    Parameters:
    -----------
    p : float
        Total momentum magnitude
    pT_cut : float
        Transverse momentum cut threshold
    theta_cut : float
        Polar angle cut threshold (radians)
        
    Returns:
    --------
    float
        Corrected integration limit
    """
    if p <= pT_cut:
        return 0.0
    
    # Calculate both constraints
    constraint1 = np.sqrt(p**2 - pT_cut**2)
    constraint2 = p * np.cos(theta_cut)
    
    # Return the more restrictive (smaller) constraint
    return np.minimum(constraint1, constraint2)


def safe_fit_range_filter(pT_data: np.ndarray, 
                         cross_section_data: np.ndarray,
                         region_type: str = "general") -> Tuple[np.ndarray, np.ndarray]:
    """
    Filter data to exclude momentum below 600 MeV distortion threshold.
    
    Parameters:
    -----------
    pT_data : array-like
        Transverse momentum data points (GeV/c)
    cross_section_data : array-like
        Corresponding cross-section measurements
    region_type : str
        Region type: "forward", "general", or "central"
        
    Returns:
    --------
    tuple
        Filtered (pT, cross_section) arrays with pT >= 0.6 GeV
    """
    # Convert 600 MeV to GeV
    min_pT = 0.6
    
    # Create mask for safe fit range
    safe_mask = pT_data >= min_pT
    
    return pT_data[safe_mask], cross_section_data[safe_mask]


def validate_velocity_parameterization(U_values: np.ndarray) -> np.ndarray:
    """
    Validate velocity parameterization and detect mislabeling errors.
    
    Checks the relationship v = U/sqrt(1 + U^2) and flags unphysical results.
    If U represents rapidity, then v should be bounded by c (v < 1).
    
    Parameters:
    -----------
    U_values : array-like
        Input parameter U (potentially rapidity or velocity)
        
    Returns:
    --------
    array-like
        Calculated velocity values v
    """
    U_values = np.asarray(U_values)
    
    # Calculate v from U using relativistic relation
    v_values = U_values / np.sqrt(1.0 + U_values**2)
    
    # Check for unphysical velocities (should be < 1)
    unphysical_mask = v_values >= 1.0
    if np.any(unphysical_mask):
        print(f"WARNING: Found {np.sum(unphysical_mask)} unphysical velocity values >= 1.0")
        print(f"Max velocity: {np.max(v_values):.6f}")
    
    # Check asymptotic behavior: as U -> infinity, v -> 1
    # But if U is already velocity, this check will fail
    large_U_mask = U_values > 10.0
    if np.any(large_U_mask):
        asymptotic_v = np.mean(v_values[large_U_mask])
        if abs(asymptotic_v - 1.0) > 0.1:
            print(f"WARNING: Asymptotic velocity {asymptotic_v:.6f} != 1.0")
            print("This suggests U may be mislabeled as velocity when it's actually rapidity")
    
    return v_values


def fit_tsallis_to_data(pT_data: np.ndarray, 
                       cross_section_data: np.ndarray,
                       m0: float = 0.13957,
                       initial_params: Optional[Tuple[float, float]] = None,
                       **fit_kwargs) -> Tuple[np.ndarray, np.ndarray]:
    """
    Fit thermodynamically consistent Tsallis distribution to experimental data.
    """
    pT_filtered, cs_filtered = safe_fit_range_filter(pT_data, cross_section_data)
    
    if initial_params is None:
        initial_params = (0.16, 1.1)  # (T, q)
    
    try:
        # Wrap the function to fix m0
        def fit_func(pT, T, q):
            return tsallis_distribution(pT, T, q, m0)
            
        popt, pcov = curve_fit(
            fit_func,
            pT_filtered,
            cs_filtered,
            p0=initial_params,
            bounds=([0.01, 1.0001], [1.0, 3.0]),
            **fit_kwargs
        )
        return popt, pcov
    except Exception as e:
        print(f"Tsallis fitting failed: {e}")
        return np.array(initial_params), np.zeros((2, 2))


def demonstrate_usage():
    """
    Demonstrate refined models and BGBW vs Tsallis comparison.
    """
    # Particle mass: pion (0.139), proton (0.938)
    m_pion = 0.13957
    m_proton = 0.93827
    
    pT_range = np.linspace(0.1, 8.0, 100)
    
    print("--- Model Comparison: Tsallis vs BGBW ---")
    
    # 1. Generate BGBW spectrum (representing 'truth' from literature)
    # Tkin=0.16, beta_avg=0.4, n=1.0 (Typical for 7 TeV pp)
    T_bgbw = 0.160
    beta_bgbw = 0.40
    n_bgbw = 1.0
    
    print(f"Generating BGBW truth (Pions): T={T_bgbw}, beta={beta_bgbw}, n={n_bgbw}")
    cs_truth = bgbw_distribution(pT_range, T_bgbw, beta_bgbw, n_bgbw, m_pion)
    
    # Add noise
    np.random.seed(42)
    noise = np.random.normal(0, 0.05 * cs_truth, len(cs_truth))
    cs_noisy = np.maximum(cs_truth + noise, 1e-12)
    
    # 2. Fit with Tsallis (Baseline comparison)
    popt, pcov = fit_tsallis_to_data(pT_range, cs_noisy, m0=m_pion)
    T_fit, q_fit = popt
    
    print(f"\nTsallis Fit to BGBW truth:")
    print(f"Fitted T: {T_fit:.4f} GeV")
    print(f"Fitted q: {q_fit:.4f}")
    
    # 3. Validation Logic: Velocity parameterization
    U_values = np.linspace(0, 2.0, 5)
    v_values = validate_velocity_parameterization(U_values)
    print(f"\nU to velocity map: {list(zip(U_values, np.round(v_values, 3)))}")
    
    # 4. Kinematic Boundary Check
    p_test = 5.0
    pT_cut = 1.0
    theta_cut = np.pi/4
    boundary = apply_kinematic_boundaries(p_test, pT_cut, theta_cut)
    print(f"\nBoundary (p={p_test}, pT_cut={pT_cut}, theta_cut=pi/4): {boundary:.4f}")


if __name__ == "__main__":
    demonstrate_usage()


if __name__ == "__main__":
    demonstrate_usage()
