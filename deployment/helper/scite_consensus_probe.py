import requests, json

# Probe Scite and Consensus via the nginx MCP proxy
# These use OAuth — try without token first to see what error we get,
# then try with a probe to see if token is stored in MCP client cache

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/event-stream'
}
JSONRPC = {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list', 'params': {}}

for name, url in [('Scite', 'http://127.0.0.1:8095/scite/'),
                  ('Consensus', 'http://127.0.0.1:8095/consensus/')]:
    print(f'=== {name} ===')
    try:
        r = requests.post(url, headers=HEADERS, json=JSONRPC, timeout=15)
        print('Status:', r.status_code)
        print('Response headers:', dict(list(r.headers.items())[:8]))
        print('Body:', r.text[:800])
    except Exception as e:
        print('Error:', e)
    print()
