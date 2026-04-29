import math
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

from fitting_pipeline import (
    safe_exp,
    manuscript_component_scalar,
    fit_one_spec,
    run_fits,
    FitSpec
)

def test_safe_exp():
    assert safe_exp(800.0) == math.exp(700.0)
    assert safe_exp(-800.0) == math.exp(-700.0)
    assert safe_exp(1.0) == math.exp(1.0)

def test_manuscript_component_scalar():
    val = manuscript_component_scalar(
        pt=1.0, norm=1.0, temperature=0.15, U=0.3, eta_max=2.5, mass_gev=0.13957
    )
    assert isinstance(val, float)
    assert val > 0

@patch("fitting_pipeline.Minuit")
def test_fit_quality_flag_poor(mock_minuit_class):
    mock_minuit = MagicMock()
    mock_minuit.valid = True
    mock_minuit.fval = 100.0  # chi2 = 100
    mock_minuit.values = {"test_param": 1.0}
    mock_minuit.errors = {"test_param": 0.1}
    mock_minuit.covariance = None
    mock_minuit.fmin = MagicMock(edm=0.01, has_accurate_covar=False)
    
    mock_minuit_class.return_value = mock_minuit
    
    spec = FitSpec(
        model_name="test_model",
        component_count=1,
        parameter_names=["test_param"],
        parameter_bounds={"test_param": (0.0, 2.0)},
        fixed_metadata={},
        model_callable=lambda x, p: x,
        initial_grid_builder=lambda x, y: [(1.0,)]
    )
    
    # 11 points, 1 parameter -> ndf = 10. chi2/ndf = 10 > 5
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0])
    y = np.ones(11)
    err = np.ones(11)
    
    result = fit_one_spec(spec, x, y, err)
    assert result["fit_quality_flag"] == "poor"

@patch("fitting_pipeline.fit_one_spec")
def test_eta_range_parser(mock_fit_one_spec, tmp_path):
    mock_fit_one_spec.return_value = {
        "success": True, 
        "fit_quality_flag": "ok",
        "parameter_values": {"norm": 1.0},
        "parameter_errors": {"norm": 0.1},
        "chi2": 1.0,
        "ndf": 1,
        "chi2_ndf": 1.0,
        "aic": 1.0,
        "bic": 1.0,
        "model_predictions": [10.0, 5.0],
        "residuals": [0.0, 0.0],
        "pulls": [0.0, 0.0]
    }
    
    df1 = pd.DataFrame({
        "pt_center_gev": [1.0, 2.0],
        "yield_value": [10.0, 5.0],
        "total_error": [1.0, 0.5],
        "eta_range": ["-2.5-2.5", "-2.5-2.5"]
    })
    
    # Should not raise any parsing error
    run_fits(tmp_path, df1, mass_gev=0.13957)
    
    df2 = pd.DataFrame({
        "pt_center_gev": [1.0, 2.0],
        "yield_value": [10.0, 5.0],
        "total_error": [1.0, 0.5],
        "eta_range": ["0-2.5", "0-2.5"]
    })
    
    # Should not raise any parsing error
    run_fits(tmp_path, df2, mass_gev=0.13957)
