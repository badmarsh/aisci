#!/usr/bin/env python3
"""
bgbw_covariance.py — C3 scaffold for issue #27.

Provides covariance-matrix construction and Generalised Least Squares (GLS)
utilities for BGBW per-class fits against HEPData ins1735345 (stat + sys
published in quadrature, full correlation matrix unavailable).

Design rationale
----------------
ins1735345 publishes stat and sys per pT bin but *not* a full covariance
matrix.  The standard χ²/ndf from diagonal weighting (diag(stat²+sys²))
treats correlated systematics as independent and therefore underestimates the
effective number of constraints — the reported χ²/ndf is artificially low.

This module synthesises a parametric covariance:

    Σ_ij = δ_ij · σ_stat,i²  +  σ_sys,i · σ_sys,j · exp(-|Δ log pT|_ij / ξ)

where ξ is a correlation length in log-pT space.  Marginalising over
ξ ∈ {0.1, 0.3, 1.0, 3.0} produces a χ²/ndf envelope that brackets the
true (unknown) covariance structure.

References
----------
- ins1735345: HEPData record doi:10.17182/hepdata.91996.v2
- Barlow (2002) "Systematic errors: facts and fictions", arXiv:hep-ex/0207026
- D'Agostini (1994) Nucl.Instrum.Meth.A 346:306
"""

from __future__ import annotations

import math
import warnings
from typing import Sequence

import numpy as np
from numpy.linalg import cholesky, LinAlgError, solve


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

CORRELATION_LENGTHS: tuple[float, ...] = (0.1, 0.3, 1.0, 3.0)


def build_covariance(
    pt: np.ndarray,
    stat: np.ndarray,
    sys: np.ndarray,
    xi: float = 1.0,
) -> np.ndarray:
    """Build a parametric pT-bin covariance matrix.

    Parameters
    ----------
    pt   : 1-D array of pT bin centres [GeV].
    stat : 1-D array of statistical uncertainties (absolute).
    sys  : 1-D array of systematic uncertainties (absolute).
    xi   : Correlation length in log-pT space (dimensionless).
             ξ → 0  → fully diagonal (stat² + sys²)
             ξ → ∞  → all sys bins fully correlated

    Returns
    -------
    Σ : (n, n) symmetric positive-semi-definite matrix.

    Notes
    -----
    The Gaussian envelope exp(-|Δ log pT| / ξ) is chosen for its simplicity
    and monotone decrease.  D'Agostini recommends explicit correlation
    coefficients when available; the ξ-envelope is a conservative substitute.
    """
    pt = np.asarray(pt, dtype=float)
    stat = np.asarray(stat, dtype=float)
    sys = np.asarray(sys, dtype=float)
    n = len(pt)

    # Guard against zero or negative pT
    log_pt = np.log(np.maximum(pt, 1e-9))

    # Systematic correlation matrix: C_ij = exp(-|Δ log pT|_ij / ξ)
    delta_log_pt = np.abs(log_pt[:, None] - log_pt[None, :])
    sys_corr = np.exp(-delta_log_pt / max(xi, 1e-9))

    # Σ = diag(stat²) + sys_i · sys_j · C_ij
    sigma = np.diag(stat ** 2) + np.outer(sys, sys) * sys_corr
    return sigma


def is_positive_definite(matrix: np.ndarray) -> bool:
    """Return True if *matrix* is numerically positive definite (Cholesky test)."""
    try:
        cholesky(matrix)
        return True
    except LinAlgError:
        return False


def regularise_covariance(matrix: np.ndarray, epsilon: float = 1e-8) -> np.ndarray:
    """Add a small diagonal jitter to restore positive definiteness if needed.

    Modifies the matrix in place and returns it.  A warning is issued if
    regularisation is required.
    """
    if is_positive_definite(matrix):
        return matrix
    scale = float(np.max(np.abs(np.diag(matrix))))
    jitter = epsilon * scale
    matrix = matrix + jitter * np.eye(len(matrix))
    if not is_positive_definite(matrix):
        # Increase jitter until Cholesky succeeds
        for _ in range(20):
            jitter *= 10.0
            matrix += jitter * np.eye(len(matrix))
            if is_positive_definite(matrix):
                break
    warnings.warn(
        f"regularise_covariance: added diagonal jitter {jitter:.2e} to restore PSD.",
        stacklevel=2,
    )
    return matrix


