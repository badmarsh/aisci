"""
Test dy/deta Jacobian: numerical significance and correct formula.

The Jacobian for converting from pseudorapidity (eta) to rapidity (y) when
integrating over eta acceptance is:
    dy/deta = p / (mT * cosh(eta))  where p = sqrt(pt^2*cosh^2(eta) + m^2*sinh^2(eta))

This is a 22% correction at pT=0.175 GeV (lowest ATLAS data bin) and must be
accounted for in fits against dN/(2*pi*pT*dpT*deta) data.

Scope: Pure mathematical identity tests. No physics interpretation of fit
parameters. Reference: handoff prompt 2026-06-20, validated via SymPy.

Evidence-ledger reference: claim "dy/deta Jacobian is applied in manuscript" —
TASK 5 in handoff prompt.
"""
import math

import pytest


# ---------------------------------------------------------------------------
# Core Jacobian formula (local copy — does NOT import production code)
# ---------------------------------------------------------------------------

def jacobian_dy_deta(pt: float, mass: float, eta: float) -> float:
    """
    Compute dy/deta at a given (pT, mass, eta).

    Derivation:
        rapidity y = ln((E + p_z) / (E - p_z)) / 2
        dy/deta = p_total / (mT * cosh(eta))
    where
        p_total = sqrt(pT^2 * cosh^2(eta) + m^2 * sinh^2(eta))
        mT = sqrt(pT^2 + m^2)
    """
    mt = math.sqrt(pt**2 + mass**2)
    p_total = math.sqrt(pt**2 * math.cosh(eta)**2 + mass**2 * math.sinh(eta)**2)
    return p_total / (mt * math.cosh(eta))


# ---------------------------------------------------------------------------
# Test 1: Reference value at lowest ATLAS bin, eta=0
# pT=0.175 GeV, m_pi=0.13957 GeV, eta=0  → dy/deta = 0.7818
# This is a 21.8% correction (>10% threshold for publication relevance).
# ---------------------------------------------------------------------------

class TestJacobianAtLowestBin:
    """At pT=0.175 GeV (lowest ATLAS data bin), Jacobian is 0.782 — 22% correction."""

    M_PION = 0.13957  # GeV, charged pion mass

    def test_jacobian_value_at_eta0(self):
        """dy/deta(pT=0.175, eta=0) = 0.7818 ± 0.001."""
        j = jacobian_dy_deta(0.175, self.M_PION, 0.0)
        assert abs(j - 0.7818) < 0.001, (
            f"Jacobian at pT=0.175, eta=0: got {j:.4f}, expected ~0.7818"
        )

    def test_jacobian_is_less_than_one(self):
        """Jacobian < 1 means neglecting it overestimates the yield."""
        j = jacobian_dy_deta(0.175, self.M_PION, 0.0)
        assert j < 1.0, f"Jacobian should be < 1 at low pT: {j}"

    def test_correction_exceeds_10_pct(self):
        """Correction (1 - dy/deta) must exceed 10% at pT=0.175 GeV."""
        j = jacobian_dy_deta(0.175, self.M_PION, 0.0)
        correction = 1.0 - j
        assert correction > 0.10, (
            f"Expected >10% correction, got {100*correction:.1f}% at pT=0.175 GeV"
        )

    def test_correction_is_22_pct(self):
        """Specifically, the correction should be ~22% (reference: handoff prompt)."""
        j = jacobian_dy_deta(0.175, self.M_PION, 0.0)
        correction_pct = 100.0 * (1.0 - j)
        assert 20.0 < correction_pct < 24.0, (
            f"Expected ~22% correction, got {correction_pct:.1f}% at pT=0.175 GeV"
        )


# ---------------------------------------------------------------------------
# Test 2: ATLAS acceptance edge at eta=0.8 (ATLAS |eta|<0.8 for charged tracks)
# Reference: dy/deta(pT=0.175, eta=0.8) ≈ 0.8847
# ---------------------------------------------------------------------------

