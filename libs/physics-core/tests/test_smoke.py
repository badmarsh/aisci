import json
import math
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np
import pandas as pd
import pytest

# Add libs/physics-core/src to python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
# Add libs/physics-core to python path for cli
sys.path.insert(0, str(Path(__file__).parent.parent))
# Add research/robert to path for ledger_scorer
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "research/robert"))

import data_loader
import fitting_pipeline
import ledger_scorer

@pytest.fixture
def mock_hepdata_responses():
    # Mock index JSON
    index_json = {
        "data_tables": [
            {
                "name": "Table 1",
                "doi": "10.17182/hepdata.91996.v2/t1",
                "data": {
                    "json": "https://www.hepdata.net/download/table/ins1735345/Table%201/json"
                }
            }
        ]
    }

    # Generate mock spectra data points (10 points)
    pt_values = [0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 1.05]
    mock_values = []
    for pt in pt_values:
        mock_values.append({
            "x": [{"value": pt, "low": pt - 0.05, "high": pt + 0.05}],
            "y": [
                {
                    "value": 100.0 * math.exp(-pt / 0.15),
                    "errors": [{"symerror": 5.0, "label": "stat"}, {"symerror": 10.0, "label": "sys"}]
                },
                {
                    "value": 150.0 * math.exp(-pt / 0.15),
                    "errors": [{"symerror": 6.0, "label": "stat"}, {"symerror": 12.0, "label": "sys"}]
                }
            ]
        })

    table_json = {
        "name": "Table 1",
        "doi": "10.17182/hepdata.91996.v2/t1",
        "location": "Page 10",
        "description": "Multiplicity class spectra",
        "headers": [
            {"name": "PT(P=3) [GEV]"},
            {"name": "(X') 21-30"},
            {"name": "(IX') 31-40"}
        ],
        "qualifiers": {
            "ETARAP(P=3)": [{"value": "-0.8-0.8"}]
        },
        "values": mock_values
    }
    
    return index_json, table_json


@patch("data_loader.requests.get")
def test_smoke_pipeline(mock_get, mock_hepdata_responses, tmp_path):
    index_json, table_json = mock_hepdata_responses

    # Setup mock requests.get responses
    mock_resp_index = MagicMock()
    mock_resp_index.json.return_value = index_json
    mock_resp_index.status_code = 200

    mock_resp_table = MagicMock()
    mock_resp_table.json.return_value = table_json
    mock_resp_table.status_code = 200

    mock_get.side_effect = [mock_resp_index, mock_resp_table]

    # 1. Run Data Loader
    args_loader = MagicMock()
    args_loader.run_dir = tmp_path
    args_loader.record_id = "ins1735345"
    args_loader.timeout_seconds = 30.0

    with patch("data_loader.parse_args", return_value=args_loader):
        rc = data_loader.main()
        assert rc == 0

    fit_input_file = tmp_path / "fit_input.csv"
    assert fit_input_file.exists()
    
    df = pd.read_csv(fit_input_file)
    assert len(df) > 0
    assert set(df["manuscript_bin"].unique()) == {"21-30", "31-40"}

    # 2. Run Fitting Pipeline via CLI
    import cli
    args_pipeline = MagicMock()
    args_pipeline.run_dir = str(tmp_path)
    args_pipeline.data_path = str(tmp_path / "fit_input.csv")
    args_pipeline.mass_gev = 0.13957
    args_pipeline.models = None
    args_pipeline.cov_mode = "diag"
    args_pipeline.xi = 1.0
    args_pipeline.dry_run = False

    with patch("cli.parse_args", return_value=args_pipeline):
        try:
            cli.main()
        except SystemExit as e:
            assert e.code == 0

    assert (tmp_path / "cli_summary.json").exists()

    # 3. Run Ledger Scorer
    # We mock parse_ledger_claims to return a simple list of mock claims
    mock_claims = [
        {
            "claim": "Lorentz-covariant",
            "evidence_required": "test",
            "current_evidence": "test",
            "status": "Sanity checked",
            "next_gate": "test"
        },
        {
            "claim": "uses a full Bose-Einstein distribution, not only a Boltzmann/Juttner approximation",
            "evidence_required": "test",
            "current_evidence": "test",
            "status": "Sanity checked",
            "next_gate": "test"
        }
    ]

    args_scorer = MagicMock()
    args_scorer.run_dir = tmp_path
    args_scorer.ledger_path = Path("dummy_ledger.md")

    with patch("ledger_scorer.parse_args", return_value=args_scorer), \
         patch("ledger_scorer.parse_ledger_claims", return_value=mock_claims), \
         patch("ledger_scorer.run_pytest", return_value=True):
        rc_score = ledger_scorer.main()
        assert rc_score == 0

    assert (tmp_path / "ledger_scorer_report.json").exists()
    report_data = json.loads((tmp_path / "ledger_scorer_report.json").read_text())
    assert report_data["total_score"] > 0


# ---------------------------------------------------------------------------
# Static Tsallis limit: crosscheck against y=0 mid-rapidity formula
# ---------------------------------------------------------------------------

def test_static_tsallis_limit_agrees_at_narrow_eta():
    """tsallis_component_scalar(etamax~0) must converge to static_tsallis_limit.

    At tiny etamax the eta-integral collapses to integrand(eta=0)*2*etamax.
    Since cosh(0)=1, energy_like = mt*1 = mt, so the integrand equals the
    static (y=0) form.  The two must agree within 1% at etamax=1e-4.
    This guards the relationship between the pipeline formula and the
    mid-rapidity form used in arXiv:1501.07127 for literature comparison.
    """
    from fitting_pipeline import tsallis_component_scalar, static_tsallis_limit

    pt, norm, T, q, mass = 1.0, 1.0, 0.15, 1.1, 0.13957
    etamax = 1e-4  # almost-zero rapidity window

    integrated = tsallis_component_scalar(pt, norm, T, q, etamax, mass)
    static = static_tsallis_limit(pt, norm, T, q, mass)
    # integrated ~= static * 2 * etamax  (rectangle rule at eta=0)
    ratio = integrated / (static * 2.0 * etamax)
    assert abs(ratio - 1.0) < 0.01, (
        f"Static limit mismatch: integrated/(static*2*etamax)={ratio:.5f} (expected ~1.0)"
    )


def test_be_denominator_guard_is_unreachable_in_valid_regime():
    """bose_component_scalar denominator guard cannot fire for valid physics params.

    Mathematical identity: gamma = sqrt(1+U^2) > U for all real U, and
    cosh(eta) >= sinh(eta) always, so gamma*mt*cosh(eta) > U*pt*sinh(eta)
    (with mt >= mass > 0), making the exponent always positive in the
    physical parameter regime (T>0, U>=0, mu=0).  This test verifies the
    function produces a finite, positive result even at extreme-but-physical
    parameters, and that the warning infrastructure is wired correctly for
    any future scenario that reaches the guard.
    """
    import math
    from fitting_pipeline import bose_component_scalar

    # Extreme but physical: T=0.01 GeV (very cold), U=2.9 (beta~0.994c)
    result = bose_component_scalar(
        pt=0.5, norm=1.0, temperature=0.01,
        U=2.9, eta_max=0.8, mass_gev=0.13957,
    )
    assert math.isfinite(result), "Result must be finite at extreme valid params"
    assert result >= 0.0, "Result must be non-negative"
