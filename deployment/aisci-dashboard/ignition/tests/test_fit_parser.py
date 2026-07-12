import os
import pandas as pd
from unittest import mock
import pytest
from ignition.fit_parser import parse_fit_artifacts

def test_aic_bic_calculation(tmp_path):
    # Create a dummy run directory
    run_dir = tmp_path / "test-run"
    run_dir.mkdir()
    
    # 1. Provide absolute chi2 and ndf. Expect AIC and BIC to be correctly calculated.
    # chi2 = 15.0, ndf = 44, k = 3 -> n = 47.
    # AIC = 15.0 + 2*3 = 21.0
    # BIC = 15.0 + 3*ln(47) = 15.0 + 3*3.850 = 15.0 + 11.55 = 26.55 = 26.6
    quality_df = pd.DataFrame([{
        "group_label": "0-5",
        "model_name": "tsallis",
        "chi2": 15.0,
        "chi2_ndf": 15.0 / 44.0,
        "ndf": 44,
        "success": True,
        "fit_quality_flag": "OK",
        "seed_index": 0,
        "feed_down_corrected": True
    }])
    
    params_df = pd.DataFrame([
        {"group_label": "0-5", "model_name": "tsallis", "parameter_name": "temperature_1", "value": 0.1, "error": 0.01},
        {"group_label": "0-5", "model_name": "tsallis", "parameter_name": "q_1", "value": 1.1, "error": 0.01},
        {"group_label": "0-5", "model_name": "tsallis", "parameter_name": "beta_1", "value": 0.6, "error": 0.01},
    ])
    
    quality_df.to_csv(run_dir / "fit_quality.csv", index=False)
    params_df.to_csv(run_dir / "fit_parameters.csv", index=False)
    
    res = parse_fit_artifacts(str(run_dir))
    row = res["fitRows"][0]
    
    assert row["chi2"] == 15.0
    assert row["aic"] == 21.0
    assert row["bic"] == 26.6
    assert row["feed_down_corrected"] is True

def test_missing_chi2_no_aic(tmp_path):
    run_dir = tmp_path / "test-run2"
    run_dir.mkdir()
    
    # Missing absolute chi2
    quality_df = pd.DataFrame([{
        "group_label": "0-5",
        "model_name": "tsallis",
        "chi2_ndf": 1.5,
        "success": True,
        "fit_quality_flag": "OK",
        "seed_index": 0
    }])
    quality_df.to_csv(run_dir / "fit_quality.csv", index=False)
    
    res = parse_fit_artifacts(str(run_dir))
    row = res["fitRows"][0]
    
    assert row["chi2"] is None
    assert row["aic"] is None
    assert row["bic"] is None
    assert row["feed_down_corrected"] is None
