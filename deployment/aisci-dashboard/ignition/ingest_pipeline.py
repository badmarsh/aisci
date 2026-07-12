import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import sys, os
import hashlib
sys.path.insert(0, os.path.dirname(__file__))
from database import init_db
from extraction_engine import extract_insights

def fetch_arxiv_papers(search_query, max_results=5):
    url = f'http://export.arxiv.org/api/query?search_query={search_query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending'
    try:
        response = urllib.request.urlopen(url)
        data = response.read()
        root = ET.fromstring(data)
    except Exception as e:
        print(f"arXiv fetch failed: {e}")
        return []

    papers = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        paper_id = entry.find('{http://www.w3.org/2005/Atom}id').text.split('/')[-1]
        title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', ' ')
        abstract = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip().replace('\n', ' ')
        published = entry.find('{http://www.w3.org/2005/Atom}published').text
        url_link = entry.find('{http://www.w3.org/2005/Atom}id').text
        category = entry.find('{http://arxiv.org/schemas/atom}primary_category').attrib.get('term', '')

        papers.append({
            'id': paper_id,
            'title': title,
            'abstract': abstract,
            'published': published,
            'url': url_link,
            'category': category
        })

    return papers

import json

def reconstruct_abstract(inverted_index):
    if not inverted_index:
        return ""
    max_index = 0
    for indices in inverted_index.values():
        if indices:
            max_index = max(max_index, max(indices))
    words = [""] * (max_index + 1)
    for word, indices in inverted_index.items():
        for i in indices:
            words[i] = word
    return " ".join(words).strip()

def fetch_openalex_papers(search_query, max_results=5):
    encoded_query = urllib.parse.quote(search_query)
    url = f'https://api.openalex.org/works?search={encoded_query}&per-page={max_results}&sort=publication_date:desc'
    req = urllib.request.Request(url, headers={'User-Agent': 'mailto:test@example.com'})
    try:
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
    except Exception as e:
        print(f"OpenAlex fetch failed: {e}")
        return []

    papers = []
    for item in data.get('results', []):
        paper_id = item.get('id', '').split('/')[-1]
        title = item.get('title', 'No Title')

        abstract_idx = item.get('abstract_inverted_index')
        abstract = reconstruct_abstract(abstract_idx) if abstract_idx else ""

        published = item.get('publication_date', '')

        primary_loc = item.get('primary_location') or {}
        url_link = primary_loc.get('landing_page_url') or item.get('doi', '')

        # Best guess for category
        concepts = item.get('concepts', [])
        category = concepts[0].get('display_name', '') if concepts else 'OpenAlex-General'

        papers.append({
            'id': paper_id,
            'title': title,
            'abstract': abstract,
            'published': published,
            'url': url_link,
            'category': category
        })
    return papers

def run_ingest(test_mode=False):
    project_id = "robert-boson-manuscript"
    init_db(project_id)

    # 1. Physics Literature Radar (HEP)
    hep_query = 'cat:hep-ph+OR+cat:hep-ex'
    oa_hep_query = 'high energy physics'

    # 2. Computer Science Radar (CS->HEP Bridge)
    cs_query = 'cat:cs.AI+OR+cat:stat.ML'
    oa_cs_query = 'machine learning in physics'

    max_res = 2 if test_mode else 10

    print("Fetching HEP papers (arXiv)...")
    hep_papers = fetch_arxiv_papers(hep_query, max_results=max_res)
    print("Fetching HEP papers (OpenAlex)...")
    oa_hep_papers = fetch_openalex_papers(oa_hep_query, max_results=max_res)

    print("Fetching CS papers (arXiv)...")
    cs_papers = fetch_arxiv_papers(cs_query, max_results=max_res)
    print("Fetching CS papers (OpenAlex)...")
    oa_cs_papers = fetch_openalex_papers(oa_cs_query, max_results=max_res)

    all_papers = hep_papers + oa_hep_papers + cs_papers + oa_cs_papers

    for p in all_papers:
        print(f"Processing [{p['category']}]: {p['title']}")

        content = p['id'] + p['title'] + p['abstract']
        source_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        provider = "mock"
        if os.environ.get("OPENAI_API_KEY") or os.environ.get("AISCI_AI_PROVIDER") == "openai":
            provider = "openai"
            # OpenAI branch logic (placeholder)
            # insights = call_openai_extraction(p['title'], p['abstract'])
            insights = extract_insights(project_id, p['title'], p['abstract'], p['category'])
            provenance = "Ingested via OpenAI API"
        elif os.environ.get("MCP_SERVER_URL"):
            provider = "mcp"
            # MCP branch logic (placeholder)
            # insights = call_mcp_extraction(...)
            insights = extract_insights(project_id, p['title'], p['abstract'], p['category'])
            provenance = "Ingested via MCP Backend"
        else:
            # Mock LLM fallback
            insights = extract_insights(project_id, p['title'], p['abstract'], p['category'])
            provenance = "Ingested via mock local parser"

        payload = {
            "id": p['id'],
            "title": p['title'],
            "abstract": p['abstract'],
            "published": p['published'],
            "url": p['url'],
            "category": p['category'],
            "provenance": provenance,
            "source_hash": source_hash,
            "claims": insights['claims'],
            "datasets": insights['datasets']
        }

        try:
            req = urllib.request.Request(
                f"http://127.0.0.1:8001/api/projects/{project_id}/literature",
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req)
        except Exception as e:
            print(f"Failed to post via webhook: {e}")

    print(f"Ingest complete. Processed {len(all_papers)} papers.")

if __name__ == '__main__':
    import sys
    test_mode = '--test' in sys.argv
    run_ingest(test_mode=test_mode)
