import pytest
from validation_policy import ValidationPolicy, default_policy

def test_validation_policy_default():
    policy = default_policy
    assert policy.chi2_warning == 3.0
    assert policy.chi2_critical == 20.0
    assert policy.rho_warning == 0.90

def test_validation_policy_custom():
    policy = ValidationPolicy(version="test", chi2_critical=50.0)
    assert policy.chi2_critical == 50.0

def test_evaluate_chi2():
    policy = default_policy

    sev, msg = policy.validate_chi2(1.5)
    assert sev == "ok"

    sev, msg = policy.validate_chi2(5.0)
    assert sev == "warning"

    sev, msg = policy.validate_chi2(25.0)
    assert sev == "critical"

def test_evaluate_correlation():
    policy = default_policy

    # OK
    sev, msg = policy.validate_correlation(0.5, "q", "T")
    assert sev == "ok"

    # Warning
    sev, msg = policy.validate_correlation(0.92, "q", "T")
    assert sev == "warning"

    # Critical
    sev, msg = policy.validate_correlation(0.98, "q", "T")
    assert sev == "critical"

    # Perfect correlation (usually means fixing parameter failed or redundant)
    sev, msg = policy.validate_correlation(-1.0, "p1", "p2")
    assert sev == "critical"
