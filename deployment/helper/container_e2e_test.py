import sqlite3
import jwt
import os
import urllib.request
import urllib.error
import json
import time
from datetime import datetime, timedelta, UTC

jwt_secret = os.environ.get("AUTH_JWT_SECRET")
db_path = "deployment/deer-flow/backend/.deer-flow/data/deerflow.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("select id, email, token_version from users where system_role='admin'")
row = c.fetchone()
conn.close()

user_id, email, token_version = row
now = datetime.now(UTC)
payload = {"sub": user_id, "exp": now + timedelta(days=7), "iat": now, "ver": token_version}
token = jwt.encode(payload, jwt_secret, algorithm="HS256")

BASE = "http://localhost:2026"

def req(path, method="GET", data=None):
    url = BASE + path
    headers = {
        "Cookie": f"access_token={token}; csrf_token=dummy_csrf",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    if method in ("POST", "PUT", "DELETE", "PATCH"):
        headers["X-CSRF-Token"] = "dummy_csrf"
    payload_bytes = json.dumps(data).encode("utf-8") if data else None
    r = urllib.request.Request(url, data=payload_bytes, method=method, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=15) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 999, str(e)

print("=" * 50)
print("DeerFlow E2E Authenticated Smoke Test")
print("=" * 50)

# Test 1: Auth
code, body = req("/api/v1/auth/me")
user_info = json.loads(body)
print(f"[1] Auth /me -> {code} | email={user_info.get('email')} role={user_info.get('system_role')}")
assert code == 200, f"Auth failed: {code} {body}"

# Test 2: Skills 
code, body = req("/api/skills")
skills_data = json.loads(body)
skill_names = [s.get("name") for s in skills_data.get("skills", [])]
print(f"[2] Skills -> {code} | count={len(skill_names)}")
assert code == 200

# Test 3: Models
code, body = req("/api/models")
models_data = json.loads(body)
model_names = [m.get("name") for m in models_data] if isinstance(models_data, list) else []
print(f"[3] Models -> {code} | count={len(model_names)} | first_3={model_names[:3]}")
assert code == 200

# Test 4: Create thread
code, body = req("/api/threads", method="POST", data={"metadata": {"title": "E2E Smoke Test"}})
thread_data = json.loads(body)
thread_id = thread_data.get("thread_id")
print(f"[4] Create thread -> {code} | thread_id={thread_id}")
assert code == 200 and thread_id

# Test 5: Create run with DEFAULT agent (assistant_id=None → uses default agent from config.yaml)
run_payload = {
    "assistant_id": None,
    "input": {
        "messages": [{"role": "user", "content": "Reply with exactly: DEERFLOW_E2E_OK"}]
    }
}
code, body = req(f"/api/threads/{thread_id}/runs", method="POST", data=run_payload)
run_data = json.loads(body)
run_id = run_data.get("run_id")
run_status = run_data.get("status")
print(f"[5] Create run -> {code} | run_id={run_id} | initial_status={run_status}")
assert code == 200 and run_id

# Test 6: Poll run status (max 30s)
print("[6] Polling run status...")
final_status = run_status
for i in range(15):
    time.sleep(2)
    code, body = req(f"/api/threads/{thread_id}/runs/{run_id}")
    final_status = json.loads(body).get("status")
    print(f"    poll {i+1}/15 -> {final_status}")
    if final_status not in ("pending", "running"):
        break

print(f"[6] Final run status: {final_status}")

# Test 7: Thread messages
code, body = req(f"/api/threads/{thread_id}/messages")
messages = json.loads(body) if code == 200 else []
print(f"[7] Thread messages -> {code} | count={len(messages)}")
for m in messages:
    event_type = m.get("event_type", m.get("role", "?"))
    content = m.get("content") or m.get("text") or ""
    print(f"    [{event_type}]: {str(content)[:120]}")

# Test 8: Onyx MCP proxy health (host port 8095)
print("[8] Onyx MCP proxy...")
try:
    with urllib.request.urlopen("http://onyx-mcp-proxy:80/onyx/sse", timeout=3) as r:
        print(f"    GET onyx-mcp-proxy:80/onyx/sse -> {r.status} PASS")
except urllib.error.HTTPError as e:
    print(f"    GET onyx-mcp-proxy:80/onyx/sse -> {e.code} (proxy reachable, auth required)")
except Exception as e:
    print(f"    GET onyx-mcp-proxy:80/onyx/sse -> ERROR: {e}")

print("=" * 50)
print("SUMMARY")
print(f"  Auth:         PASS")
print(f"  Skills:       {len(skill_names)} skills")
print(f"  Models:       {len(model_names)} models")
print(f"  Thread:       {thread_id}")
print(f"  Run status:   {final_status}")
print(f"  Messages:     {len(messages)}")
print("=" * 50)
