"""
Read-only identity tests for mathematical objects defined in
libs/physics-core/src/boson_paper_analysis.py.

Scope rules (per AGENTS.md and project separation policy):
- These tests cover pure-math identities only; they do NOT import the
  production script, do NOT read or write any data files, do NOT hit any
  network endpoint, and do NOT promote or interpret any physics claim.
- They are sanity checks at the level of equations, not scientific conclusions.
- Do not add chi2/ndf interpretation, claim-state promotion, or physical
  commentary here; those belong in research/robert/evidence-ledger.md and
  research/robert/next-actions.md.
"""

import math
import pytest


# ---------------------------------------------------------------------------
# Identity 1: velocity parameterisation v = U / sqrt(1 + U^2)
# Source: boson_paper_analysis.py Section 2, Robert's U-parameterisation.
# The check is purely algebraic; no physics interpretation is attached.
# ---------------------------------------------------------------------------

def velocity_from_U(U: float) -> float:
    """v = U / sqrt(1 + U^2).  Local copy; does not import production code."""
    return U / math.sqrt(1.0 + U * U)


def gamma_from_U(U: float) -> float:
    """gamma = sqrt(1 + U^2).  Local copy."""
    return math.sqrt(1.0 + U * U)


class TestVelocityParameterisation:
    """v = U/sqrt(1+U^2) is in [0, 1) for all finite U >= 0."""

    @pytest.mark.parametrize("U", [0.0, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 100.0])
    def test_velocity_is_subluminal(self, U):
        v = velocity_from_U(U)
        assert 0.0 <= v < 1.0, f"v={v} is not in [0, 1) for U={U}"

    def test_velocity_zero_at_U_zero(self):
        assert velocity_from_U(0.0) == pytest.approx(0.0)

    @pytest.mark.parametrize("U", [100.0, 1000.0])
    def test_velocity_approaches_one_for_large_U(self, U):
        v = velocity_from_U(U)
        assert v > 0.999, f"Expected v near 1 for large U={U}, got {v}"

    @pytest.mark.parametrize("U", [0.3, 1.0, 4.0])
    def test_gamma_v_equals_U(self, U):
        """gamma * v == U exactly (defining property of this parameterisation)."""
        g = gamma_from_U(U)
        v = velocity_from_U(U)
        assert g * v == pytest.approx(U, rel=1e-9)


# ---------------------------------------------------------------------------
# Identity 2: cosh addition formula used for the exponent.
# Source: boson_paper_analysis.py Section 1.
# pT * cosh(eta) * cosh(Y) - pT * sinh(eta) * sinh(Y) == pT * cosh(eta - Y)
# ---------------------------------------------------------------------------

class TestCoshAdditionFormula:
    """The exponent pT*cosh(eta-Y) == pT*(cosh(eta)cosh(Y) - sinh(eta)sinh(Y))."""

    @pytest.mark.parametrize("eta,Y", [
        (0.0, 0.0),
        (0.5, 0.3),
        (-1.2, 0.8),
        (2.5, 1.0),
        (0.0, 2.0),
    ])
    def test_cosh_addition_identity(self, eta, Y):
        pT = 1.5  # arbitrary positive value; identity is scale-independent
        lhs = pT * (math.cosh(eta) * math.cosh(Y) - math.sinh(eta) * math.sinh(Y))
        rhs = pT * math.cosh(eta - Y)
        assert lhs == pytest.approx(rhs, rel=1e-9)


# ---------------------------------------------------------------------------
# Identity 3: pT Gaussian integral  integral_0^inf pT * exp(-lambda * pT) dpT == 1/lambda^2
# Source: boson_paper_analysis.py Section 3 normalization check.
# Tested numerically; does not perform any fit or data read.
# ---------------------------------------------------------------------------

def numerical_pT_integral(lam: float, n_steps: int = 50_000) -> float:
    """Approximate integral_0^inf pT exp(-lam*pT) dpT by trapezoidal rule."""
    # Truncate at 10/lam where the integrand is negligibly small.
    pT_max = 10.0 / lam
    dt = pT_max / n_steps
    total = 0.0
    for i in range(n_steps):
        pT = (i + 0.5) * dt
        total += pT * math.exp(-lam * pT) * dt
    return total


class TestNormalizationIntegral:
    """int_0^inf pT exp(-lambda pT) dpT = 1/lambda^2."""

    @pytest.mark.parametrize("lam", [0.5, 1.0, 2.0, 5.0])
    def test_pT_integral_matches_analytic(self, lam):
        analytic = 1.0 / (lam ** 2)
        numeric = numerical_pT_integral(lam)
        # 0.1% tolerance is well within trapezoidal-rule accuracy at 50k steps.
        assert numeric == pytest.approx(analytic, rel=1e-3)


# ---------------------------------------------------------------------------
# Identity 4: rapidity Y = arcsinh(U)  (sinh(Y) == U by definition)
# Source: boson_paper_analysis.py Section 2.
# ---------------------------------------------------------------------------

class TestRapidityFromU:
    """Y = arcsinh(U) implies sinh(Y) == U."""

    @pytest.mark.parametrize("U", [0.0, 0.1, 0.5, 1.0, 2.0, 5.0])
    def test_sinh_of_arcsinh_U_equals_U(self, U):
        Y = math.asinh(U)
        assert math.sinh(Y) == pytest.approx(U, rel=1e-12, abs=1e-15)

    @pytest.mark.parametrize("U", [0.3, 1.0, 4.0])
    def test_cosh_of_arcsinh_U_equals_gamma(self, U):
        """cosh(arcsinh(U)) == sqrt(1 + U^2) == gamma."""
        Y = math.asinh(U)
        expected_gamma = math.sqrt(1.0 + U * U)
        assert math.cosh(Y) == pytest.approx(expected_gamma, rel=1e-12)
