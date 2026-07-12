import pytest
from ignition.validation_policy import ValidationPolicy

def test_feed_down_boundaries():
    policy = ValidationPolicy()

    # Uncorrected feed-down (default / False): boundary is [0.06, 0.30]
    sev, msg = policy.validate_temperature(0.055, feed_down_corrected=False)
    assert sev == "warning"
    assert "low temperature < 0.06" in msg

    sev, msg = policy.validate_temperature(0.31, feed_down_corrected=False)
    assert sev == "warning"
    assert "high temperature > 0.3" in msg

    # Corrected feed-down: boundary is [0.05, 0.25]
    sev, msg = policy.validate_temperature(0.055, feed_down_corrected=True)
    assert sev == "ok"

    sev, msg = policy.validate_temperature(0.26, feed_down_corrected=True)
    assert sev == "warning"
    assert "high temperature > 0.25" in msg

    # Unknown (None): boundary is [0.05, 0.30]
    sev, msg = policy.validate_temperature(0.055, feed_down_corrected=None)
    assert sev == "ok"

def test_t_q_degeneracy():
    policy = ValidationPolicy()

    # Actual names from artifacts
    # T_kin and q_1
    sev, msg = policy.validate_t_q_degeneracy(0.86, "tsallis", "T_kin", "q_1")
    assert sev == "warning"
    assert "T-q Degeneracy" in msg

    # Below threshold
    sev, msg = policy.validate_t_q_degeneracy(0.84, "tsallis", "T_kin", "q_1")
    assert sev == "ok"

    # Different parameter names
    sev, msg = policy.validate_t_q_degeneracy(0.86, "tsallis", "temperature_1", "q")
    assert sev == "warning"
