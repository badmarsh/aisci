#!/usr/bin/env python3
"""Probe ins1735345 table descriptions to find per-bin multiplicity pT spectra."""
import requests
import json
import time


def get_json(url):
    for i in range(3):
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if i < 2:
                time.sleep(2 ** i)
            else:
                raise


data = get_json("https://www.hepdata.net/record/ins1735345?format=json")
tables = data.get("data_tables", [])
print("=== ins1735345 table details ===")
for t in tables[:8]:
    tj = get_json(t["data"]["json"])
    print(f"  Name: {t['name']}")
    print(f"  Description: {tj.get('description', '')[:300]}")
    quals = tj.get("qualifiers", {})
    print(f"  Qualifier keys: {list(quals.keys())}")
    for k, v in quals.items():
        print(f"    {k}: {v}")
    print()

# Also search for better ALICE records
for rec in ["ins1822767", "ins1657387", "ins1803445"]:
    try:
        time.sleep(2)
        d = get_json(f"https://www.hepdata.net/record/{rec}?format=json")
        tables2 = d.get("data_tables", [])
        print(f"\n=== {rec} ({len(tables2)} tables) ===")
        t0 = get_json(tables2[0]["data"]["json"]) if tables2 else {}
        print(f"  First table desc: {t0.get('description','')[:200]}")
    except Exception as e:
        print(f"\n=== {rec} ERROR: {e} ===")
