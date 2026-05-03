import os
import httpx
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class OnyxConnector:
    """
    DeerFlow Connector for Onyx Knowledge Base.
    Supports document ingestion and retrieval.
    """
    def __init__(self, api_base: Optional[str] = None, api_key: Optional[str] = None):
        self.api_base = api_base or os.environ.get("ONYX_API_BASE", "http://host.docker.internal:80/api")
        self.api_key = api_key or os.environ.get("ONYX_API_KEY")
        
        if not self.api_key:
            raise ValueError("ONYX_API_KEY must be provided or set in environment")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def ingest_document(self, title: str, content: str, source_link: str = "") -> Dict[str, Any]:
        """
        Ingest a single document into Onyx.
        Note: Onyx usually uses connectors (file, web, etc.), 
        but we can use the internal ingestion API if available.
        """
        url = f"{self.api_base.rstrip('/')}/ingest/document"
        payload = {
            "title": title,
            "content": content,
            "link": source_link
        }
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to ingest document into Onyx: {e}")
            return {"error": str(e)}

    def search(self, query: str, num_hits: int = 5) -> List[Dict[str, Any]]:
        """
        Search the Onyx knowledge base.
        """
        url = f"{self.api_base.rstrip('/')}/search/send-search-message"
        payload = {
            "search_query": query,
            "num_hits": num_hits,
            "include_content": True,
            "stream": False
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json().get("documents", [])
        except Exception as e:
            logger.error(f"Onyx Search failed: {e}")
            return []

if __name__ == "__main__":
    # Quick sanity check
    connector = OnyxConnector()
    print(f"OnyxConnector initialized at {connector.api_base}")
