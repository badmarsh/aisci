import os
import json
import pandas as pd
from pathlib import Path
import sys
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from physics.src.fitting_pipeline import run_fits
import physics.src.fitting_pipeline as fp

# Monkeypatch build_fit_specs to only return the models we need for Table 1
# This avoids a Bus Error when scipy tries to integrate divergent 3-component BGBW models.
original_build = fp.build_fit_specs

def patched_build(*args, **kwargs):
    specs = original_build(*args, **kwargs)
    wanted = {
        ("manuscript_juttner", 1)
    }
    return [s for s in specs if (s.model_name, s.component_count) in wanted]

fp.build_fit_specs = patched_build

def main():
    run_dir = Path("research/robert/runs/2026-07-09-jacobian-fix")
    run_dir.mkdir(parents=True, exist_ok=True)
    
    data_path = "physics/data/fit_input.csv"
    df = pd.read_csv(data_path)
    
    print("Running selected fits with updated Jacobian...")
    results = run_fits(
        run_dir=run_dir,
        fit_input=df,
        mass_gev=0.13957,
    )
    
    output_file = run_dir / "fit_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
        
    # Check for parameter degeneracies (rho > 0.9)
    corr_file = run_dir / "parameter_correlations.csv"
    if corr_file.exists():
        corr_df = pd.read_csv(corr_file)
        degeneracies = corr_df[abs(corr_df['correlation']) > 0.9]
        if not degeneracies.empty:
            print(f"WARNING: {len(degeneracies)} parameter correlations > 0.9 found. See evidence ledger.")
            # Log to DB Activity
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'ignition'))
            from api import log_activity
            log_activity("Full Covariance Scan", "AI", f"Flagged {len(degeneracies)} bin/model combinations with rho > 0.9")
        
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()
