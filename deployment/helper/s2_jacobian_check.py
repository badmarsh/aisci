from __future__ import annotations
import requests, time, os, json

# Read API key from env or .env file
key = os.environ.get('SEMANTICSCHOLAR_API_KEY', '')
if not key:
    try:
        for line in open('/home/ubuntu/aisci/deployment/onyx/.env'):
            if 'SEMANTICSCHOLAR_API_KEY' in line and '=' in line and not line.startswith('#'):
                key = line.strip().split('=', 1)[1].strip().strip('"').strip("'")
                break
    except Exception:
        pass

if not key:
    print('ERROR: SEMANTICSCHOLAR_API_KEY not found')
    exit(1)

HEADERS = {'x-api-key': key}
BASE = 'https://api.semanticscholar.org/graph/v1'

# --- Step 1: Paper lookup ---
r = requests.get(
    f'{BASE}/paper/ARXIV:1110.5526',
    params={'fields': 'paperId,citationCount,tldr,year,title'},
    headers=HEADERS, timeout=15
)
meta = r.json()
print('=== PAPER ===')
print('Title:', meta.get('title'))
print('Year:', meta.get('year'))
print('Citations:', meta.get('citationCount'))
tldr = meta.get('tldr') or {}
print('TLDR:', tldr.get('text', 'none'))
paper_id = meta.get('paperId')
time.sleep(1)

# --- Step 2: Citation traversal ---
r = requests.get(
    f'{BASE}/paper/{paper_id}/citations',
    params={'fields': 'title,year,abstract,citationCount,externalIds', 'limit': 100},
    headers=HEADERS, timeout=15
)
cites_data = r.json()
cites = cites_data.get('data', [])
total_cites = meta.get('citationCount', 0)
print()
print(f'=== CITATIONS (showing {len(cites)} of {total_cites}) ===')
time.sleep(1)

# Filter for pseudorapidity/Jacobian mentions
keywords = ['pseudorapidity', 'jacobian', 'dy/d', 'eta_max', 'rapidity acceptance',
            'eta range', 'pseudo-rapidity', 'rapidity to pseudorapidity']
hits = []
for c in cites:
    p = c.get('citingPaper', {})
    abst = (p.get('abstract') or '').lower()
    title_lower = (p.get('title') or '').lower()
    if any(kw in abst or kw in title_lower for kw in keywords):
        hits.append(p)

print('Mentioning pseudorapidity/Jacobian:', len(hits))
for h in hits[:8]:
    arxiv = (h.get('externalIds') or {}).get('ArXiv', '')
    print(' ', h.get('year'), '|', h.get('title'), '| arXiv:', arxiv, '| cites:', h.get('citationCount', 0))

# --- Step 3: Bulk boolean search ---
print()
print('=== BULK SEARCH: Tsallis + pseudorapidity (Physics field) ===')
r = requests.get(
    f'{BASE}/paper/search/bulk',
    params={
        'query': '"Tsallis" + pseudorapidity + rapidity',
        'fields': 'title,year,externalIds,citationCount',
        'sort': 'citationCount:desc',
    },
    headers=HEADERS, timeout=15
)
bulk = r.json()
print('Total matching:', bulk.get('total', 0))
for p in bulk.get('data', [])[:10]:
    arxiv = (p.get('externalIds') or {}).get('ArXiv', '')
    print(' ', p.get('year'), '|', p.get('title'), '| arXiv:', arxiv, '| cites:', p.get('citationCount', 0))
