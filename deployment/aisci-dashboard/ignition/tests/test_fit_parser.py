import pytest
import os
from fit_parser import parse_fit_artifacts, parse_model_name

def test_parse_model_name():
    assert parse_model_name("tsallis_2c") == "Tsallis-Pareto 2c"
    assert parse_model_name("juttner_1c") == "Jüttner/Boltzmann 1c"
    assert parse_model_name("unknown_model") == "Unknown_Model 1c"

def test_parse_fit_artifacts(tmp_path):
    run_dir = tmp_path / "run_2026-07-12"
    run_dir.mkdir()
    
    quality_file = run_dir / "fit_quality.csv"
    quality_file.write_text("group_label,model_name,chi2_ndf,success,fit_quality_flag,aic,bic,seed_index\n0-5,tsallis_1c,1.5,True,GOOD,100,105,1\n")
    
    params_file = run_dir / "fit_parameters.csv"
    params_file.write_text("group_label,model_name,parameter_name,value,error\n0-5,tsallis_1c,T_stat,120.0,5.0\n0-5,tsallis_1c,beta_s,0.6,0.01\n")
    
    corr_file = run_dir / "parameter_correlations.csv"
    corr_file.write_text("group_label,model_name,parameter_left,parameter_right,correlation\n0-5,tsallis_1c,T_stat,beta_s,0.85\n")
    
    result = parse_fit_artifacts(str(run_dir))
    
    assert len(result["fitRows"]) == 1
    row = result["fitRows"][0]
    
    assert row["bin"] == "0-5"
    assert row["model"] == "Tsallis-Pareto 1c"
    assert row["chi2"] == 1.5
    assert row["status"] == "Clean Fit"
    assert row["T"] == "120.000 ± 5.000"
    assert row["beta"] == "0.600 ± 0.010"
    assert row["correlations"]["T_stat|beta_s"] == 0.85

def test_parse_fit_artifacts_missing_files(tmp_path):
    run_dir = tmp_path / "run_2026-07-12"
    run_dir.mkdir()
    
    with pytest.raises(FileNotFoundError):
        parse_fit_artifacts(str(run_dir))
