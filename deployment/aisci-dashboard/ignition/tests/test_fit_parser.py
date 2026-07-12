import pytest
from fit_parser import parse_fit_artifacts, parse_correlations

def test_parse_fit_results(tmp_path):
    csv_file = tmp_path / "fit_results.csv"
    csv_file.write_text("valid,AIC,BIC,chi2,ndf\nTrue,100,105,15.5,10\nFalse,0,0,0,0\n")
    
    # Should get the first valid row and skip the header
    valid, aic, bic, chi2, ndf = parse_fit_artifacts(str(csv_file))
    assert valid is True
    assert aic == 100.0
    assert bic == 105.0
    assert chi2 == 15.5
    assert ndf == 10.0

def test_parse_fit_results_invalid(tmp_path):
    csv_file = tmp_path / "fit_results.csv"
    csv_file.write_text("valid,AIC,BIC,chi2,ndf\nFalse,0,0,0,0\n")
    
    valid, aic, bic, chi2, ndf = parse_fit_artifacts(str(csv_file))
    assert valid is False

def test_parse_correlations(tmp_path):
    csv_file = tmp_path / "correlations.csv"
    # model,param1,param2,value
    csv_file.write_text("bin,model,p1,p2,0.98\nbin,model,p1,p3,0.5\n")
    
    correlations = parse_correlations(str(csv_file))
    assert len(correlations) == 2
    assert correlations[0] == {"param1": "p1", "param2": "p2", "value": 0.98}
    assert correlations[1] == {"param1": "p1", "param2": "p3", "value": 0.5}
