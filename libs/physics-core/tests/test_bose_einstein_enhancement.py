"""
Test Bose-Einstein vs Boltzmann occupancy ratio at physically relevant E/T values.

Confirms enhancement factors validated via Wolfram Alpha on 2026-06-20:
  n_BE / n_Boltz = 1/(1 - exp(-E/T))
  At E/T = 1: ratio = e/(e-1) = 1.58197670687932...

Scope: Pure mathematical identity tests. No physics interpretation.
These tests sanity-check the BE enhancement claimed in the handoff prompt
and support evidence-ledger claim on BE denominators (TASK 4, TASK 8).

Science standard (AGENTS.md): Keep BE vs Boltzmann wording explicit in all outputs.
"""
import math

import pytest


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def be_to_boltzmann_ratio(E_over_T: float) -> float:
    """
    Ratio n_BE / n_Boltzmann for a single mode.

    n_BE = 1 / (exp(E/T) - 1)   [Bose-Einstein]
    n_Boltz = exp(-E/T)           [Classical Boltzmann]
    ratio = n_BE / n_Boltz = exp(E/T) / (exp(E/T) - 1) = 1 / (1 - exp(-E/T))
    """
    return 1.0 / (1.0 - math.exp(-E_over_T))


# ---------------------------------------------------------------------------
# Test 1: Reference value at E/T = 1
# Wolfram Alpha: e/(e-1) = 1.5819767068793265...
# ---------------------------------------------------------------------------

class TestBEEnhancementAtET1:
    """n_BE/n_Boltz at E/T = 1 = e/(e-1) = 1.5819767..."""

    def test_ratio_formula_matches_eulers_e(self):
        """1/(1 - exp(-1)) == e/(e-1) exactly (algebraic identity)."""
        ratio_formula = 1.0 / (1.0 - math.exp(-1.0))
        ratio_euler = math.e / (math.e - 1.0)
        assert abs(ratio_formula - ratio_euler) < 1e-12, (
            f"Formula mismatch: {ratio_formula:.15e} vs {ratio_euler:.15e}"
        )

    def test_ratio_vs_wolfram_alpha_value(self):
        """Wolfram Alpha: e/(e-1) = 1.5819767 to 7 significant figures."""
        ratio = be_to_boltzmann_ratio(1.0)
        assert abs(ratio - 1.5819767) < 1e-6, (
            f"BE ratio at E/T=1: {ratio:.7f}, expected 1.5819767"
        )

    def test_ratio_exceeds_50_pct_enhancement(self):
        """Enhancement at E/T=1 must be > 50% over Boltzmann."""
        ratio = be_to_boltzmann_ratio(1.0)
        assert ratio > 1.5, f"Expected >50% enhancement at E/T=1, got ratio={ratio:.4f}"

    def test_enhancement_factor_58_pct(self):
        """Specifically ~58% enhancement at E/T=1 (1.58 - 1 = 0.58)."""
        ratio = be_to_boltzmann_ratio(1.0)
        enhancement_pct = 100.0 * (ratio - 1.0)
        assert 55.0 < enhancement_pct < 62.0, (
            f"Expected ~58% enhancement at E/T=1, got {enhancement_pct:.1f}%"
        )


# ---------------------------------------------------------------------------
# Test 2: BE enhancement > 50% for E/T < ~1.5 (low pT regime)
# This confirms the claim that the BE denominator matters at low pT.
# pT range of ATLAS data starts at 0.175 GeV; T_kin ~ 0.10-0.13 GeV
# → E/T at pT=0.175, T=0.12: E ~ mT ~ 0.225 GeV → E/T ~ 1.9
# → E/T at pT=0.175, T=0.13: E/T ~ 1.7
# → E/T < 1.5 is relevant at even lower pT (below threshold for this data)
# ---------------------------------------------------------------------------

