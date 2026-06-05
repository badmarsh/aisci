#!/usr/bin/env python3
import requests
import json

url = "https://www.hepdata.net/record/ins1735345?format=json"
r = requests.get(url).json()
t1_url = None
for t in r.get("data_tables", []):
    if t["name"] == "Table 1":
        t1_url = t["data"]["json"]
        break

if t1_url:
    t1 = requests.get(t1_url).json()
    print("=== Headers ===")
    print(json.dumps(t1.get("headers"), indent=2))
    
    print("\n=== Row 0 ===")
    print(json.dumps(t1.get("values")[0] if t1.get("values") else None, indent=2))
    
    print("\n=== Row 1 ===")
    print(json.dumps(t1.get("values")[1] if t1.get("values") else None, indent=2))
else:
    print("Table 1 URL not found")
