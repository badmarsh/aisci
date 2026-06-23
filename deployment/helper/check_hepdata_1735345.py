#!/usr/bin/env python3
"""Check HEPData ins1735345 table 1 headers and qualifiers to resolve O-05."""
import json
import urllib.request

headers_http = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Accept": "application/json",
}

# Fetch the actual table 1 data
TABLE_URL = "https://www.hepdata.net/download/table/ins1735345/Table%201/json"
req = urllib.request.Request(TABLE_URL, headers=headers_http)
response = urllib.request.urlopen(req, timeout=30)
data = json.loads(response.read())

print("=== TABLE 1 STRUCTURE ===")
print(f"Name: {data.get('name')}")
print(f"Location: {data.get('location')}")
print(f"Description: {str(data.get('description',''))[:200]}")
print()

headers = data.get("headers", [])
print("Headers:")
for h in headers:
    print(f"  {h}")

qualifiers = data.get("qualifiers", {})
print("\nQualifiers:")
for k, v in qualifiers.items():
    print(f"  '{k}': {v}")

# Check first few values
values = data.get("values", [])
print(f"\nTotal values: {len(values)}")
if values:
    print(f"First value x: {values[0].get('x')}")
    print(f"First value y header count: {len(values[0].get('y',[]))}")
