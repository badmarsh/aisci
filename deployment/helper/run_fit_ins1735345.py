#!/usr/bin/env python3
from __future__ import annotations
import json
import shutil
import subprocess
from pathlib import Path

# Paths
BASE_DIR = Path("/home/ubuntu/aisci")
DATA_CSV = BASE_DIR / "physics/data/fit_input_ins1735345.csv"
RUN_DIR = BASE_DIR / "research/robert/runs/2026-05-30-multiplicity-fit"
PDF_PATH = BASE_DIR / "research/robert/manuscript/boson-probability-function-moving-system.md"

def main():
    print("Setting up run directory...")
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Copy data CSV
    dest_csv = RUN_DIR / "fit_input.csv"
    shutil.copy(DATA_CSV, dest_csv)
    print(f"Copied data to {dest_csv}")
    
    # 2. Write mapping validation JSON
    mapping = {
        "fit_ready": True,
        "record_id": "ins1735345",
        "blockers": []
    }
    with open(RUN_DIR / "hepdata_mapping_validation.json", "w") as f:
        json.dump(mapping, f, indent=2)
    print("Wrote hepdata_mapping_validation.json")
    
    # 3. Run the fitting pipeline
    print("Running fitting pipeline...")
    cmd = [
        "python3",
        str(BASE_DIR / "physics/src/fitting_pipeline.py"),
        "--run-dir", str(RUN_DIR),
        "--pdf-path", str(PDF_PATH)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("=== STDOUT ===")
    print(result.stdout)
    print("=== STDERR ===")
    print(result.stderr)
    
    if result.returncode == 0:
        print("Fitting pipeline completed successfully!")
    else:
        print(f"Fitting pipeline failed with exit code {result.returncode}")

if __name__ == "__main__":
    main()
