#!/usr/bin/env python3
from __future__ import annotations
"""Smoke-test assert_fit_gate and generate_fit_dashboard imports and basic logic."""
import sys
sys.path.insert(0, "/home/ubuntu/aisci")

from physics.src.fitting_pipeline import (
    assert_fit_gate,
    generate_fit_dashboard,
    GATE_CHI2_NDF_MAX,
    GATE_CHI2_NDF_MIN,
    GATE_EDM_MAX,
    GATE_REL_ERROR_MAX,
    FitSpec,
    manuscript_fit_spec,
)

print(f"Gates: chi2_ndf_max={GATE_CHI2_NDF_MAX}, chi2_ndf_min={GATE_CHI2_NDF_MIN}, edm_max={GATE_EDM_MAX}, rel_error_max={GATE_REL_ERROR_MAX}")

# Build a minimal FitSpec for testing
spec = manuscript_fit_spec(component_count=1, eta_max=0.8, mass_gev=0.13957)

# Case 1: perfect fit — should pass
good_result = {
    "success": True,
    "has_accurate_covar": True,
    "chi2_ndf": 1.2,
    "edm": 0.001,
    "aic": 100.0,
    "bic": 110.0,
    "parameter_values": {"norm_1": 5.0, "temperature_1": 0.15, "U_1": 0.5},
    "parameter_errors": {"norm_1": 0.3, "temperature_1": 0.01, "U_1": 0.05},
}
verdict = assert_fit_gate(good_result, spec, "bin_21-30")
assert verdict["gate_passed"], f"Expected pass, got: {verdict}"
print(f"[PASS] Good fit correctly passes gate: chi2_ndf={verdict['chi2_ndf']}")

# Case 2: poor chi2/ndf — should fail gate 3
bad_chi2 = {**good_result, "chi2_ndf": 8.5}
verdict2 = assert_fit_gate(bad_chi2, spec, "bin_31-40")
assert not verdict2["gate_passed"], f"Expected fail on bad chi2, got: {verdict2}"
assert any("chi2/ndf" in f for f in verdict2["gate_failures"]), verdict2
print(f"[PASS] High chi2/ndf correctly fails gate: {verdict2['gate_failures']}")

# Case 3: unconstrained parameter — should fail gate 5
unconstrained = {**good_result, "parameter_errors": {"norm_1": 0.3, "temperature_1": 0.01, "U_1": 1.5}}
verdict3 = assert_fit_gate(unconstrained, spec, "bin_41-50")
assert not verdict3["gate_passed"], f"Expected fail on unconstrained param, got: {verdict3}"
assert any("Unconstrained" in f for f in verdict3["gate_failures"]), verdict3
print(f"[PASS] Unconstrained param correctly fails gate: {verdict3['gate_failures']}")

# Case 4: non-convergent — should fail gate 1
no_conv = {**good_result, "success": False}
verdict4 = assert_fit_gate(no_conv, spec, "bin_51-60")
assert not verdict4["gate_passed"]
print(f"[PASS] Non-convergent fit correctly fails gate: {verdict4['gate_failures']}")

print("\nAll assert_fit_gate smoke tests PASSED.")
