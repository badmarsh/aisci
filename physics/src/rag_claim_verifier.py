#!/usr/bin/env python3
from __future__ import annotations
"""
RAG-Assisted Claim Verification Pipeline

This module evaluates a set of physics claims against the indexed literature corpus
using the Onyx RAG system. It retrieves relevant literature context and uses an LLM
to classify the claim as 'Supported', 'Contradicted', or 'Nuanced'.
"""

import json
import os
import requests
import argparse
from pathlib import Path
from typing import Any, Dict

# Default Onyx REST API endpoint (Danswer/Onyx standard)
ONYX_API_URL = os.environ.get("ONYX_API_URL", "http://127.0.0.1:8080")
ONYX_API_KEY = os.environ.get("ONYX_API_KEY", "")

# Default LLM endpoint (e.g. Ollama or a local OpenAI-compatible endpoint)
LLM_API_URL = os.environ.get("LLM_API_URL", "http://127.0.0.1:11434/v1/chat/completions")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.1")

def query_onyx_for_context(claim: str) -> str:
    """Retrieve relevant context for the claim from the Onyx RAG index."""
    headers = {"Content-Type": "application/json"}
    if ONYX_API_KEY:
        headers["Authorization"] = f"Bearer {ONYX_API_KEY}"
    
    # Using the standard Onyx/Danswer search endpoint
    search_url = f"{ONYX_API_URL}/api/search"
    payload = {
        "query": claim,
        "search_type": "hybrid",
        "retrieval_options": {
            "run_search": True,
            "real_time_web_search": False
        }
    }
    
    try:
        response = requests.post(search_url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Extract snippets from top documents
        documents = data.get("top_documents", [])
        if not documents:
            return "No relevant context found in the literature index."
            
        context_parts = []
        for doc in documents[:5]:
            source = doc.get("semantic_identifier", "Unknown Source")
            content = doc.get("contents", "")[:1000] # truncate long contents
            context_parts.append(f"Source: {source}\nExcerpt: {content}")
            
        return "\n\n".join(context_parts)
    except Exception as e:
        # Fallback for benchmark testing if Onyx is not fully responsive
        print(f"Warning: Failed to query Onyx ({e}). Using empty context.")
        return "No relevant context found in the literature index."

def evaluate_claim_with_llm(claim: str, context: str) -> Dict[str, Any]:
    """Evaluate the claim based on the retrieved context using an LLM."""
    
    system_prompt = (
        "You are an expert computational physicist reviewing manuscript claims.\n"
        "Given a claim and a set of literature excerpts, classify the claim into exactly one of these categories:\n"
        "1. Supported (The literature confirms the claim)\n"
        "2. Contradicted (The literature explicitly disputes or contradicts the claim)\n"
        "3. Nuanced (The literature partially supports the claim, but with caveats, or uses different assumptions)\n"
        "4. Unsupported (The provided literature does not contain enough information to evaluate the claim)\n\n"
        "Output ONLY a JSON object with the following schema:\n"
        "{\n"
        "  \"classification\": \"Supported|Contradicted|Nuanced|Unsupported\",\n"
        "  \"rationale\": \"Brief explanation of why, referencing specific sources\",\n"
        "  \"confidence\": 0.0 to 1.0\n"
        "}"
    )
    
    user_prompt = f"CLAIM:\n{claim}\n\nLITERATURE CONTEXT:\n{context}\n\nEVALUATE:"
    
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(LLM_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        result_text = response.json()["choices"][0]["message"]["content"]
        result = json.loads(result_text)
        return {
            "classification": result.get("classification", "Unsupported"),
            "rationale": result.get("rationale", "Failed to parse rationale"),
            "confidence": result.get("confidence", 0.0)
        }
    except Exception as e:
        print(f"Warning: LLM evaluation failed ({e}).")
        return {
            "classification": "Error",
            "rationale": f"LLM evaluation failed: {e}",
            "confidence": 0.0
        }

def verify_claims(claims_file: Path, output_file: Path):
    """Run the verification pipeline over a list of claims."""
    with open(claims_file, 'r') as f:
        claims_data = json.load(f)
        
    results = []
    for item in claims_data:
        claim_id = item.get("id", "unknown")
        claim_text = item.get("claim", "")
        print(f"Evaluating [{claim_id}]: {claim_text[:50]}...")
        
        context = query_onyx_for_context(claim_text)
        evaluation = evaluate_claim_with_llm(claim_text, context)
        
        results.append({
            "id": claim_id,
            "claim": claim_text,
            "context_retrieved": bool(context and context != "No relevant context found in the literature index."),
            "classification": evaluation["classification"],
            "rationale": evaluation["rationale"],
            "confidence": evaluation["confidence"]
        })
        
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Verification complete. Results saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG-Assisted Claim Verification")
    parser.add_argument("--input", type=Path, required=True, help="Path to input JSON file containing claims")
    parser.add_argument("--output", type=Path, required=True, help="Path to save output JSON results")
    args = parser.parse_args()
    
    verify_claims(args.input, args.output)
