import os
import pytest
from validation_policy import ValidationPolicy, default_policy
from pipelines import registry as pipeline_registry
from project_registry import registry as project_registry

def test_dynamic_chi2_threshold():
    policy = ValidationPolicy()
    
    # 1. Static fallback (no NDF)
    sev_static, msg_static = policy.validate_chi2(15.0)
    assert sev_static == "warning", "Expected warning for chi2=15.0"
    
    # 2. Static critical fallback (no NDF)
    sev_crit, msg_crit = policy.validate_chi2(25.0)
    assert sev_crit == "critical", "Expected critical for chi2=25.0"

    # 3. Dynamic NDF-based calibration (ndf=44)
    # Using scipy.stats.chi2, for ndf=44:
    # 95th percentile (warning threshold) is around 60.48 / 44 = 1.37
    # 99th percentile (critical threshold) is around 68.71 / 44 = 1.56
    # Let's test with chi2_ndf = 1.8 (should be critical)
    sev, msg = policy.validate_chi2(1.8, ndf=44)
    assert sev == "critical"
    assert "calibrated threshold" in msg

    # Let's test with chi2_ndf = 1.4 (should be warning)
    sev_warn, msg_warn = policy.validate_chi2(1.4, ndf=44)
    assert sev_warn == "warning"
    assert "calibrated threshold" in msg_warn

    # Let's test with chi2_ndf = 1.0 (should be ok)
    sev_ok, msg_ok = policy.validate_chi2(1.0, ndf=44)
    assert sev_ok == "ok"

def test_t_q_degeneracy():
    policy = ValidationPolicy()
    
    # 1. Tsallis model with strong correlation -> warning
    sev, msg = policy.validate_t_q_degeneracy(-0.91, "tsallis_1c", "temperature_1", "q_1")
    assert sev == "warning"
    assert "T-q Degeneracy" in msg
    
    # 2. Tsallis model with low correlation -> ok
    sev_ok, _ = policy.validate_t_q_degeneracy(0.40, "tsallis_1c", "temperature_1", "q_1")
    assert sev_ok == "ok"
    
    # 3. Non-Tsallis model with strong correlation -> ok (handled by standard correlation checks, not t-q specifically)
    sev_non_tsallis, _ = policy.validate_t_q_degeneracy(-0.91, "juttner_1c", "temperature_1", "U_1")
    assert sev_non_tsallis == "ok"

def test_sensitivity_scan_pipeline_registration():
    project_id = "robert-boson-manuscript"
    spec = project_registry.get_project(project_id)
    
    pipelines = pipeline_registry.get_pipelines_for_project(spec)
    pipeline_ids = [p.id for p in pipelines]
    
    assert "sensitivity-scan" in pipeline_ids
    
    scan_spec = pipeline_registry.get_pipeline(spec, "sensitivity-scan")
    assert "exact_be_fit_range_scan.py" in scan_spec.command[-1]
    
    # Verify working directory is repository root
    assert scan_spec.working_dir.endswith("aisci")
    
    dry_res = scan_spec.dry_run()
    assert dry_res["status"] == "available"
