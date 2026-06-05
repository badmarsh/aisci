#!/usr/bin/env python3
"""
Probe HEPData records to find one that contains per-multiplicity-bin pT spectra
matching Robert's manuscript bins: 21-30, 31-40, 41-50, 51-60, 61-70, 71-80,
81-90, 91-100, 101-125, 126-150.

Usage:
    python probe_hepdata.py
"""
import json
import time
import requests

MANUSCRIPT_BINS = [
    "21-30", "31-40", "41-50", "51-60", "61-70",
    "71-80", "81-90", "91-100", "101-125", "126-150",
]

CANDIDATE_RECORDS = [
    "ins1735345",   # arXiv:1905.07208 charged-particle production vs mult+spherocity 5.02+13 TeV
    "ins1657384",   # possible alt record
    "ins1784209",   # possible alt record
    "ins1657384",
    "ins1822767",   # ALICE mult-dep pi K p at 13 TeV
    "ins1657387",
]


def get_json(url, timeout=30):
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


def probe_record(rec_id):
    url = f"https://www.hepdata.net/record/{rec_id}?format=json"
    print(f"\n=== {rec_id} ===")
    try:
        data = get_json(url)
    except Exception as e:
        print(f"  FETCH ERROR: {e}")
        return

    tables = data.get("data_tables", [])
    print(f"  Total tables: {len(tables)}")

    pt_spectrum_hits = []
    mult_bin_hits = []

    for t in tables:
        try:
            tj = get_json(t["data"]["json"], timeout=20)
        except Exception as e:
            print(f"  Table fetch error: {e}")
            continue

        headers = tj.get("headers", [])
        hnames = [h.get("name", "") for h in headers]
        quals = tj.get("qualifiers", {})
        mult_qual = quals.get("N(P=3)", [{}])
        mult_val = mult_qual[0].get("value", "") if mult_qual else ""
        nrows = len(tj.get("values", []))

        # Check if this looks like a pT spectrum
        is_pt = any("PT" in h or "pT" in h.lower() for h in hnames)
        # Check if multiplicity qualifier matches any manuscript bin
        matches = [b for b in MANUSCRIPT_BINS if b == mult_val.strip()]

        status = []
        if is_pt:
            status.append("pt_spectrum")
        if matches:
            status.append(f"MATCHES_BINS:{matches}")

        print(f"  {t['name']}: headers={hnames[:3]}, mult={mult_val!r}, rows={nrows}, {status}")

        if is_pt and matches:
            pt_spectrum_hits.append({"table": t["name"], "mult": mult_val, "rows": nrows})

    if pt_spectrum_hits:
        print(f"\n  *** FOUND per-bin pT spectra in {rec_id}: {pt_spectrum_hits} ***")
    else:
        print(f"  No matching per-bin pT spectra found in {rec_id}")

    return pt_spectrum_hits


def main():
    seen = set()
    all_hits = {}
    for rec in CANDIDATE_RECORDS:
        if rec in seen:
            continue
        seen.add(rec)
        hits = probe_record(rec)
        if hits:
            all_hits[rec] = hits

    print("\n\n=== SUMMARY ===")
    if all_hits:
        for rec, hits in all_hits.items():
            print(f"  {rec}: {hits}")
    else:
        print("  No candidate records contain per-bin pT spectra matching manuscript bins.")
        print("  Robert must provide the data table directly.")


if __name__ == "__main__":
    main()
