import pytest
from validation_policy import ValidationPolicy

def test_validation_policy_default():
    policy = ValidationPolicy()
    assert policy.chi2_warning == 10.0
    assert policy.chi2_critical == 200.0
    assert policy.rho_warning == 0.95

def test_validation_policy_custom():
    policy = ValidationPolicy(chi2_warning=5.0, chi2_critical=100.0, rho_warning=0.90)
    assert policy.chi2_warning == 5.0
    assert policy.chi2_critical == 100.0
    assert policy.rho_warning == 0.90

def test_evaluate_chi2():
    policy = ValidationPolicy()
    
    # Normal
    res = policy.evaluate_chi2(5.0)
    assert res is None
    
    # Warning
    res = policy.evaluate_chi2(15.0)
    assert res is not None
    assert res["severity"] == "warning"
    assert res["type"] == "chi2"
    
    # Critical
    res = policy.evaluate_chi2(250.0)
    assert res is not None
    assert res["severity"] == "critical"
    assert res["type"] == "chi2"

def test_evaluate_correlation():
    policy = ValidationPolicy()
    
    # Normal
    res = policy.evaluate_correlation("q", "T", 0.5)
    assert res is None
    
    # Warning (positive correlation)
    res = policy.evaluate_correlation("q", "T", 0.96)
    assert res is not None
    assert res["severity"] == "warning"
    assert res["type"] == "correlation"
    
    # Warning (negative correlation)
    res = policy.evaluate_correlation("q", "T", -0.96)
    assert res is not None
    assert res["severity"] == "warning"
    assert res["type"] == "correlation"
