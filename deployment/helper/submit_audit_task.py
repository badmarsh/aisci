#!/usr/bin/env python3
from __future__ import annotations
"""Submit comprehensive audit task to DeerFlow"""

import requests
import json

# Read the audit prompt
with open('/mnt/user-data/uploads/COMPREHENSIVE_AUDIT_PROMPT.md', 'r') as f:
    audit_instructions = f.read()

# Create the full prompt
prompt = f"""Execute the following comprehensive audit of the AISCI codebase.

{audit_instructions}

IMPORTANT: The codebase is located at /mnt/host/aisci/ in your sandbox environment.

Begin the systematic audit now, starting with security and configuration issues."""

# DeerFlow API endpoint
base_url = "http://localhost:2026"
csrf_url = f"{base_url}/api/v1/csrf-token"
api_url = f"{base_url}/api/v1/sessions"

print("Submitting comprehensive audit task to DeerFlow...")
print(f"Prompt length: {len(prompt)} characters")

# Create a session to maintain cookies
session = requests.Session()

try:
    # Get CSRF token
    print("\nGetting CSRF token...")
    csrf_response = session.get(csrf_url)
    csrf_response.raise_for_status()
    csrf_token = csrf_response.json().get('csrf_token')
    print(f"✓ Got CSRF token: {csrf_token[:20]}...")

    # Create session payload
    payload = {
        "message": prompt,
        "agent_name": "coder",
        "model_name": "gemini-2.5-flash",
        "stream": False
    }

    # Add CSRF token to headers
    headers = {
        "X-CSRF-Token": csrf_token,
        "Content-Type": "application/json"
    }

    print("\nSending audit request...")
    response = session.post(api_url, json=payload, headers=headers, timeout=300)
    response.raise_for_status()

    result = response.json()
    print("\n✓ Task submitted successfully!")
    print(f"\nSession ID: {result.get('session_id', 'N/A')}")
    print(f"Status: {result.get('status', 'N/A')}")

    if 'response' in result:
        print("\n" + "="*80)
        print("AUDIT RESPONSE:")
        print("="*80)
        print(result['response'])

except requests.exceptions.RequestException as e:
    print(f"\n✗ Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response status: {e.response.status_code}")
        print(f"Response body: {e.response.text[:500]}")
