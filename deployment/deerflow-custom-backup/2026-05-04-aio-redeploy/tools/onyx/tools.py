import json
import logging
import os
import httpx
from langchain.tools import tool
from deerflow.config import get_app_config

logger = logging.getLogger(__name__)

def _search_onyx(
    query: str,
    num_hits: int = 5,
) -> dict:
    """
    Execute search using Onyx REST API (Sync).
    """
    api_key = os.environ.get("ONYX_API_KEY")
    api_base = os.environ.get("ONYX_API_BASE", "http://host.docker.internal:80/api")
    
    if not api_key:
        logger.error("ONYX_API_KEY not found in environment")
        return {"error": "ONYX_API_KEY not configured"}

    url = f"{api_base.rstrip('/')}/search/send-search-message"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "search_query": query,
        "num_hits": num_hits,
        "include_content": True,
        "stream": False
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Failed to search Onyx: {e}")
        return {"error": str(e)}

@tool("onyx_search", parse_docstring=True)
def onyx_search_tool(
    query: str,
) -> str:
    """Search the internal Onyx knowledge base for physics research, experimental data, and scientific literature.
    Use this tool to find information grounded in the repository's indexed documents, such as Tsallis statistics, Blast-Wave fits, and ALICE/CMS experimental results.

    Args:
        query: Search keywords describing the physics concept or data you want to retrieve.
    """
    num_hits = 5
    config = get_app_config().get_tool_config("onyx_search")

    # Override num_hits from config if set
    if config is not None and "num_hits" in config.model_extra:
        num_hits = config.model_extra.get("num_hits", num_hits)

    results_raw = _search_onyx(
        query=query,
        num_hits=num_hits,
    )

    if "error" in results_raw:
        return json.dumps(results_raw, ensure_ascii=False)

    documents = results_raw.get("documents", [])
    if not documents:
        return json.dumps({"error": "No documents found in Onyx for this query", "query": query}, ensure_ascii=False)

    normalized_results = [
        {
            "title": doc.get("semantic_identifier", "Unknown Document"),
            "content": doc.get("blurb", ""),
            "source_type": doc.get("source_type", "unknown"),
            "link": doc.get("link", ""),
            "metadata": doc.get("metadata", {})
        }
        for doc in documents
    ]

    output = {
        "query": query,
        "total_hits": len(normalized_results),
        "results": normalized_results,
    }

    return json.dumps(output, indent=2, ensure_ascii=False)
