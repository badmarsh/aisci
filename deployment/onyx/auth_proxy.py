"""
Auth proxy sidecar: intercepts JSON login requests from the frontend
and forwards them as form-data to the Onyx API server.

The Onyx frontend sends: POST /api/auth/login with {"email": "...", "password": "..."}
The Onyx backend expects: POST /auth/login with username=...&password=... (form data)

This bridge transforms the request format.
"""

import os
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()

API_SERVER_URL = os.environ.get("API_SERVER_URL", "http://api_server:8080")


import json
import urllib.parse

@app.post("/auth/login")
async def login(request: Request):
    print(f"--- INCOMING REQUEST ---")
    print(f"Headers: {request.headers}")
    try:
        raw_body = await request.body()
        print(f"Body length: {len(raw_body)}")
        if not raw_body:
            return Response(status_code=400, content="Empty body")
            
        content_type = request.headers.get("content-type", "")
        if "application/x-www-form-urlencoded" in content_type:
            # Parse form data into a dict
            parsed = urllib.parse.parse_qsl(raw_body.decode('utf-8'))
            body = dict(parsed)
        else:
            # Default to JSON parsing
            body = json.loads(raw_body)
            
    except Exception as e:
        print(f"Error parsing body: {e}")
        return Response(status_code=400, content="Invalid format")

    email = body.get("email", body.get("username", ""))
    password = body.get("password", "")

    safe_headers = {
        "x-forwarded-for", "x-real-ip", "x-forwarded-proto", 
        "x-forwarded-host", "x-forwarded-port", "user-agent",
        "accept", "accept-language"
    }
    
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() in safe_headers
    }
    
    # Explicitly set the host header to what nginx sent us, or fallback
    headers["Host"] = request.headers.get("x-forwarded-host", request.headers.get("host", ""))
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    # Forward as form-data to the real API server
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_SERVER_URL}/auth/login",
            data={"username": email, "password": password},
            headers=headers,
            follow_redirects=False,
        )

    # Build response with the same status and cookies
    response = Response(status_code=resp.status_code)
    for key, value in resp.headers.items():
        if key.lower() in ("set-cookie", "content-type", "content-length"):
            response.headers[key] = value

    # Copy any auth cookies from the response
    return response


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