class TestJacobianAtATLASEdge:
    """At eta=0.8 (ATLAS acceptance edge), Jacobian is ~0.885."""

    M_PION = 0.13957

    def test_jacobian_at_eta_0p8(self):
        """dy/deta(pT=0.175, eta=0.8) ≈ 0.8847 ± 0.001."""
        j = jacobian_dy_deta(0.175, self.M_PION, 0.8)
        assert abs(j - 0.8847) < 0.001, (
            f"Jacobian at pT=0.175, eta=0.8: got {j:.4f}, expected ~0.8847"
        )

    def test_jacobian_increases_with_eta(self):
        """Jacobian increases as eta increases from 0 (correction is smaller at large eta)."""
        j0 = jacobian_dy_deta(0.175, self.M_PION, 0.0)
        j08 = jacobian_dy_deta(0.175, self.M_PION, 0.8)
        assert j08 > j0, (
            f"Expected Jacobian to increase with eta: j(0)={j0:.4f} j(0.8)={j08:.4f}"
        )


# ---------------------------------------------------------------------------
# Test 3: Jacobian approaches 1 at large pT (massless limit)
# At pT >> m: mT ≈ pT, p_total ≈ pT*cosh(eta) → dy/deta → 1
# ---------------------------------------------------------------------------

class TestJacobianHighPtLimit:
    """At high pT, Jacobian → 1 (rapidity ≈ pseudorapidity)."""

    M_PION = 0.13957

    @pytest.mark.parametrize("pt", [5.0, 10.0, 20.0])
    def test_jacobian_approaches_one(self, pt):
        """dy/deta → 1 for pT >> m_pi at any eta."""
        j = jacobian_dy_deta(pt, self.M_PION, 0.0)
        assert abs(j - 1.0) < 0.005, (
            f"Jacobian should be ~1 at pT={pt} GeV: got {j:.6f}"
        )

    @pytest.mark.parametrize("pt", [0.15, 0.3, 0.5, 1.0, 2.0, 5.0, 10.0])
    def test_jacobian_in_0_to_1(self, pt):
        """Jacobian must be strictly in (0, 1] for all physical pT."""
        j = jacobian_dy_deta(pt, self.M_PION, 0.0)
        assert 0.0 < j <= 1.0 + 1e-10, (
            f"Jacobian out of range at pT={pt}: {j:.6f}"
        )

    def test_jacobian_exactly_one_at_zero_mass(self):
        """Massless particle: dy/deta = 1 exactly at eta=0."""
        m = 1e-10  # effectively massless
        j = jacobian_dy_deta(1.0, m, 0.0)
        assert abs(j - 1.0) < 1e-6, f"Massless Jacobian != 1: {j}"


# ---------------------------------------------------------------------------
# Test 4: Consistency — mean Jacobian across ATLAS acceptance
# The eta-averaged Jacobian over [-0.8, 0.8] at pT=0.175 GeV should be ~0.83,
# corresponding to a ~17% average correction over the acceptance.
# ---------------------------------------------------------------------------

class TestJacobianAcceptanceAverage:
    """Mean Jacobian over ATLAS |eta| < 0.8 at lowest pT bin."""

    M_PION = 0.13957

    def test_mean_jacobian_over_atlas_acceptance(self):
        """Mean dy/deta over eta in [-0.8, 0.8] at pT=0.175 should be in [0.80, 0.88]."""
        eta_values = [i * 0.1 for i in range(-8, 9)]  # -0.8 to 0.8 in steps of 0.1
        mean_j = sum(jacobian_dy_deta(0.175, self.M_PION, e) for e in eta_values) / len(eta_values)
        assert 0.80 < mean_j < 0.88, (
            f"Mean Jacobian over ATLAS acceptance = {mean_j:.4f}, expected 0.80-0.88"
        )
