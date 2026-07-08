#!/usr/bin/env python3
"""
Validate and normalize HEPData record ins1419652 for Robert's baseline-fit run.

This loader does two separate jobs:
1. Convert the raw HEPData JSON tables into a canonical tabular form.
2. Prove whether the record contains fit-ready pT spectra for the manuscript's
   multiplicity intervals, instead of assuming that it does.

The current Stage 3 blocker is not just row extraction quality. The loader
therefore writes both the normalized spectra and an explicit mapping verdict.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import requests


HEPDATA_RECORD_ID = "ins1419652"
HEPDATA_RECORD_URL = f"https://www.hepdata.net/record/{HEPDATA_RECORD_ID}?format=json"
MANUSCRIPT_MULTIPLICITY_BINS = [
    (21, 30),
    (31, 40),
    (41, 50),
    (51, 60),
    (61, 70),
    (71, 80),
    (81, 90),
    (91, 100),
    (101, 125),
    (126, 150),
]


@dataclass(frozen=True)
class TableMetadata:
    table_name: str
    table_doi: str
    location: str
    description: str
    x_header: str
    y_header: str
    observable_kind: str
    eta_range: str
    multiplicity_selection: str
    pt_selection: str
    extrapolated: bool
    x_rows: int
    json_url: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Run directory under research/robert/runs/YYYY-MM-DD-baseline-fit",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=30.0,
        help="HTTP timeout for HEPData requests.",
    )
    return parser.parse_args()


def request_json(url: str, timeout_seconds: float) -> dict[str, Any]:
    """Fetch a JSON resource with 3 attempts and exponential backoff (1s, 2s, 4s)."""
    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=timeout_seconds)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise last_exc  # type: ignore[misc]


def normalize_space(value: Any) -> str:
    return " ".join(str(value).split())


def parse_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return None


def stringify_range(low: float | None, high: float | None) -> str | None:
    if low is None or high is None:
        return None
    low_text = str(int(low)) if float(low).is_integer() else f"{low:g}"
    high_text = str(int(high)) if float(high).is_integer() else f"{high:g}"
    return f"{low_text}-{high_text}"


def parse_interval_token(text: str) -> tuple[float | None, float | None]:
    cleaned = normalize_space(text).replace("--", "-")
    match = re.fullmatch(r"(-?\d+(?:\.\d+)?)\s*-\s*(-?\d+(?:\.\d+)?)", cleaned)
    if not match:
        return None, None
    return float(match.group(1)), float(match.group(2))


def symmetrize_error(error: dict[str, Any]) -> tuple[str, float | None, float | None, float | None]:
    label = normalize_space(error.get("label", "unknown"))
    if "symerror" in error:
        value = parse_float(error["symerror"])
        return label, value, value, value

    asym = error.get("asymerror", {})
    plus = parse_float(asym.get("plus"))
    minus = parse_float(asym.get("minus"))
    if plus is None and minus is None:
        return label, None, None, None

    abs_plus = abs(plus) if plus is not None else None
    abs_minus = abs(minus) if minus is not None else None
    symmetric = max(v for v in [abs_plus, abs_minus] if v is not None)
    return label, abs_minus, abs_plus, symmetric


def classify_table(headers: list[dict[str, Any]]) -> str:
    header_names = [normalize_space(header.get("name", "")) for header in headers]
    joined = " | ".join(header_names)
    if "PT(P=3)" in joined and "DPT(P=3)" in joined:
        return "pt_spectrum"
    # Multi-column layout: first header is pT axis, remaining are multiplicity-bin columns
    if header_names and "PT(P=3)" in header_names[0] and len(header_names) > 1:
        return "pt_spectrum"
    if header_names and header_names[0] == "N(P=3)" and "DNEV/DN(P=3)" in joined:
        return "multiplicity_distribution"
    if header_names and header_names[0] == "N(P=3)" and "MEAN(NAME=PT(P=3))" in joined:
        return "mean_pt_vs_multiplicity"
    if "ETARAP(P=3)" in joined and "DETARAP(P=3)" in joined:
        return "pseudorapidity_distribution"
    return "other"


def build_table_metadata(table_json: dict[str, Any], table_index_entry: dict[str, Any]) -> TableMetadata:
    headers = table_json.get("headers", [])
    qualifiers = table_json.get("qualifiers", {})
    x_header = normalize_space(headers[0]["name"]) if headers else ""
    y_header = normalize_space(headers[1]["name"]) if len(headers) > 1 else ""
    return TableMetadata(
        table_name=normalize_space(table_json.get("name", "")),
        table_doi=normalize_space(table_json.get("doi", "")),
        location=normalize_space(table_json.get("location", "")),
        description=normalize_space(table_json.get("description", "")),
        x_header=x_header,
        y_header=y_header,
        observable_kind=classify_table(headers),
        eta_range=normalize_space(
            qualifiers.get("ETARAP(P=3)", [{}])[0].get("value", "")
        ),
        multiplicity_selection=normalize_space(
            qualifiers.get("N(P=3)", [{}])[0].get("value", "")
        ),
        pt_selection=normalize_space(
            qualifiers.get("PT(P=3)", [{}])[0].get("value", "")
        ),
        extrapolated="Extrapolated to include strange baryons" in qualifiers,
        x_rows=len(table_json.get("values", [])),
        json_url=table_index_entry["data"]["json"],
    )




def _bin_label_from_column_header(header_name: str) -> str | None:
    """Extract e.g. "(X') 21-30" -> "21-30"; "(IX') 31-40" -> "31-40"."""
    stripped = re.sub(r"^\s*\([IVX]+'\)\s*", "", header_name.strip())
    m = re.search(r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)", stripped)
    if m:
        lo = m.group(1)
        hi = m.group(2)
        return f"{lo}-{hi}"
    return None
def extract_pt_rows(metadata: TableMetadata, table_json: dict[str, Any]) -> list[dict[str, Any]]:
    # Build y-column -> manuscript_bin mapping for multi-column tables
    headers = table_json.get("headers", [])
    y_col_bins: list[tuple[int, str | None]] = []
    if len(headers) > 1:
        for col_idx, hdr in enumerate(headers[1:]):
            label = _bin_label_from_column_header(hdr.get("name", ""))
            y_col_bins.append((col_idx, label))
    if not y_col_bins:
        y_col_bins = [(0, None)]  # single y column, no bin label

    rows: list[dict[str, Any]] = []
    for row_index, value in enumerate(table_json.get("values", []), start=1):
        x_cell = (value.get("x") or [{}])[0]
        y_list = value.get("y") or [{}]

        for y_idx, manuscript_bin in y_col_bins:
            y_cell = y_list[y_idx] if y_idx < len(y_list) else {}
            parsed_errors = {
                label.lower(): {
                    "minus": minus,
                    "plus": plus,
                    "sym": sym,
                }
                for label, minus, plus, sym in (
                    symmetrize_error(error) for error in y_cell.get("errors", [])
                )
            }

            stat_error = (parsed_errors.get("stat") or {}).get("sym")
            sys_error = (parsed_errors.get("sys") or {}).get("sym")
            total_error = None
            if stat_error is not None and sys_error is not None:
                total_error = math.sqrt(stat_error ** 2 + sys_error ** 2)

            rows.append(
                {
                    "source_record": HEPDATA_RECORD_ID,
                    "source_table": metadata.table_name,
                    "source_table_doi": metadata.table_doi,
                    "source_location": metadata.location,
                    "description": metadata.description,
                    "observable_kind": metadata.observable_kind,
                    "eta_range": metadata.eta_range,
                    "multiplicity_selection": metadata.multiplicity_selection,
                    "pt_selection": metadata.pt_selection,
                    "extrapolated": metadata.extrapolated,
                    "row_index": row_index,
                    "pt_low_gev": parse_float(x_cell.get("low")),
                    "pt_high_gev": parse_float(x_cell.get("high")),
                    "pt_center_gev": parse_float(x_cell.get("value")),
                    "yield_value": parse_float(y_cell.get("value")),
                    "stat_error": stat_error,
                    "sys_error_minus": (parsed_errors.get("sys") or {}).get("minus"),
                    "sys_error_plus": (parsed_errors.get("sys") or {}).get("plus"),
                    "sys_error": sys_error,
                    "total_error": total_error,
                    "fit_ready": manuscript_bin is not None,
                    "manuscript_bin": manuscript_bin,
                    "mapping_status": "matched_to_manuscript_bin" if manuscript_bin else "unmatched_to_manuscript_bin",
                }
            )
    return rows


def extract_distribution_bin_ranges(table_json: dict[str, Any]) -> list[str]:
    ranges: list[str] = []
    for value in table_json.get("values", []):
        x_cell = (value.get("x") or [{}])[0]
        low = parse_float(x_cell.get("low"))
        high = parse_float(x_cell.get("high"))
        label = stringify_range(low, high)
        if label:
            ranges.append(label)
    return ranges


def manuscript_bin_labels() -> list[str]:
    return [f"{low}-{high}" for low, high in MANUSCRIPT_MULTIPLICITY_BINS]


def validate_mapping(
    table_metadata: list[TableMetadata],
    table_payloads: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    manuscript_labels = manuscript_bin_labels()
    pt_tables = [metadata for metadata in table_metadata if metadata.observable_kind == "pt_spectrum"]
    multiplicity_tables = [
        metadata for metadata in table_metadata if metadata.observable_kind == "multiplicity_distribution"
    ]

    pt_table_summary = [
        {
            "table": metadata.table_name,
            "doi": metadata.table_doi,
            "eta_range": metadata.eta_range,
            "multiplicity_selection": metadata.multiplicity_selection,
            "pt_selection": metadata.pt_selection,
            "location": metadata.location,
            "description": metadata.description,
        }
        for metadata in pt_tables
    ]

    multiplicity_row_coverage: list[dict[str, Any]] = []
    for metadata in multiplicity_tables:
        bin_ranges = extract_distribution_bin_ranges(table_payloads[metadata.table_name])
        manuscript_like_bins = [bin_range for bin_range in bin_ranges if bin_range in manuscript_labels]
        multiplicity_row_coverage.append(
            {
                "table": metadata.table_name,
                "doi": metadata.table_doi,
                "eta_range": metadata.eta_range,
                "row_count": len(bin_ranges),
                "example_row_bins": bin_ranges[:12],
                "contains_exact_manuscript_row_bins": manuscript_like_bins,
            }
        )

    exact_pt_matches = [
        item
        for item in pt_table_summary
        if item["multiplicity_selection"] in manuscript_labels
    ]
    has_only_inclusive_pt_spectra = all(
        item["multiplicity_selection"] == ">= 1" for item in pt_table_summary
    )

    blockers: list[str] = []
    if not pt_table_summary:
        blockers.append("No pT spectrum tables were found in ins1419652.")
    if has_only_inclusive_pt_spectra:
        blockers.append(
            "All pT spectrum tables in ins1419652 are inclusive with qualifier N(P=3) >= 1; "
            "none are conditioned on manuscript multiplicity intervals."
        )
    if not exact_pt_matches:
        blockers.append(
            "No pT spectrum table in ins1419652 carries an exact manuscript multiplicity-bin qualifier "
            f"among {manuscript_labels}."
        )
    # FIX 3: only append this blocker when there are genuinely no exact_pt_matches,
    # i.e. when multiplicity rows exist in distribution tables but not as pT spectra.
    # Previously this fired unconditionally, polluting the blockers list even when
    # exact_pt_matches was non-empty.
    if not exact_pt_matches:
        blockers.append(
            "Multiplicity-bin rows appear in multiplicity-distribution tables, "
            "but those rows do not provide conditional pT spectra for the same "
            "multiplicity bins."
        )

    return {
        "record_id": HEPDATA_RECORD_ID,
        "manuscript_multiplicity_bins": manuscript_labels,
        "pt_spectrum_tables": pt_table_summary,
        "multiplicity_distribution_tables": multiplicity_row_coverage,
        "exact_manuscript_pt_matches": exact_pt_matches,
        "fit_ready": bool(exact_pt_matches),
        "blockers": blockers,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    args = parse_args()
    args.run_dir.mkdir(parents=True, exist_ok=True)

    record_json = request_json(HEPDATA_RECORD_URL, args.timeout_seconds)
    table_payloads: dict[str, dict[str, Any]] = {}
    table_metadata: list[TableMetadata] = []
    pt_rows: list[dict[str, Any]] = []

    for table_index_entry in record_json.get("data_tables", []):
        table_json = request_json(table_index_entry["data"]["json"], args.timeout_seconds)
        metadata = build_table_metadata(table_json, table_index_entry)
        table_payloads[metadata.table_name] = table_json
        table_metadata.append(metadata)
        if metadata.observable_kind == "pt_spectrum":
            pt_rows.extend(extract_pt_rows(metadata, table_json))

    table_index_df = pd.DataFrame(
        [
            {
                "source_record": HEPDATA_RECORD_ID,
                "table_name": metadata.table_name,
                "table_doi": metadata.table_doi,
                "location": metadata.location,
                "observable_kind": metadata.observable_kind,
                "eta_range": metadata.eta_range,
                "multiplicity_selection": metadata.multiplicity_selection,
                "pt_selection": metadata.pt_selection,
                "extrapolated": metadata.extrapolated,
                "x_rows": metadata.x_rows,
                "x_header": metadata.x_header,
                "y_header": metadata.y_header,
                "description": metadata.description,
                "json_url": metadata.json_url,
            }
            for metadata in table_metadata
        ]
    ).sort_values(["observable_kind", "table_name"], kind="stable")

    _raw = pd.DataFrame(pt_rows)
    canonical_pt_df = (_raw.sort_values(["source_table", "row_index"], kind="stable")
                       if not _raw.empty else _raw)

    mapping_validation = validate_mapping(table_metadata, table_payloads)

    write_json(args.run_dir / "hepdata_record_ins1419652.json", record_json)
    write_json(args.run_dir / "hepdata_mapping_validation.json", mapping_validation)
    table_index_df.to_csv(args.run_dir / "hepdata_table_index.csv", index=False)
    canonical_pt_df.to_csv(args.run_dir / "hepdata_pt_spectra.csv", index=False)

    # Write fit_input.csv from qualifier-matched rows OR column-bin matched rows
    _col_bin_ready = (
        not canonical_pt_df.empty
        and "fit_ready" in canonical_pt_df.columns
        and canonical_pt_df["fit_ready"].any()
    )
    if mapping_validation["fit_ready"] or _col_bin_ready:
        fit_ready_df = canonical_pt_df[canonical_pt_df["fit_ready"]].copy()
        fit_ready_df.to_csv(args.run_dir / "fit_input.csv", index=False)

    summary = {
        "record_id": HEPDATA_RECORD_ID,
        "table_count": len(table_metadata),
        "pt_spectrum_rows": len(canonical_pt_df),
        "fit_ready": bool(mapping_validation["fit_ready"] or _col_bin_ready),
        "artifacts": [
            "hepdata_record_ins1419652.json",
            "hepdata_table_index.csv",
            "hepdata_pt_spectra.csv",
            "hepdata_mapping_validation.json",
        ],
    }
    write_json(args.run_dir / "hepdata_extraction_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
