import requests
import os
import json
import time

def test_semantic_scholar():
    api_key = os.environ.get("SEMANTICSCHOLAR_API_KEY")
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
        print("Using authenticated Semantic Scholar API.")
    else:
        print("WARNING: SEMANTICSCHOLAR_API_KEY not found. Using public endpoint (strict rate limits).")

    # Cleymans & Worku (2012) arXiv ID
    paper_id = "ARXIV:1110.5526"
    base_url = "https://api.semanticscholar.org/graph/v1"

    print(f"Fetching details for {paper_id}...")
    try:
        time.sleep(2) # Ensure we are well below the 1 req/s cumulative limit
        # Get basic paper details
        resp = requests.get(
            f"{base_url}/paper/{paper_id}",
            params={"fields": "title,year,citationCount,abstract,tldr"},
            headers=headers
        )
        resp.raise_for_status()
        data = resp.json()
        print("\n--- Paper Details ---")
        print(f"Title: {data.get('title')}")
        print(f"Year: {data.get('year')}")
        print(f"Citation Count: {data.get('citationCount')}")
        tldr = data.get('tldr')
        print(f"TLDR: {tldr.get('text') if tldr else 'N/A'}")

        time.sleep(2) # Rate limit 1 req/s, cumulative

        # Fetch first page of citations
        print("\nFetching first 5 citations...")
        resp_cites = requests.get(
            f"{base_url}/paper/{paper_id}/citations",
            params={"fields": "title,year", "limit": 5},
            headers=headers
        )
        resp_cites.raise_for_status()
        cites_data = resp_cites.json()
        
        print("\n--- Citations ---")
        for i, item in enumerate(cites_data.get('data', [])):
            cite = item.get('citingPaper', {})
            print(f"{i+1}. {cite.get('title')} ({cite.get('year')})")

        print("\nSUCCESS: Semantic Scholar API is working correctly.")
        
    except requests.exceptions.RequestException as e:
        print(f"API Request Failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    # Load env from .env if needed
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="/home/ubuntu/aisci/.env")
    test_semantic_scholar()
