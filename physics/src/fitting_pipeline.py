#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
from typing import Any

from models import *
from fitting import *

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--pdf-path", type=Path, required=True)
    parser.add_argument("--mass-gev", type=float, default=DEFAULT_MASS_GEV)
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    return run_all_fits(args.run_dir, args.pdf_path, args.mass_gev)

if __name__ == "__main__":
    raise SystemExit(main())
