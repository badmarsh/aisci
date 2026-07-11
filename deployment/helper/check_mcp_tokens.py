from __future__ import annotations
import os
import sys

def check_tokens():
    env_paths = ["deployment/onyx/.env", "deployment/onyx/.env.local"]
    tokens = {
        "CONSENSUS_MCP_BEARER_TOKEN": None,
        "SCITE_MCP_BEARER_TOKEN": None
    }
    
    for path in env_paths:
        if os.path.exists(path):
            with open(path, "r") as f:
                for line in f:
                    for token_name in tokens:
                        if line.startswith(f"{token_name}="):
                            value = line.split("=", 1)[1].strip().strip("'").strip('"')
                            if value:
                                tokens[token_name] = value
    
    missing = [name for name, val in tokens.items() if not val]
    
    if missing:
        print(f"WARNING: The following MCP tokens are missing or empty: {', '.join(missing)}")
        print("Literature search tools (Scite/Consensus) will return 401 Unauthorized.")
        print("Please complete the OAuth flows documented in docs/ops/mcp-oauth-flows.md.")
    else:
        print("SUCCESS: All MCP literature tokens are present.")

if __name__ == "__main__":
    check_tokens()
