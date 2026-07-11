#!/usr/bin/env python3
from __future__ import annotations
"""
DeerFlow E2E authenticated smoke test.
Uses cookie-based auth (access_token cookie) as DeerFlow requires.
"""
import json
import sys
import urllib.request
import urllib.error
import http.cookiejar

BASE = "http://localhost:2026"
# Retrieve from env, fallback to reading .env.local or .env paths
import os
from pathlib import Path
def get_admin_email():
    if os.environ.get("ADMIN_EMAIL"):
        return os.environ.get("ADMIN_EMAIL")
    # Check Onyx env files
    for path in ["deployment/onyx/.env.local", "deployment/onyx/.env"]:
        p = Path(path)
        if p.exists():
            for line in p.read_text().splitlines():
                if line.startswith("ADMIN_EMAIL="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
    return "admin@aisci.local"
ADMIN_EMAIL = get_admin_email()
# Try common passwords; the actual password is in .env.local or was set at first boot
PASSWORDS_TO_TRY = ["admin", "admin1234", "Admin1234!", "deerflow", "password"]


def req(opener, method, path, data=None, label=""):
    url = BASE + path
    payload = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=payload, method=method)
    r.add_header("Content-Type", "application/json")
    try:
        with opener.open(r, timeout=10) as resp:
            body = resp.read().decode()
            code = resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        code = e.code
    print(f"  {method} {path} -> {code}")
    if body and len(body) < 400:
        print(f"    {body.strip()}")
    return code, body


def main():
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    print("=== DeerFlow E2E Authenticated Smoke Test ===\n")

    # 1. Setup status — is admin initialized?
    print("[1] Setup status...")
    code, body = req(opener, "GET", "/api/auth/setup-status")
    try:
        needs_setup = json.loads(body).get("needs_setup", False)
        print(f"    needs_setup={needs_setup}")
    except Exception:
        needs_setup = False

    # 2. Login
    print("\n[2] Login attempt...")
    token = None
    for pw in PASSWORDS_TO_TRY:
        code, body = req(opener, "POST", "/api/auth/login",
                        data={"email": ADMIN_EMAIL, "password": pw},
                        label=f"pw={pw}")
        if code == 200:
            print(f"    LOGIN OK with password (len={len(pw)})")
            # Cookie is set automatically by CookieJar
            cookies = {c.name: c.value for c in jar}
            token = cookies.get("access_token")
            print(f"    access_token cookie present: {bool(token)}")
            break
        elif code == 401 or code == 400:
            print(f"    Wrong password (len={len(pw)}) -> {code}")
        else:
            print(f"    Unexpected: {code}")

    if not token and not needs_setup:
        print("\n    Could not login — password unknown. Try /api/auth/change-password from the UI.")

    # 3. /api/auth/me
    print("\n[3] Auth /me endpoint...")
    code, body = req(opener, "GET", "/api/auth/me")
    if code == 200:
        info = json.loads(body)
        print(f"    PASS — logged in as: {info.get('email')} role={info.get('system_role')}")
    else:
        print(f"    FAIL — {code}")

    # 4. Run list
    print("\n[4] Run list (authenticated)...")
    code, body = req(opener, "GET", "/api/runs")
    if code == 200:
        runs = json.loads(body)
        print(f"    PASS — {len(runs) if isinstance(runs, list) else '?'} runs found")
    else:
        print(f"    FAIL — {code}")

    # 5. Onyx MCP proxy health (host-side)
    print("\n[5] Onyx MCP proxy health...")
    try:
        with urllib.request.urlopen("http://localhost:8095/onyx/sse", timeout=3) as r:
            print(f"    GET :8095/onyx/sse -> {r.status} PASS")
    except urllib.error.HTTPError as e:
        print(f"    GET :8095/onyx/sse -> {e.code} (may need auth, proxy is reachable)")
    except Exception as e:
        print(f"    GET :8095/onyx/sse -> ERROR: {e}")

    # 6. Onyx search tool (via DeerFlow if authenticated)
    print("\n[6] DeerFlow /api/tools list...")
    code, body = req(opener, "GET", "/api/tools")
    if code == 200:
        tools = json.loads(body)
        names = [t.get("name") for t in tools] if isinstance(tools, list) else list(tools.keys())
        print(f"    PASS — {len(names)} tools: {names[:8]}")
        onyx_present = any("onyx" in str(n).lower() for n in names)
        print(f"    onyx_search present: {onyx_present}")
    else:
        print(f"    NOTE: {code} — {body[:200]}")

    print("\n=== Done ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
