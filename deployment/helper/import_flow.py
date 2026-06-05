import requests

jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjEifQ.eyJpZCI6ImFWVlF2VmVCc0tNdE95SWFGd09NSCIsInR5cGUiOiJVU0VSIiwicGxhdGZvcm0iOnsiaWQiOiI2ZkFVcWdKNVg4aWtHZFZ2WlhoczcifSwidG9rZW5WZXJzaW9uIjoiX2xNekFWWVBiNU92WUNtMVM4cE9CIiwiaWF0IjoxNzgwNjAyMDc3LCJleHAiOjE3ODEyMDY4NzcsImlzcyI6ImFjdGl2ZXBpZWNlcyJ9._FQx8_hPaJEABg2X29emrRbv5hSUPjDnPE7G8wsVRmU"
project_id = "KaLdcxpzcwALFF8CAGyfr"
headers = {"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"}

trigger = {
    "name": "trigger",
    "type": "PIECE_TRIGGER",
    "valid": True,
    "displayName": "Catch Webhook",
    "settings": {
        "pieceName": "@activepieces/piece-webhook",
        "pieceVersion": "~0.1.34",
        "pieceType": "OFFICIAL",
        "triggerName": "catch_request",
        "input": {},
        "inputUiInfo": {}
    },
    "nextAction": {
      "name": "step_1",
      "type": "PIECE",
      "valid": True,
      "displayName": "Trigger Python Agent",
      "settings": {
        "pieceName": "@activepieces/piece-http",
        "pieceType": "OFFICIAL",
        "pieceVersion": "~0.11.9",
        "actionName": "send_request",
        "input": {
          "method": "POST",
          "url": "http://host.docker.internal:8000/run_script",
          "body": {
            "script": "trigger_onyx_agent.py",
            "args": [
              "--card-id",
              "{{trigger.body.issue_id}}",
              "--persona",
              "arxiv_researcher"
            ]
          },
          "headers": {
            "Content-Type": "application/json"
          }
        },
        "inputUiInfo": {}
      }
    }
}

print("Creating flow...")
res = requests.post("http://localhost:8082/api/v1/flows", json={"projectId": project_id, "displayName": "Weekly ArXiv Scan"}, headers=headers)
flow_id = res.json()["id"]

print(f"Applying UPDATE_TRIGGER to {flow_id}...")
op = {
    "type": "UPDATE_TRIGGER",
    "request": trigger
}
res_op = requests.post(f"http://localhost:8082/api/v1/flows/{flow_id}", json=op, headers=headers)
print(res_op.status_code)
print(res_op.text[:500])
