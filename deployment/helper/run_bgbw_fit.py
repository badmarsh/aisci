#!/usr/bin/env python3
"""
Blast-Wave Baseline Fit Run for ins1735345 data.

Runs fits for blast_wave, tsallis, and manuscript_juttner models
(1c, 2c, 3c) to complete the model comparison triangle across all 10 multiplicity bins.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Ensure the aisci package path is available
BASE_DIR = Path("/home/ubuntu/aisci")
sys.path.insert(0, str(BASE_DIR))

from physics.src.fitting_pipeline import (
    manuscript_fit_spec,
    tsallis_fit_spec,
    blast_wave_fit_spec,
    fit_one_spec,
    plot_fit_diagnostics,
    infer_group_columns,
    write_json,
)

def assert_fit_gate(result, spec, group_label):
    chi2_ndf = result.get('chi2_ndf', 1000)
    valid = result.get('success', False)
    passed = valid and (0.1 <= chi2_ndf <= 5.0)
    return {"gate_passed": passed, "gate_failures": [] if passed else ["failed"]}

def generate_fit_dashboard(quality_df, gate_verdicts, RUN_DIR):
    passed = sum(1 for v in gate_verdicts if v["gate_passed"])
    return {"summary": {"gate_passed": passed, "gate_failed": len(gate_verdicts) - passed, "pass_rate_pct": round(passed/max(1, len(gate_verdicts))*100, 1)}}

try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

# ────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────
DATA_CSV = BASE_DIR / "physics/data/fit_input_ins1735345.csv"
RUN_DIR  = BASE_DIR / "research/robert/runs/2026-05-31-o03-tsallis-bgbw-fit"

# Manuscript acceptance and mass
ETA_MAX  = 0.8    # |η| < 0.8 (ALICE, this record)
MASS_GEV = 0.13957  # pion mass

# Manuscript pT gate: 120 MeV ≤ pT ≤ 5000 MeV (Figs 7-9)
PT_LOW_GEV  = 0.120
PT_HIGH_GEV = 5.0

COMPONENT_COUNTS = [1, 2, 3]
MODELS = ["blast_wave", "tsallis", "manuscript_juttner"]

def build_bgbw_specs(eta_max: float, mass_gev: float):
    """Build the specs for the model comparison triangle."""
    specs = []
    for nc in COMPONENT_COUNTS:
        specs.append(blast_wave_fit_spec(nc, mass_gev))
        specs.append(tsallis_fit_spec(nc, eta_max, mass_gev))
        specs.append(manuscript_fit_spec(nc, eta_max, mass_gev))
    return specs

def main() -> int:
    print("=== Blast-Wave Baseline Fit Run ===")
    print(f"Data:    {DATA_CSV}")
    print(f"Run dir: {RUN_DIR}")
    print(f"pT gate: {PT_LOW_GEV}–{PT_HIGH_GEV} GeV  |  η_max = {ETA_MAX}")

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "covariance").mkdir(exist_ok=True)
    (RUN_DIR / "diagnostics").mkdir(exist_ok=True)

    # Load data and apply pT gate
    df = pd.read_csv(DATA_CSV)
    orig_rows = len(df)
    df = df[
        (df["pt_center_gev"] >= PT_LOW_GEV) &
        (df["pt_center_gev"] <= PT_HIGH_GEV)
    ].copy()
    print(f"Loaded {orig_rows} rows → {len(df)} after pT gate")

    # Drop rows with missing errors
    df = df.dropna(subset=["total_error", "pt_center_gev", "yield_value"])
    df = df[df["total_error"] > 0]
    print(f"After dropping bad rows: {len(df)} rows")
    print(f"Bins: {sorted(df['manuscript_bin'].unique())}")

    df.to_csv(RUN_DIR / "fit_input.csv", index=False)

    # Build fit specs
    specs = build_bgbw_specs(ETA_MAX, MASS_GEV)
    print(f"Fit specs: {len(specs)} ({len(COMPONENT_COUNTS)} component counts × {len(MODELS)} models)")

    group_columns = infer_group_columns(df)
    grouped = [("all_data", df)] if not group_columns else list(df.groupby(group_columns, dropna=False))

    parameter_rows = []
    quality_rows = []
    correlation_rows = []
    comparison_rows = []
    gate_verdicts = []

    for group_key, group_df in grouped:
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        group_label = "__".join(str(v) for v in group_key)
        x_values = group_df["pt_center_gev"].to_numpy(dtype=float)
        y_values = group_df["yield_value"].to_numpy(dtype=float)
        y_errors = group_df["total_error"].to_numpy(dtype=float)

        print(f"\n  Bin: {group_label}  ({len(x_values)} points)")

        best_for_group = []
        for spec in specs:
            tag = f"{spec.model_name}/{spec.component_count}c"
            result = fit_one_spec(spec, x_values, y_values, y_errors)
            gate_verdict = assert_fit_gate(result, spec, group_label)
            gate_verdicts.append(gate_verdict)

            chi2_ndf = result.get("chi2_ndf")
            ok = "✓" if gate_verdict["gate_passed"] else "✗"
            print(f"    {ok} {tag:45s}  chi2/ndf={chi2_ndf!r:>10}  success={result.get('success')}")

            quality_rows.append({
                "group_label": group_label,
                "model_name": spec.model_name,
                "component_count": spec.component_count,
                "success": result.get("success", False),
                "chi2": result.get("chi2"),
                "ndf": result.get("ndf"),
                "chi2_ndf": result.get("chi2_ndf"),
                "fit_quality_flag": result.get("fit_quality_flag", "ok"),
                "gate_passed": gate_verdict["gate_passed"],
                "gate_failures": "; ".join(gate_verdict["gate_failures"]),
                "aic": result.get("aic"),
                "bic": result.get("bic"),
                "edm": result.get("edm"),
                "has_accurate_covar": result.get("has_accurate_covar"),
                "seed_index": result.get("seed_index"),
            })

            for pname, pvalue in (result.get("parameter_values") or {}).items():
                parameter_rows.append({
                    "group_label": group_label,
                    "model_name": spec.model_name,
                    "component_count": spec.component_count,
                    "parameter_name": pname,
                    "value": pvalue,
                    "error": (result.get("parameter_errors") or {}).get(pname),
                })

            corr = result.get("correlation_matrix")
            if corr is not None:
                corr_arr = np.asarray(corr, dtype=float)
                cov_arr = np.asarray(result["covariance_matrix"], dtype=float)
                cov_df = pd.DataFrame(cov_arr, index=spec.parameter_names, columns=spec.parameter_names)
                cov_df.to_csv(RUN_DIR / "covariance" / f"{group_label}__{spec.model_name}__{spec.component_count}c.csv")
                for ri, ln in enumerate(spec.parameter_names):
                    for ci, rn in enumerate(spec.parameter_names):
                        correlation_rows.append({
                            "group_label": group_label,
                            "model_name": spec.model_name,
                            "component_count": spec.component_count,
                            "parameter_left": ln,
                            "parameter_right": rn,
                            "correlation": corr_arr[ri, ci],
                        })

            predictions = np.asarray(result.get("model_predictions", []), dtype=float)
            residuals = np.asarray(result.get("residuals", []), dtype=float)
            pulls = np.asarray(result.get("pulls", []), dtype=float)
            resid_df = pd.DataFrame({
                "pt_center_gev": x_values,
                "yield_value": y_values,
                "total_error": y_errors,
                "prediction": predictions,
                "residual": residuals,
                "pull": pulls,
            })
            resid_df.to_csv(
                RUN_DIR / "diagnostics" / f"{group_label}__{spec.model_name}__{spec.component_count}c_residuals.csv",
                index=False,
            )
            if HAS_MPL and result.get("success") and len(predictions) > 0:
                plot_fit_diagnostics(
                    RUN_DIR / "diagnostics" / f"{group_label}__{spec.model_name}__{spec.component_count}c.png",
                    x_values, y_values, y_errors, predictions, residuals, pulls,
                    title=f"{group_label} | {spec.model_name} | {spec.component_count}c",
                )

            best_for_group.append({
                "group_label": group_label,
                "model_name": spec.model_name,
                "component_count": spec.component_count,
                "success": result.get("success", False),
                "chi2_ndf": result.get("chi2_ndf"),
                "aic": result.get("aic"),
                "bic": result.get("bic"),
            })

        successful = [r for r in best_for_group if r["success"]]
        successful.sort(key=lambda r: (r["aic"] if r["aic"] is not None else 1e18))
        for rank, row in enumerate(successful, 1):
            comparison_rows.append({"rank_in_group": rank, **row})

    # Write outputs
    pd.DataFrame(parameter_rows).to_csv(RUN_DIR / "fit_parameters.csv", index=False)
    pd.DataFrame(quality_rows).to_csv(RUN_DIR / "fit_quality.csv", index=False)
    pd.DataFrame(correlation_rows).to_csv(RUN_DIR / "parameter_correlations.csv", index=False)
    pd.DataFrame(comparison_rows).to_csv(RUN_DIR / "model_comparison.csv", index=False)

    quality_df = pd.DataFrame(quality_rows)
    dashboard = generate_fit_dashboard(quality_df, gate_verdicts, RUN_DIR)
    summary = dashboard.get("summary", {})
    print(f"\n=== Gate summary ===")
    print(f"  Passed: {summary.get('gate_passed')}  Failed: {summary.get('gate_failed')}  Rate: {summary.get('pass_rate_pct')}%")

    write_json(RUN_DIR / "fit_run_status.json", {
        "fit_ready": True,
        "pipeline_status": "completed_bgbw_run",
        "pt_gate_low_gev": PT_LOW_GEV,
        "pt_gate_high_gev": PT_HIGH_GEV,
        "eta_max": ETA_MAX,
        "mass_gev": MASS_GEV,
        "models": MODELS,
        "component_counts": COMPONENT_COUNTS,
        "note": "Blast-wave baseline complete.",
        **{k: summary.get(k) for k in ("gate_passed", "gate_failed", "pass_rate_pct")},
    })
    print("Done. Results in:", RUN_DIR)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
