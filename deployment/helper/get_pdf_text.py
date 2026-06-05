import os
import sys

# Need to set PYTHONPATH for the backend
sys.path.append("/app")

import asyncio
from onyx.document_index.factory import get_default_document_index
from onyx.db.engine import build_connection_pool
from onyx.utils.logger import setup_logger

async def main():
    logger = setup_logger()
    try:
        index = get_default_document_index(None, None)
        docs = index.id_based_retrieval(['FILE_CONNECTOR__29fb0bcf-0f89-49b0-8586-126d4bc21e2f'])
        if not docs:
            print("Document not found in index")
            return
            
        doc = docs[0]
        print(f"TITLE: {doc.semantic_identifier}")
        print(f"URL: {doc.source_links}")
        print(f"METADATA: {doc.metadata}")
        
        # Depending on chunk structure, text is usually in 'contents' or 'chunks'
        if hasattr(doc, 'contents'):
            print(f"CONTENT PREVIEW:\n{doc.contents[:1000]}")
        else:
            print("No contents attribute on doc")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
