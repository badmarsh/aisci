import os
from dotenv import load_dotenv

# Load env vars
load_dotenv("/home/ubuntu/aisci/deployment/onyx/.env")

import sys
sys.path.append("/home/ubuntu/aisci/deployment/deer-flow/backend/packages/harness")

try:
    from deerflow.community.browser_agent.tools import browser_agent_tool
    
    print("Executing browser agent. This may take a few moments...")
    result = browser_agent_tool.invoke({"task": "Go to example.com and extract the main heading text."})
    
    print("Browser Agent Result:")
    print(result)
except Exception as e:
    print(f"Test failed: {e}")
