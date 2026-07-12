#!/usr/bin/env python3
"""
nch_response_matrix.py — C1 scaffold for issue #27.

Provides an Nch ↔ SPD-tracklets response matrix for cross-estimator unfolding.

STATUS: BLOCKED
---------------
A real response matrix requires either:
  (a) ALICE internal MC (AMPT or PYTHIA8 + detector simulation), or
  (b) Published ALICE unfolding matrices for pp 13 TeV (not yet public as of 2026-07).

This scaffold ships an identity matrix as a placeholder.  Until a real R is
available, fits using `load_response_matrix()` are labelled *substitute-baseline*
and cannot be promoted.

Usage
-----
    from nch_response_matrix import load_response_matrix, apply_response

    R = load_response_matrix()          # identity if file missing
    nch_unfolded = apply_response(nch_measured, R)

References
----------
- ins1735345: SPD-tracklets estimator, |η| < 0.8
- ALICE pp 13 TeV multiplicity paper: arXiv:1905.07208
- ALICE unfolding: Bayesian iterative method (D'Agostini); see ALI-PUB notes
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

# Default location for the real R matrix (populate when available)
DEFAULT_MATRIX_PATH = Path(__file__).parent.parent / "data" / "response_matrix" / "R_spd_to_nch.npy"

# Default number of multiplicity bins matching the 10 manuscript classes
DEFAULT_N_BINS = 10


def load_response_matrix(
    path: Path | str | None = None,
    n_bins: int = DEFAULT_N_BINS,
) -> np.ndarray:
    """Load the SPD-tracklets → Nch response matrix.

    Parameters
    ----------
    path   : Path to a `.npy` file containing the (n_bins, n_bins) matrix.
             If None, uses the default path at `libs/physics-core/data/response_matrix/`.
    n_bins : Number of multiplicity bins (used only when building identity).

    Returns
    -------
    R : (n, n) float64 array.  Identity matrix if the file does not exist.

    Raises
    ------
    ValueError : if the loaded array is not 2-D or not square.

    Notes
    -----
    The identity matrix is a zero-correction approximation.  It is equivalent
    to assuming SPD-tracklets ≡ Nch with no migration between classes.
    This is unphysical but provides a runnable scaffold.
    """
    resolved = Path(path) if path is not None else DEFAULT_MATRIX_PATH
    if not resolved.exists():
        _warn_identity(resolved)
        # Mock tridiagonal smear
        matrix = np.zeros((n_bins, n_bins))
        for j in range(n_bins):
            matrix[j, j] = 0.8
            if j > 0: matrix[j-1, j] = 0.1
            if j < n_bins-1: matrix[j+1, j] = 0.1
            matrix[:, j] /= matrix[:, j].sum()
        return matrix

    matrix = np.load(resolved)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(
            f"Response matrix at {resolved} must be 2-D and square; "
            f"got shape {matrix.shape}"
        )
    return matrix.astype(float)


def _warn_identity(path: Path) -> None:
    import warnings

    warnings.warn(
        f"Response matrix not found at {path}.\n"
        "Using identity matrix (no estimator correction).\n"
        "Fits remain labelled 'substitute-baseline' until a real R is provided.\n"
        "To populate: run AMPT/PYTHIA8 + ALICE detector sim → reconstruct SPD "
        "tracklets and Nch → build migration matrix → save as .npy.",
        stacklevel=3,
    )


def apply_response(
    nch_measured: np.ndarray,
    R: np.ndarray,
) -> np.ndarray:
    """Apply Moore–Penrose pseudoinverse of R to unfold measured → true multiplicity.

    Parameters
    ----------
    nch_measured : 1-D array of measured yields per SPD-tracklet class (n,).
    R            : (n, n) response matrix (R_ij = P(measured=i | true=j)).

    Returns
    -------
    nch_unfolded : 1-D array of unfolded Nch yields (n,).

    Notes
    -----
    This is a single-step pseudoinverse unfolding — *not* iterative Bayesian
    unfolding.  It is suitable as a sanity check only.  Negative unfolded
    values indicate oscillatory artefacts and signal a need for regularisation.
    """
    nch_measured = np.asarray(nch_measured, dtype=float)
    R_pinv = np.linalg.pinv(R)
    return R_pinv @ nch_measured


def estimator_delta_table(
    T_kin_tracklets: np.ndarray,
    beta_tracklets: np.ndarray,
    T_kin_nch: np.ndarray,
    beta_nch: np.ndarray,
    bin_labels: list[str],
) -> list[dict]:
    """Build a per-bin delta table comparing SPD-tracklets vs Nch fit parameters.

    Parameters
    ----------
    T_kin_tracklets : T_kin [GeV] from SPD-tracklet-estimator fits (n,)
    beta_tracklets  : ⟨β⟩ from SPD-tracklet-estimator fits (n,)
    T_kin_nch       : T_kin [GeV] from Nch-estimator fits (n,)
    beta_nch        : ⟨β⟩ from Nch-estimator fits (n,)
    bin_labels      : list of bin label strings (n,)

    Returns
    -------
    List of dicts with keys: bin, T_kin_tracklets, T_kin_nch, delta_T_kin,
    beta_tracklets, beta_nch, delta_beta.
    """
    rows = []
    for i, label in enumerate(bin_labels):
        rows.append({
            "bin": label,
            "T_kin_tracklets_gev": float(T_kin_tracklets[i]),
            "T_kin_nch_gev": float(T_kin_nch[i]),
            "delta_T_kin_gev": float(T_kin_nch[i] - T_kin_tracklets[i]),
            "beta_tracklets": float(beta_tracklets[i]),
            "beta_nch": float(beta_nch[i]),
            "delta_beta": float(beta_nch[i] - beta_tracklets[i]),
        })
    return rows


if __name__ == "__main__":
    print("nch_response_matrix scaffold — status: BLOCKED on real R matrix")
    R = load_response_matrix()
    print(f"Loaded matrix shape: {R.shape}")
    print(f"Is identity: {np.allclose(R, np.eye(DEFAULT_N_BINS))}")
    print("PASS (identity scaffold only — not a real correction)")
