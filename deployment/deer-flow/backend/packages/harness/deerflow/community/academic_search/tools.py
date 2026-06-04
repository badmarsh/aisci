"""Academic Search Tool — searches ArXiv and Semantic Scholar simultaneously,
merges and deduplicates results for scientific/academic queries."""

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain.tools import tool

logger = logging.getLogger(__name__)


def _search_arxiv(query: str, max_results: int = 5) -> list[dict]:
    """Search ArXiv for academic papers."""
    try:
        import urllib.request
        import xml.etree.ElementTree as ET

        url = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&max_results={max_results}&sortBy=relevance"
        req = urllib.request.Request(url, headers={"User-Agent": "DeerFlow/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_data = resp.read().decode("utf-8")

        root = ET.fromstring(xml_data)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)

        results = []
        for entry in entries[:max_results]:
            title = entry.find("atom:title", ns).text.strip() if entry.find("atom:title", ns) is not None else ""
            summary = entry.find("atom:summary", ns).text.strip() if entry.find("atom:summary", ns) is not None else ""
            link_el = entry.find("atom:id", ns)
            url = link_el.text.strip() if link_el is not None else ""
            published = entry.find("atom:published", ns)
            pub_date = published.text.strip() if published is not None else ""

            results.append({
                "title": title,
                "url": url,
                "content": f"[{pub_date}] {summary[:500]}",
                "source": "arxiv",
            })
        return results
    except Exception as e:
        logger.error(f"ArXiv search failed: {e}")
        return []


def _search_semantic_scholar(query: str, max_results: int = 5) -> list[dict]:
    """Search Semantic Scholar for academic papers."""
    import httpx
    import os

    base_url = os.environ.get("SEMANTICSCHOLAR_API_BASE", "http://onyx-mcp-proxy:80/semanticscholar")
    if base_url.endswith("/"):
        base_url = base_url[:-1]
    
    url = f"{base_url}/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": max_results,
        "fields": "title,abstract,url,year,authors,venue,citationCount",
    }
    
    api_key = os.environ.get("SEMANTICSCHOLAR_API_KEY")
    headers = {"x-api-key": api_key} if api_key else {}

    try:
        resp = httpx.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        papers = data.get("data", [])
        results = []
        for p in papers[:max_results]:
            authors = ", ".join([a.get("name", "") for a in p.get("authors", []) if a.get("name")])[:100]
            year = p.get("year", "")
            venue = p.get("venue", "")
            citations = p.get("citationCount", 0)
            abstract = p.get("abstract", "")
            results.append({
                "title": p.get("title", ""),
                "url": p.get("url", ""),
                "content": f"{authors}. {venue} ({year}) [Citations: {citations}] — {abstract[:400]}",
                "source": "semanticscholar",
            })
        return results
    except Exception as e:
        logger.error(f"Semantic Scholar search failed: {e}")
        return []


@tool("academic_search", parse_docstring=True)
def academic_search_tool(
    query: str,
    max_results: int = 5,
) -> str:
    """Search academic papers across ArXiv and Semantic Scholar simultaneously.
    Returns deduplicated, structured paper abstracts.

    Args:
        query: Academic search query (paper topic, title keywords, etc.).
        max_results: Maximum results per engine. Default is 5.
    """
    all_results = []
    seen_urls = set()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(_search_arxiv, query, max_results): "arxiv",
            executor.submit(_search_semantic_scholar, query, max_results): "semanticscholar",
        }
        for future in as_completed(futures):
            engine = futures[future]
            try:
                results = future.result()
                for r in results:
                    if r["url"] not in seen_urls:
                        seen_urls.add(r["url"])
                        all_results.append(r)
            except Exception as e:
                logger.warning(f"Academic search engine {engine} failed: {e}")

    if not all_results:
        return json.dumps({"error": "No academic results found", "query": query}, ensure_ascii=False)

    return json.dumps({
        "query": query,
        "total_results": len(all_results),
        "sources": ["arxiv", "semanticscholar"],
        "results": all_results,
    }, indent=2, ensure_ascii=False)
