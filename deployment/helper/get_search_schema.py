from __future__ import annotations
import json

with open("deployment/helper/openapi.json", "r") as f:
    schema = json.load(f)

print(json.dumps(schema.get("paths", {}).get("/search"), indent=2))
