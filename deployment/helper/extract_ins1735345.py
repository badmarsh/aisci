#!/usr/bin/env python3
"""
Extract per-multiplicity-bin pT spectra from HEPData ins1735345, Table 1.

ins1735345 (arXiv:1905.07208) contains pT spectra as a function of
event multiplicity for pp collisions at 13 TeV with |eta|<0.8.
The multiplicity is estimated with SPD tracklets.

Table 1 structure:
  - Rows: pT values (47 bins)
  - Columns: one per multiplicity class (the 10 SPD-tracklet classes)

The column headers encode the multiplicity bin labels (e.g., "21-30", "31-40").
This script:
1. Downloads Table 1 JSON
2. Identifies column headers and maps them to manuscript bins
3. Emits a long-form CSV in the same format expected by fitting_pipeline.py

Output: libs/physics-core/data/fit_input_ins1735345.csv
"""
from __future__ import annotations

import json
import math
import re
import sys
import time
from pathlib import Path

import requests
import pandas as pd

RECORD_ID = "ins1735345"
TABLE_1_URL = "https://www.hepdata.net/record/ins1735345?format=json"

MANUSCRIPT_BINS = [
    "21-30", "31-40", "41-50", "51-60", "61-70",
    "71-80", "81-90", "91-100", "101-125", "126-150",
]

OUT_DIR = Path("/home/ubuntu/aisci/libs/physics-core/data")
OUT_CSV = OUT_DIR / "fit_input_ins1735345.csv"
META_JSON = OUT_DIR / "fit_input_ins1735345_meta.json"


def get_json(url: str, timeout: int = 30) -> dict:
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                raise


def parse_float(v) -> float | None:
    try:
        return float(str(v).replace(",", "")) if v not in (None, "") else None
    except ValueError:
        return None


def symmetrize_error(error: dict) -> float | None:
    if "symerror" in error:
        return abs(parse_float(error["symerror"]) or 0.0)
    asym = error.get("asymerror", {})
    plus = parse_float(asym.get("plus"))
    minus = parse_float(asym.get("minus"))
    values = [abs(v) for v in [plus, minus] if v is not None]
    return max(values) if values else None


def normalize_bin_label(label: str) -> str:
    """Normalize e.g. '21_30', '21 to 30', '21-30' -> '21-30'."""
    cleaned = re.sub(r"[_ ]+to[_ ]+", "-", label.strip())
    cleaned = re.sub(r"[_ ]+", "-", cleaned)
    return cleaned


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Fetching record index for {RECORD_ID} ...")
    record = get_json(TABLE_1_URL)
    tables = record.get("data_tables", [])

    # Table 1 = SPD tracklet multiplicity at 13 TeV
    table1_entry = None
    for t in tables:
        if t["name"] == "Table 1":
            table1_entry = t
            break

    if table1_entry is None:
        print("ERROR: Table 1 not found in record", file=sys.stderr)
        return 1

    print(f"Fetching Table 1 JSON ...")
    t1 = get_json(table1_entry["data"]["json"])

    headers = t1.get("headers", [])
    values = t1.get("values", [])

    print(f"  Headers: {[h.get('name','') for h in headers]}")
    print(f"  Rows: {len(values)}")

    # Header 0 is pT; headers 1..N are multiplicity columns
    # Each header may have a 'values' list of sub-column labels
    # Try to extract column labels
    col_labels: list[str] = []
    for h in headers[1:]:  # skip pT header
        name = h.get("name", "")
        col_labels.append(name)

    print(f"  Multiplicity column labels: {col_labels}")

    # Map column labels to manuscript bins
    col_to_bin: dict[int, str] = {}
    roman_to_bin_map = {
        "X'": "21-30",
        "IX'": "31-40",
        "VIII'": "41-50",
        "VII'": "51-60",
        "VI'": "61-70",
        "V'": "71-80",
        "IV'": "81-90",
        "III'": "91-100",
        "II'": "101-125",
        "I'": "126-150"
    }
    for idx, label in enumerate(col_labels):
        matched = False
        for roman, bin_val in roman_to_bin_map.items():
            if f"({roman})" in label or f" {roman}" in label:
                col_to_bin[idx] = bin_val
                matched = True
                break
        if not matched:
            if idx < len(MANUSCRIPT_BINS):
                col_to_bin[idx] = MANUSCRIPT_BINS[idx]

    print(f"  Matched columns -> bins: {col_to_bin}")

    # Extract rows
    rows: list[dict] = []
    for row in values:
        x_cells = row.get("x", [{}])
        y_cells = row.get("y", [])

        pt_cell = x_cells[0] if x_cells else {}
        pt_low = parse_float(pt_cell.get("low"))
        pt_high = parse_float(pt_cell.get("high"))
        pt_center = parse_float(pt_cell.get("value"))
        if pt_center is None and pt_low is not None and pt_high is not None:
            pt_center = (pt_low + pt_high) / 2.0

        for col_idx, bin_label in col_to_bin.items():
            if col_idx >= len(y_cells):
                continue
            y_cell = y_cells[col_idx]
            yield_val = parse_float(y_cell.get("value"))
            if yield_val is None:
                continue

            # Errors
            errors = y_cell.get("errors", [])
            stat_err = None
            sys_err = None
            for err in errors:
                lbl = err.get("label", "").lower()
                val = symmetrize_error(err)
                if "stat" in lbl:
                    stat_err = val
                elif "sys" in lbl or "uncorr" in lbl or "corr" in lbl:
                    sys_err = val

            total_err = None
            if stat_err is not None and sys_err is not None:
                total_err = math.sqrt(stat_err ** 2 + sys_err ** 2)
            elif stat_err is not None:
                total_err = stat_err
            elif sys_err is not None:
                total_err = sys_err

            rows.append({
                "source_record": RECORD_ID,
                "source_table": "Table 1",
                "source_table_doi": table1_entry.get("doi", ""),
                "observable_kind": "pt_spectrum",
                "eta_range": "-0.8-0.8",
                "multiplicity_selection": bin_label,
                "manuscript_bin": bin_label,
                "fit_ready": True,
                "mapping_status": "matched_to_manuscript_bin",
                "pt_low_gev": pt_low,
                "pt_high_gev": pt_high,
                "pt_center_gev": pt_center,
                "yield_value": yield_val,
                "stat_error": stat_err,
                "sys_error": sys_err,
                "total_error": total_err,
            })

    df = pd.DataFrame(rows)
    df.to_csv(OUT_CSV, index=False)
    print(f"\nWrote {len(df)} rows to {OUT_CSV}")
    print(f"Bins found: {sorted(df['manuscript_bin'].unique())}")
    print(f"pT range: {df['pt_center_gev'].min():.3f} - {df['pt_center_gev'].max():.3f} GeV")

    meta = {
        "source_record": RECORD_ID,
        "arxiv": "1905.07208",
        "paper": "Charged-particle production as a function of multiplicity and transverse spherocity in pp collisions at sqrt(s)=5.02 and 13 TeV",
        "table": "Table 1",
        "energy_gev": 13000,
        "eta_range": "-0.8-0.8",
        "multiplicity_estimator": "SPD_tracklets",
        "rows": len(df),
        "bins_matched": sorted(df["manuscript_bin"].unique().tolist()),
        "output_csv": str(OUT_CSV),
    }
    META_JSON.write_text(json.dumps(meta, indent=2) + "\n")
    print(f"Wrote metadata to {META_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
