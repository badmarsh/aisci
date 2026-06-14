from __future__ import annotations
import requests
import json

res = requests.get("https://cloud.activepieces.com/api/v1/flow-templates?pieces=@activepieces/piece-webhook")
if res.status_code == 200:
    templates = res.json().get('data', [])
    if templates:
        # Get full template details
        tmpl_res = requests.get(f"https://cloud.activepieces.com/api/v1/flow-templates/{templates[0]['id']}")
        with open('template_example.json', 'w') as f:
            json.dump(tmpl_res.json(), f, indent=2)
        print("Template example saved")
        print(json.dumps(tmpl_res.json()['template']['trigger'], indent=2)[:500])
    else:
        print("No templates found")
else:
    print("Failed to fetch templates:", res.status_code)
