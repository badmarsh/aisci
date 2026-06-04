import json

from firecrawl import FirecrawlApp
from langchain.tools import tool

from deerflow.config import get_app_config


def _get_firecrawl_client(tool_name: str = "web_search") -> FirecrawlApp:
    config = get_app_config().get_tool_config(tool_name)
    api_key = None
    if config is not None and "api_key" in config.model_extra:
        api_key = config.model_extra.get("api_key")
    return FirecrawlApp(api_key=api_key)  # type: ignore[arg-type]


@tool("firecrawl_search", parse_docstring=True)
def firecrawl_search_tool(query: str) -> str:
    """Search the web using Firecrawl.

    Args:
        query: The query to search for.
    """
    try:
        config = get_app_config().get_tool_config("web_search")
        max_results = 5
        if config is not None:
            max_results = config.model_extra.get("max_results", max_results)

        client = _get_firecrawl_client("web_search")
        result = client.search(query, params={"limit": max_results})

        # result['data'] contains list of results in newer firecrawl-py versions
        if isinstance(result, dict) and "data" in result:
            web_results = result["data"]
        else:
            web_results = getattr(result, "web", []) or []

        normalized_results = [
            {
                "title": item.get("title", "") if isinstance(item, dict) else getattr(item, "title", "") or "",
                "url": item.get("url", "") if isinstance(item, dict) else getattr(item, "url", "") or "",
                "snippet": item.get("description", "") if isinstance(item, dict) else getattr(item, "description", "") or "",
            }
            for item in web_results
        ]
        json_results = json.dumps(normalized_results, indent=2, ensure_ascii=False)
        return json_results
    except Exception as e:
        return f"Error: {str(e)}"


@tool("firecrawl_scrape", parse_docstring=True)
def firecrawl_scrape_tool(url: str) -> str:
    """Fetch the contents of a web page at a given URL using Firecrawl.
    Only fetch EXACT URLs that have been provided directly by the user or have been returned in results from the search tools.

    Args:
        url: The URL to fetch the contents of.
    """
    try:
        client = _get_firecrawl_client("web_fetch")
        result = client.scrape_url(url, params={"formats": ["markdown"]})

        if isinstance(result, dict):
            markdown_content = result.get("markdown", "")
            metadata = result.get("metadata", {})
            title = metadata.get("title", "Untitled")
        else:
            markdown_content = getattr(result, "markdown", "")
            metadata = getattr(result, "metadata", None)
            title = metadata.title if metadata and hasattr(metadata, "title") else "Untitled"

        if not markdown_content:
            return "Error: No content found"
    except Exception as e:
        return f"Error: {str(e)}"

    return f"# {title}\n\n{markdown_content[:4096]}"


@tool("firecrawl_crawl", parse_docstring=True)
def firecrawl_crawl_tool(url: str) -> str:
    """Crawl a website starting from a given URL using Firecrawl.

    Args:
        url: The starting URL to crawl.
    """
    try:
        client = _get_firecrawl_client("web_fetch")
        # In v2, crawl is often async and returns a job ID or similar
        # For simplicity in this tool, we might just start it or return a message
        result = client.crawl_url(url, params={"limit": 10, "scrapeOptions": {"formats": ["markdown"]}})
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@tool("firecrawl_map", parse_docstring=True)
def firecrawl_map_tool(url: str) -> str:
    """Map a website to get a list of URLs using Firecrawl.

    Args:
        url: The URL to map.
    """
    try:
        client = _get_firecrawl_client("web_fetch")
        result = client.map_url(url)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@tool("firecrawl_extract", parse_docstring=True)
def firecrawl_extract_tool(urls: list[str], prompt: str) -> str:
    """Extract structured data from a list of URLs using Firecrawl.

    Args:
        urls: List of URLs to extract data from.
        prompt: The prompt describing what to extract.
    """
    try:
        client = _get_firecrawl_client("web_fetch")
        result = client.extract(urls, {"prompt": prompt})
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"
