import requests, time, os, json

key = os.environ.get('ASTA_API_KEY', '')
if not key:
    try:
        for line in open('/home/ubuntu/aisci/deployment/onyx/.env'):
            if 'ASTA_API_KEY' in line and '=' in line and not line.startswith('#'):
                key = line.strip().split('=', 1)[1].strip().strip('"').strip("'")
                break
    except Exception:
        pass

ASTA_HEADERS = {
    'x-api-key': key,
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/event-stream'
}
ASTA_URL = 'https://asta-tools.allen.ai/mcp/v1'

def asta_call(method, params, req_id=1):
    payload = {'jsonrpc': '2.0', 'id': req_id, 'method': method, 'params': params}
    r = requests.post(ASTA_URL, headers=ASTA_HEADERS, json=payload, timeout=30)
    for line in r.text.splitlines():
        if line.startswith('data:'):
            try:
                return json.loads(line[5:].strip())
            except Exception:
                pass
    return {}

def asta_tool(name, arguments, req_id=1):
    res = asta_call('tools/call', {'name': name, 'arguments': arguments}, req_id=req_id)
    content = res.get('result', {}).get('content', [])
    if content:
        text = content[0].get('text', '')
        try:
            return json.loads(text)
        except Exception:
            return text
    err = res.get('result', {}).get('content', [{}])
    return res

# --- 1: snippet_search (full-text inside papers) ---
print('=== ASTA snippet_search: Tsallis + rapidity/Jacobian ===')
r1 = asta_tool('snippet_search', {
    'query': 'Tsallis distribution pseudorapidity rapidity Jacobian dy deta pion ALICE',
    'limit': 6
}, req_id=1)
if isinstance(r1, list):
    for s in r1:
        print(f"\n[{s.get('year','?')}] {s.get('title','?')}")
        print('ID:', s.get('paperId', s.get('externalIds', {}).get('ArXiv', '?')))
        print('Text:', str(s.get('text', s.get('snippet','')))[:350])
elif isinstance(r1, str):
    print(r1[:1500])
else:
    print(json.dumps(r1, indent=2)[:1500])
time.sleep(1)

# --- 2: search_papers_by_relevance ---
print('\n=== ASTA search_papers_by_relevance: Tsallis rapidity Jacobian ===')
r2 = asta_tool('search_papers_by_relevance', {
    'keyword': 'Tsallis distribution pseudorapidity rapidity Jacobian heavy-ion ALICE',
    'limit': 6
}, req_id=2)
if isinstance(r2, list):
    for p in r2:
        arxiv = (p.get('externalIds') or {}).get('ArXiv', '')
        print(f"  [{p.get('year','?')}] {p.get('title','?')} arXiv:{arxiv}")
elif isinstance(r2, str):
    print(r2[:1500])
else:
    print(json.dumps(r2, indent=2)[:1500])
time.sleep(1)

# --- 3: get_citations for Cleymans paper ---
print('\n=== ASTA get_citations: Cleymans arXiv:1110.5526 ===')
r3 = asta_tool('get_citations', {
    'paper_id': 'ARXIV:1110.5526',
    'limit': 10
}, req_id=3)
if isinstance(r3, list):
    for p in r3:
        arxiv = (p.get('externalIds') or {}).get('ArXiv', '')
        print(f"  [{p.get('year','?')}] {p.get('title','?')} arXiv:{arxiv} (cites:{p.get('citationCount',0)})")
elif isinstance(r3, str):
    print(r3[:1500])
else:
    print(json.dumps(r3, indent=2)[:1500])