def gls_chi2(
    y: np.ndarray,
    y_pred: np.ndarray,
    cov: np.ndarray,
) -> tuple[float, int]:
    """Compute GLS χ² and degrees of freedom.

    Uses Cholesky decomposition so that:
        χ² = r^T Σ⁻¹ r
    is evaluated as ||L⁻¹ r||² where L is the lower Cholesky factor.

    Parameters
    ----------
    y      : observed values (n,)
    y_pred : model predictions (n,)
    cov    : (n, n) covariance matrix

    Returns
    -------
    (chi2, ndf)  where ndf = n (caller subtracts n_params if desired)
    """
    r = np.asarray(y, dtype=float) - np.asarray(y_pred, dtype=float)
    cov = regularise_covariance(np.asarray(cov, dtype=float).copy())
    L = cholesky(cov)
    # Solve L z = r → z = L⁻¹ r
    z = solve(L, r)
    chi2 = float(z @ z)
    return chi2, len(r)


def gls_residuals(
    y: np.ndarray,
    y_pred: np.ndarray,
    cov: np.ndarray,
) -> np.ndarray:
    """Return Cholesky-whitened residuals z = L⁻¹(y - y_pred).

    These are the standardised residuals used to assess fit quality:
    under a correct model they are approximately N(0, I).
    """
    r = np.asarray(y, dtype=float) - np.asarray(y_pred, dtype=float)
    cov = regularise_covariance(np.asarray(cov, dtype=float).copy())
    L = cholesky(cov)
    return solve(L, r)


def chi2_envelope(
    pt: np.ndarray,
    stat: np.ndarray,
    sys: np.ndarray,
    y: np.ndarray,
    y_pred: np.ndarray,
    n_params: int,
    xi_values: Sequence[float] = CORRELATION_LENGTHS,
) -> dict[str, float | dict[str, float]]:
    """Compute GLS χ²/ndf over a grid of correlation lengths.

    Returns a dict with keys:
      - 'diag'         : diagonal (uncorrelated) χ²/ndf
      - 'correlated'   : dict mapping str(xi) → χ²/ndf
      - 'envelope_min' : minimum χ²/ndf across all ξ
      - 'envelope_max' : maximum χ²/ndf across all ξ
    """
    n = len(pt)
    ndf = n - n_params

    # Diagonal baseline
    diag_err = np.sqrt(stat ** 2 + sys ** 2)
    r = y - y_pred
    diag_chi2 = float(np.sum((r / diag_err) ** 2))
    diag_chi2_ndf = diag_chi2 / ndf if ndf > 0 else float("nan")

    correlated: dict[str, float] = {}
    for xi in xi_values:
        cov = build_covariance(pt, stat, sys, xi)
        c2, _ = gls_chi2(y, y_pred, cov)
        correlated[str(xi)] = c2 / ndf if ndf > 0 else float("nan")

    all_vals = list(correlated.values())
    return {
        "diag": diag_chi2_ndf,
        "correlated": correlated,
        "envelope_min": min(all_vals) if all_vals else float("nan"),
        "envelope_max": max(all_vals) if all_vals else float("nan"),
    }


# ---------------------------------------------------------------------------
# Smoke test (run as __main__)
# ---------------------------------------------------------------------------

def _smoke_test() -> None:
    """Verify PSD property and diagonal bias on synthetic data."""
    rng = np.random.default_rng(42)
    n = 20
    pt = np.linspace(0.2, 3.0, n)
    stat = rng.uniform(0.01, 0.05, n)
    sys = rng.uniform(0.02, 0.10, n)
    y = rng.normal(1.0, 0.05, n)
    y_pred = y + rng.normal(0.0, 0.03, n)

    results: list[str] = []
    for xi in CORRELATION_LENGTHS:
        cov = build_covariance(pt, stat, sys, xi)
        psd = is_positive_definite(cov)
        c2, _ = gls_chi2(y, y_pred, cov)
        results.append(f"  ξ={xi:4.1f}  PSD={psd}  GLS-χ²={c2:.3f}")

    # Diagonal bias
    diag_err = np.sqrt(stat ** 2 + sys ** 2)
    diag_c2 = float(np.sum(((y - y_pred) / diag_err) ** 2))
    cov_1 = build_covariance(pt, stat, sys, xi=1.0)
    gls_c2_1, _ = gls_chi2(y, y_pred, cov_1)
    bias = diag_c2 / gls_c2_1 if gls_c2_1 > 0 else float("nan")

    print("bgbw_covariance smoke test")
    print("\n".join(results))
    print(f"  diagonal_chi2_ndf_bias (diag/GLS@ξ=1) = {bias:.3f}  (expect ~1.2–1.5)")
    assert all("PSD=True" in r for r in results), "PSD check failed"
    print("PASS")


if __name__ == "__main__":
    _smoke_test()
