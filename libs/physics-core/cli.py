#!/usr/bin/env python3
"""
AiSci Physics CLI
=================
Thin wrapper around physics/src/fitting_pipeline.py that makes the
pipeline invocable as a one-liner from DeerFlow, CI, or a sandbox kernel.

Usage
-----
python physics/cli.py \
    --run-dir research/robert/runs/YYYY-MM-DD-test \
    --data-path physics/data/fit_input_ins1735345.csv \
    --mass-gev 0.13957 \
    --models bgbw tsallis_1c tsallis_2c juttner_1c \
    --cov-mode diag

Outputs
-------
<run-dir>/fit_quality.csv        — chi2/ndf, AIC, BIC per bin per model
<run-dir>/parameters.csv         — best-fit parameters
<run-dir>/cli_summary.json       — machine-readable summary for agents
Stdout: JSON summary (chi2/ndf table) for easy agent parsing.
"""
import argparse
import json
import pathlib
import sys
import datetime

# Ensure physics/src is importable
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))


def parse_args():
    p = argparse.ArgumentParser(
        description="AiSci Physics CLI — run model fits and emit JSON summary."
    )
    p.add_argument(
        "--run-dir", required=True,
        help="Output directory (created if absent). "
             "E.g. research/robert/runs/YYYY-MM-DD-test"
    )
    p.add_argument(
        "--data-path",
        default="libs/physics-core/data/fit_input_ins1735345.csv",
        help="Path to per-bin pT spectrum CSV (HEPData format)."
    )
    p.add_argument(
        "--mass-gev", type=float, default=0.13957,
        help="Particle mass in GeV (default: pion 0.13957)."
    )
    p.add_argument(
        "--models", nargs="+",
        default=["bgbw", "tsallis_1c", "tsallis_2c",
                 "juttner_1c", "juttner_2c", "bose_1c", "bose_2c"],
        help="Model keys to run. Valid: bgbw tsallis_1c tsallis_2c "
             "juttner_1c juttner_2c bose_1c bose_2c"
    )
    p.add_argument(
        "--cov-mode", default="diag",
        choices=["diag", "correlated"],
        help="Covariance mode: 'diag' (independent) or 'correlated' (GLS)."
    )
    p.add_argument(
        "--xi", type=float, default=1.0,
        help="Correlation length in log-pT for GLS covariance (default 1.0)."
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Validate args and data path without running fits."
    )
    return p.parse_args()


def main():
    args = parse_args()
    run_dir = pathlib.Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    # Write run metadata immediately (survives crashes)
    meta = {
        "cli_version": "1.0.0",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "data_path": args.data_path,
        "mass_gev": args.mass_gev,
        "models": args.models,
        "cov_mode": args.cov_mode,
        "xi": args.xi,
        "run_dir": str(run_dir),
    }
    (run_dir / "cli_meta.json").write_text(json.dumps(meta, indent=2))

    if args.dry_run:
        data_path = pathlib.Path(args.data_path)
        if not data_path.exists():
            print(json.dumps({"status": "error",
                              "message": f"data-path not found: {args.data_path}"}))
            sys.exit(1)
        print(json.dumps({"status": "dry-run-ok", "meta": meta}))
        return

    # Import and run pipeline
    try:
        from fitting_pipeline import run_all_fits  # type: ignore
    except ImportError as e:
        print(json.dumps({
            "status": "error",
            "message": f"Cannot import fitting_pipeline: {e}. "
                       "Ensure iminuit, scipy, numpy, pandas are installed.",
        }))
        sys.exit(2)

    results = run_all_fits(
        data_path=args.data_path,
        run_dir=str(run_dir),
        mass_gev=args.mass_gev,
        model_keys=args.models,
        cov_mode=args.cov_mode,
        xi=args.xi,
    )

    # Emit machine-readable JSON summary to stdout for agent parsing
    summary = {
        "status": "ok",
        "run_dir": str(run_dir),
        "models_run": args.models,
        "bins": list(results.keys()) if isinstance(results, dict) else [],
        "best_model_per_bin": {
            bin_key: min(model_results, key=lambda m: model_results[m].get("chi2_ndf", 9999))
            for bin_key, model_results in results.items()
        } if isinstance(results, dict) else {},
    }
    summary_path = run_dir / "cli_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    # ── Anomaly duty check (AGENTS.md § Science Rules) ───────────────────
    ANOMALY_CHI2_THRESHOLD = 10.0
    ANOMALY_CORR_THRESHOLD = 0.90

    anomalies = []
    for bin_key, model_results in summary.get("best_model_per_bin", {}).items():
        for model_key, model_run in results.items() if isinstance(results, dict) else []:
            if isinstance(model_run, dict):
                chi2_ndf = model_run.get("chi2_ndf", 0)
                if chi2_ndf > ANOMALY_CHI2_THRESHOLD:
                    anomalies.append({
                        "type": "chi2_regression",
                        "bin": bin_key,
                        "model": model_key,
                        "chi2_ndf": chi2_ndf,
                        "threshold": ANOMALY_CHI2_THRESHOLD,
                    })
                for corr_key, corr_val in model_run.get("correlations", {}).items():
                    if abs(corr_val) > ANOMALY_CORR_THRESHOLD:
                        anomalies.append({
                            "type": "high_correlation",
                            "bin": bin_key,
                            "model": model_key,
                            "param_pair": corr_key,
                            "rho": corr_val,
                            "threshold": ANOMALY_CORR_THRESHOLD,
                        })

    if anomalies:
        anomaly_path = run_dir / "anomalies.json"
        anomaly_path.write_text(json.dumps(anomalies, indent=2))
        print(
            f"\n⚠️  ANOMALY DUTY: {len(anomalies)} anomaly/anomalies detected. "
            f"See {anomaly_path}.\n"
            f"Per AGENTS.md § Science Rules, you MUST append a proposed follow-up "
            f"item to research/robert/next-actions.md before ending this session.\n"
            f"Invoke agent-skills/science-hypothesis-generator/ to draft the entry.",
            file=sys.stderr,
        )
        summary["anomalies"] = anomalies
        summary_path.write_text(json.dumps(summary, indent=2))
    # ─────────────────────────────────────────────────────────────────────
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
