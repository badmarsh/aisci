from __future__ import annotations
import requests, os, json

key = ''
try:
    for line in open('/home/ubuntu/aisci/deployment/onyx/.env'):
        if 'ONYX_API_KEY' in line and '=' in line and not line.startswith('#'):
            key = line.strip().split('=', 1)[1].strip().strip('"').strip("'")
            break
except Exception:
    pass

headers = {'Authorization': f'Bearer {key}'}

# Check exact user prompts in both sessions
for session_id, label in [
    ('a2d15bd1-bda7-4ef9-9b3f-ff10b713d300', 'Session A (good)'),
    ('a843d321-fec0-414d-9213-633769d03858', 'Session B (deep research)'),
]:
    r = requests.get(f'http://localhost:3000/api/chat/get-chat-session/{session_id}',
                     headers=headers, timeout=10)
    data = r.json()
    print(f'\n=== {label} ===')
    for m in data.get('messages', []):
        if m.get('message_type') == 'user':
            content = m.get('message', '')
            print(f'Prompt ({len(content)} chars): |{content}|')
            break

# Check persona 1 system prompt length
print('\n=== PERSONA 1 (Scientific Researcher) system prompt ===')
r2 = requests.get('http://localhost:3000/api/persona', headers=headers, timeout=10)
if r2.status_code == 200:
    personas = r2.json()
    if isinstance(personas, list):
        for p in personas:
            if p.get('id') == 1:
                prompt = p.get('system_prompt') or p.get('prompt_text') or ''
                print(f'System prompt length: {len(prompt)} chars')
                print(f'First 200 chars: {prompt[:200]}')
                print(f'Tools: {[t.get("name","?") for t in (p.get("tools") or [])]}')
    else:
        print(json.dumps(personas, indent=2)[:500])
