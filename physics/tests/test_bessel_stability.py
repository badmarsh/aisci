"""
Test BGBW Bessel fix: ive/kve reconstruction equals I0*K1 exactly.

Scope: Pure numerical identity tests validating the overflow fix applied to
blast_wave_component_scalar() in fitting_pipeline.py (Bessel overflow fix, 2026-06-20).
These tests are sanity checks at the level of mathematical identities.
They do NOT interpret fit parameters or promote scientific claims.

Reference (from AGENTS.md): Do not interpret fit parameters physically until
chi2/ndf, covariance, correlations, residuals, fit-range sensitivity, and
baseline comparisons exist.
"""
import math
import sys
import os

import numpy as np
import pytest
from scipy.special import ive, kve, i0, k1

# ---------------------------------------------------------------------------
# Helper: add src to path so we can import fitting_pipeline functions
# ---------------------------------------------------------------------------
_SRC = os.path.join(os.path.dirname(__file__), "..", "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)


# ---------------------------------------------------------------------------
# Test 1: Identity I_0(a)*K_1(b) = ive(0,a)*kve(1,b)*exp(a-b) exactly
# Wolfram Alpha reference value: I_0(3.5)*K_1(4.2) = 0.073326096292702972
# ---------------------------------------------------------------------------

class TestBesselReconstructionExact:
    """ive/kve + exp(a-b) recovers direct I0*K1 to float64 precision."""

    def test_reference_value_i0k1(self):
        """Wolfram Alpha: I0(3.5)*K1(4.2) = 0.073326096292702972."""
        a, b = 3.5, 4.2
        direct = i0(a) * k1(b)
        assert abs(direct - 0.073326096292702972) < 1e-10, (
            f"I0({a})*K1({b}) = {direct:.15e} vs WA 0.073326096292702972"
        )

    def test_scaled_reconstruction_matches_direct(self):
        """ive(0,a)*kve(1,b)*exp(a-b) == I0(a)*K1(b) to 1e-12."""
        a, b = 3.5, 4.2
        direct = i0(a) * k1(b)
        scaled = ive(0, a) * kve(1, b) * np.exp(a - b)
        assert abs(direct - scaled) < 1e-12, (
            f"Reconstruction error: direct={direct:.15e}, scaled={scaled:.15e}"
        )

    @pytest.mark.parametrize("a,b", [
        (0.1, 0.5),
        (1.0, 2.0),
        (3.5, 4.2),   # Wolfram Alpha reference
        (10.0, 12.0),
        (50.0, 55.0),  # Would overflow with naive I0*K1
        (100.0, 110.0),
        (200.0, 210.0),
    ])
    def test_reconstruction_parametric(self, a, b):
        """Scaled reconstruction is accurate across a wide argument range."""
        scaled = ive(0, a) * kve(1, b) * np.exp(a - b)
        assert np.isfinite(scaled), f"Overflow at a={a}, b={b}"
        assert scaled > 0, f"Non-positive value at a={a}, b={b}"
        if a < 20 and b < 20:
            direct = i0(a) * k1(b)
            if np.isfinite(direct):
                assert abs(direct - scaled) / (abs(direct) + 1e-300) < 1e-10, (
                    f"Relative error {abs(direct-scaled)/abs(direct):.2e} at a={a}, b={b}"
                )

    def test_naive_overflow_at_large_args(self):
        """Naive I0*K1 overflows at large arguments; scaled form does not."""
        a, b = 800.0, 850.0
        naive = i0(a) * k1(b)
        scaled = ive(0, a) * kve(1, b) * np.exp(a - b)
        # Naive should overflow (inf) or underflow to 0, scaled should be finite
        assert not np.isfinite(naive) or naive == 0.0, (
            "Expected naive I0*K1 to fail at a=800, b=850"
        )
        assert np.isfinite(scaled), "Scaled form must be finite at large args"
        assert scaled > 0


# ---------------------------------------------------------------------------
# Test 2: blast_wave_component_scalar produces finite, non-negative values
# in physically relevant parameter ranges.
# ---------------------------------------------------------------------------

class TestBlastWaveNoOverflow:
    """blast_wave_component_scalar must be finite and non-negative everywhere."""

    def _get_bw_fn(self):
        """Import blast_wave_component_scalar from fitting_pipeline.py."""
        try:
            from fitting_pipeline import blast_wave_component_scalar
            return blast_wave_component_scalar
        except ImportError:
            pytest.skip("fitting_pipeline not importable in this environment")

    def test_finite_at_standard_parameters(self):
        """Standard parameters (T=120 MeV, beta_s=0.6): must be finite and positive."""
        bw = self._get_bw_fn()
        result = bw(0.5, 1.0, 0.12, 0.6, 1.0, 0.13957)
        assert np.isfinite(result), f"Not finite: {result}"
        assert result >= 0.0

    def test_no_overflow_high_flow(self):
        """High beta_s=0.95, low T=0.08 GeV → large Bessel arguments; must not overflow."""
        bw = self._get_bw_fn()
        result = bw(2.0, 1.0, 0.08, 0.95, 1.0, 0.13957)
        assert np.isfinite(result), f"Overflow at high flow: {result}"
        assert result >= 0.0

    @pytest.mark.parametrize("pt", [0.15, 0.3, 0.5, 1.0, 2.0, 3.0, 5.0])
    @pytest.mark.parametrize("beta_s", [0.3, 0.6, 0.85, 0.95])
    def test_parametric_finite(self, pt, beta_s):
        """No overflow for any pT × beta_s combination at T=0.10 GeV."""
        bw = self._get_bw_fn()
        result = bw(pt, 1.0, 0.10, beta_s, 1.0, 0.13957)
        assert np.isfinite(result), f"Overflow at pT={pt}, beta_s={beta_s}: {result}"
        assert result >= 0.0


# ---------------------------------------------------------------------------
# Test 3: Physical constraint a <= b always holds (exp factor <= 1)
# Proof: a = pT*sinh(rho)/T, b = mT*cosh(rho)/T
#        b - a = (mT*cosh(rho) - pT*sinh(rho))/T >= 0
#        because mT >= pT and cosh >= sinh for all rho >= 0.
# ---------------------------------------------------------------------------

class TestExpFactorBounded:
    """exp(a-b) must always satisfy 0 < exp(a-b) <= 1 for physical parameters."""

    @pytest.mark.parametrize("pt", [0.15, 0.3, 0.5, 1.0, 2.0, 3.0])
    @pytest.mark.parametrize("beta_s", [0.1, 0.3, 0.6, 0.9, 0.99])
    def test_exp_factor_at_most_one(self, pt, beta_s):
        """a <= b for all physical (pT, beta_s) — so exp(a-b) in (0,1]."""
        mass = 0.13957  # pion mass in GeV
        T = 0.12
        rho = math.atanh(min(beta_s, 0.999999))
        mt = math.sqrt(pt**2 + mass**2)
        a = pt * math.sinh(rho) / T   # I0 argument
        b = mt * math.cosh(rho) / T   # K1 argument
        diff = a - b
        assert diff <= 1e-10, (
            f"a > b at pT={pt}, beta_s={beta_s}: a={a:.4f}, b={b:.4f}, diff={diff:.6f}"
        )
        assert math.exp(diff) <= 1.0 + 1e-10, (
            f"exp(a-b) > 1 at pT={pt}, beta_s={beta_s}"
        )
        assert math.isfinite(math.exp(diff)), "exp(a-b) must be finite"

    def test_marginally_physical_edge(self):
        """At pT → mT (massless limit): mT = pT, a and b have cosh vs sinh — still b > a."""
        # Near-massless: m → 0, mT → pT
        pt = 1.0
        mass = 1e-6  # near-massless
        mt = math.sqrt(pt**2 + mass**2)
        T = 0.1
        rho = math.atanh(0.9)
        a = pt * math.sinh(rho) / T
        b = mt * math.cosh(rho) / T
        # cosh(rho) > sinh(rho) for all finite rho, so b >= a
        assert b >= a - 1e-9, f"Massless limit violated: b={b:.4f} < a={a:.4f}"