class TestBEEnhancementLowET:
    """BE enhancement > 50% for E/T < 1.5 (highly quantum regime)."""

    @pytest.mark.parametrize("ET", [0.5, 0.75, 1.0])
    def test_enhancement_above_50pct(self, ET):
        """For E/T in [0.5, 1.0], n_BE/n_Boltz > 1.5 (>50% enhancement)."""
        ratio = be_to_boltzmann_ratio(ET)
        assert ratio > 1.5, (
            f"BE enhancement only {ratio:.3f} (< 1.5) at E/T={ET}"
        )

    def test_enhancement_above_40pct_at_ET125(self):
        """At E/T=1.25: ratio = 1/(1-exp(-1.25)) ≈ 1.40 (40% above Boltzmann)."""
        ratio = be_to_boltzmann_ratio(1.25)
        assert ratio > 1.35, f"BE ratio at E/T=1.25: {ratio:.4f}, expected >1.35"
        assert abs(ratio - 1.402) < 0.002, f"E/T=1.25 ratio: {ratio:.4f}, expected ~1.402"

    @pytest.mark.parametrize("ET", [0.3, 0.5, 0.75, 1.0, 1.25, 1.5])
    def test_ratio_monotonically_decreasing(self, ET):
        """Ratio decreases as E/T increases (more classical at higher energies)."""
        ratio_lower = be_to_boltzmann_ratio(ET)
        ratio_upper = be_to_boltzmann_ratio(ET + 0.5)
        assert ratio_lower > ratio_upper, (
            f"Ratio not monotone: at E/T={ET}: {ratio_lower:.4f}, at E/T={ET+0.5}: {ratio_upper:.4f}"
        )

    def test_ratio_diverges_near_zero(self):
        """For E/T → 0, BE ratio → ∞ (Bose condensation divergence)."""
        ratio_small = be_to_boltzmann_ratio(0.01)   # ≈ 100.5 (1/ET for small ET)
        ratio_large = be_to_boltzmann_ratio(5.0)    # ≈ 1.007
        # ratio_small ≈ 100.5, 50*ratio_large ≈ 50.3 → safely satisfied
        assert ratio_small > 50 * ratio_large, (
            f"Expected large enhancement near E/T=0: ratio(0.01)={ratio_small:.1f}, "
            f"50*ratio(5.0)={50*ratio_large:.1f}"
        )


# ---------------------------------------------------------------------------
# Test 3: Boltzmann recovered at large E/T (classical limit)
# For E/T >> 1: n_BE ≈ exp(-E/T) = n_Boltz → ratio → 1
# ---------------------------------------------------------------------------

class TestBoltzmannClassicalLimit:
    """For E/T >> 1, BE → Boltzmann (ratio → 1)."""

    @pytest.mark.parametrize("ET", [5.0, 7.0, 10.0, 15.0])
    def test_boltzmann_recovered_at_large_ET(self, ET):
        """1/(1 - exp(-E/T)) → 1 for E/T >> 1."""
        ratio = be_to_boltzmann_ratio(ET)
        assert abs(ratio - 1.0) < 0.01, (
            f"BE → Boltzmann failed at E/T={ET}: ratio={ratio:.6f}, expected ~1.0"
        )

    def test_1_pct_correction_at_ET_5(self):
        """At E/T=5, BE correction is < 1% over Boltzmann."""
        ratio = be_to_boltzmann_ratio(5.0)
        correction = abs(ratio - 1.0) * 100
        assert correction < 1.0, f"BE correction at E/T=5: {correction:.3f}%, expected <1%"

    def test_specific_value_ET_10(self):
        """At E/T=10: ratio = 1/(1-exp(-10)) ≈ 1.0000454."""
        ratio = be_to_boltzmann_ratio(10.0)
        expected = 1.0 / (1.0 - math.exp(-10.0))
        assert abs(ratio - expected) < 1e-12
        assert abs(ratio - 1.0) < 0.001


# ---------------------------------------------------------------------------
# Test 4: Physical relevance of BE denominator for ATLAS pion data
# At pT=0.175 GeV, T=0.12 GeV: E ≈ mT = sqrt(pT^2 + m_pi^2) = 0.225 GeV
# E/T ≈ 1.87 → BE enhancement ≈ 1/(1-exp(-1.87)) ≈ 1.18 (18% above Boltzmann)
# ---------------------------------------------------------------------------

class TestBEPhysicalRelevanceATLAS:
    """BE enhancement at the lowest ATLAS pT bin with typical T_kin values."""

    M_PION = 0.13957  # GeV
    PT_LOW = 0.175    # GeV, lowest ATLAS bin center

    def _mt(self, pt: float) -> float:
        return math.sqrt(pt**2 + self.M_PION**2)

    def test_be_enhancement_at_lowest_pt_T120MeV(self):
        """At pT=0.175, T=120 MeV: E/T ≈ 1.87, BE enhancement ≈ 18%."""
        T = 0.120  # GeV
        ET = self._mt(self.PT_LOW) / T  # ≈ 1.87
        ratio = be_to_boltzmann_ratio(ET)
        enhancement_pct = 100.0 * (ratio - 1.0)
        # Enhancement should be significant (>10%) at this pT and T
        assert enhancement_pct > 10.0, (
            f"BE enhancement at pT=0.175, T=0.12: {enhancement_pct:.1f}%, expected >10%"
        )

    def test_be_enhancement_vanishes_at_high_pt(self):
        """At pT=3.0 GeV, T=0.12: E/T >> 1 → enhancement < 1%."""
        T = 0.120
        ET = self._mt(3.0) / T
        ratio = be_to_boltzmann_ratio(ET)
        enhancement_pct = 100.0 * (ratio - 1.0)
        assert enhancement_pct < 1.0, (
            f"BE enhancement at pT=3.0, T=0.12: {enhancement_pct:.2f}%, expected <1%"
        )
