import json

with open("deployment/helper/openapi.json", "r") as f:
    schema = json.load(f)

print(json.dumps(schema.get("components", {}).get("schemas", {}).get("SearchRequest"), indent=2))
