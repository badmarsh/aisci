#!/usr/bin/env python3
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


def tsallis_distribution(pT: np.ndarray, T: float, beta_T: float, q: float) -> np.ndarray:
    """
    Tsallis distribution function for transverse momentum spectra.
    
    Parameters:
    -----------
    pT : array-like
        Transverse momentum values (GeV/c)
    T : float
        Temperature parameter (GeV)
    beta_T : float  
        Transverse flow velocity (dimensionless, 0 <= beta_T < 1)
    q : float
        Non-extensive parameter (q > 1 for power-law tails)
        
    Returns:
    --------
    array-like
        Differential cross-section dN/(pT*dpT*dy) values
        
    Notes:
    ------
    This simplified Tsallis-like distribution can model power-law tails at high
    pT through q, but it is not yet a literature-matched baseline.
    """
    # Ensure physical constraints
    if T <= 0 or beta_T < 0 or beta_T >= 1 or q <= 1:
        return np.zeros_like(pT)
    
    # Tsallis factor: [1 + (q-1)*E/T]^(-1/(q-1))
    # For relativistic particles: E = sqrt(m^2 + pT^2) ≈ pT for high pT
    # Using massless approximation for simplicity (valid for pT >> m_pi)
    energy = pT  # Massless approximation
    
    # Calculate the Tsallis exponent
    tsallis_arg = 1.0 + (q - 1.0) * energy / T
    # Avoid negative arguments due to numerical issues
    tsallis_arg = np.maximum(tsallis_arg, 1e-10)
    
    # Apply flow boost
    flow_factor = np.exp(-beta_T * pT / T)
    
    # Combined distribution
    result = flow_factor * np.power(tsallis_arg, -1.0 / (q - 1.0))
    
    return result


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
                       initial_params: Optional[Tuple[float, float, float]] = None,
                       **fit_kwargs) -> Tuple[np.ndarray, np.ndarray]:
    """
    Fit Tsallis distribution to experimental data.
    
    Parameters:
    -----------
    pT_data : array-like
        Transverse momentum data points (GeV/c)
    cross_section_data : array-like
        Measured cross-section values
    initial_params : tuple, optional
        Initial guess for (T, beta_T, q)
    **fit_kwargs : dict
        Additional keyword arguments for curve_fit
        
    Returns:
    --------
    tuple
        (optimal_parameters, parameter_covariance)
    """
    # Apply safe fit range filter
    pT_filtered, cs_filtered = safe_fit_range_filter(pT_data, cross_section_data)
    
    # Set default initial parameters if not provided
    if initial_params is None:
        initial_params = (0.15, 0.5, 1.1)  # Typical values for pp collisions
    
    try:
        # Perform the fit
        popt, pcov = curve_fit(
            tsallis_distribution,
            pT_filtered,
            cs_filtered,
            p0=initial_params,
            bounds=([0.01, 0.0, 1.001], [1.0, 0.99, 3.0]),
            **fit_kwargs
        )
        return popt, pcov
    except Exception as e:
        print(f"Fitting failed: {e}")
        # Return initial parameters as fallback
        return np.array(initial_params), np.zeros((3, 3))


def demonstrate_usage():
    """
    Demonstrate the physics validation functions with example data.
    """
    # Generate synthetic ATLAS-like data
    np.random.seed(42)
    pT_true = np.linspace(0.1, 10.0, 100)
    
    # True parameters (typical for 13 TeV pp collisions)
    T_true, beta_T_true, q_true = 0.16, 0.6, 1.15
    cs_true = tsallis_distribution(pT_true, T_true, beta_T_true, q_true)
    
    # Add realistic noise
    noise = np.random.normal(0, 0.1 * cs_true, len(cs_true))
    cs_noisy = cs_true + noise
    
    # Fit the data
    popt, pcov = fit_tsallis_to_data(pT_true, cs_noisy)
    T_fit, beta_T_fit, q_fit = popt
    
    print("Tsallis Fitting Results:")
    print(f"True parameters:   T={T_true:.3f}, beta_T={beta_T_true:.3f}, q={q_true:.3f}")
    print(f"Fitted parameters: T={T_fit:.3f}, beta_T={beta_T_fit:.3f}, q={q_fit:.3f}")
    print(f"Parameter errors:  T={np.sqrt(pcov[0,0]):.3f}, beta_T={np.sqrt(pcov[1,1]):.3f}, q={np.sqrt(pcov[2,2]):.3f}")
    
    # Test kinematic boundaries with multiple scenarios
    print(f"\nKinematic boundary tests:")
    test_cases = [
        (5.0, 1.0, np.pi/4),   # Standard case
        (2.0, 1.5, np.pi/6),   # Tight pT cut
        (10.0, 0.5, np.pi/3),  # Loose constraints
        (1.0, 2.0, np.pi/4),   # Invalid case (p < pT_cut)
    ]
    
    for i, (test_p, test_pT_cut, test_theta_cut) in enumerate(test_cases):
        boundary = apply_kinematic_boundaries(test_p, test_pT_cut, test_theta_cut)
        print(f"Case {i+1}: p={test_p}, pT_cut={test_pT_cut}, theta_cut={test_theta_cut:.3f} rad -> boundary={boundary:.3f}")
    
    # Test safe fit range filtering
    pT_all = np.linspace(0.1, 8.0, 50)
    cs_all = np.ones_like(pT_all)
    pT_filtered, cs_filtered = safe_fit_range_filter(pT_all, cs_all, "general")
    print(f"\nSafe fit range test:")
    print(f"Original range: {pT_all.min():.1f} - {pT_all.max():.1f} GeV")
    print(f"Filtered range: {pT_filtered.min():.1f} - {pT_filtered.max():.1f} GeV")
    print(f"Points removed: {len(pT_all) - len(pT_filtered)} (below 0.6 GeV threshold)")
    
    # Test velocity validation
    U_test = np.linspace(0, 5, 100)
    v_test = validate_velocity_parameterization(U_test)
    print(f"\nVelocity validation: max(v) = {np.max(v_test):.6f} (should be < 1.0)")


if __name__ == "__main__":
    demonstrate_usage()
