import os
import json
import subprocess
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any

studio_router = APIRouter(prefix="/api/studio")

# Directory to save Canvas states per paper
CANVAS_STATE_DIR = os.path.join(os.path.dirname(__file__), "..", ".canvas_states")
os.makedirs(CANVAS_STATE_DIR, exist_ok=True)

@studio_router.get("/papers/{paper_id}/canvas")
def get_canvas_state(paper_id: str):
    file_path = os.path.join(CANVAS_STATE_DIR, f"{paper_id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {"nodes": [], "edges": []}

@studio_router.post("/papers/{paper_id}/canvas")
def save_canvas_state(paper_id: str, state: Dict[str, Any] = Body(...)):
    file_path = os.path.join(CANVAS_STATE_DIR, f"{paper_id}.json")
    with open(file_path, "w") as f:
        json.dump(state, f)
    return {"status": "success"}

import re

def _calculate_affordance(abstract: str) -> str:
    abstract = abstract.lower()
    if any(k in abstract for k in ["monte carlo", "simulation", "cfd"]):
        return "Simulation-testable"
    if any(k in abstract for k in ["theorem", "proof", "formal", "complexity", "lemma"]):
        return "Formally provable"
    return "Data-analytic"

def _calculate_provability(abstract: str) -> int:
    score = 50
    abstract = abstract.lower()
    if "data" in abstract: score += 10
    if "open source" in abstract or "github" in abstract: score += 20
    if "tsallis" in abstract: score += 15
    return min(100, score)

def _get_heuristics(abstract: str) -> dict:
    abstract = abstract.lower()
    return {
        "no_chi2": "chi2" not in abstract and "chi-square" not in abstract,
        "cs_heavy": "neural network" in abstract or "machine learning" in abstract,
        "no_formal_proof": "proof" not in abstract
    }

@studio_router.post("/discover")
def run_discovery(query: str = Body(..., embed=True)):
    """
    Invokes LDR (agy) to find candidate papers with weak CS heuristics.
    """
    try:
        prompt = f"Find 3 papers related to '{query}'. Output strictly in JSON format matching this schema: [{{\"id\": \"arxiv-...\", \"title\": \"...\", \"authors\": \"...\", \"category\": \"...\", \"abstract\": \"...\"}}]. Do not include any other text."
        
        result = subprocess.run(
            ["agy", "-p", prompt], 
            capture_output=True, 
            text=True, 
            cwd="/home/ubuntu/local-deep-research"
        )
        
        raw_out = result.stdout.strip()
        json_str = raw_out
        
        match = re.search(r'```json\s*(.*?)\s*```', raw_out, re.DOTALL)
        if match:
            json_str = match.group(1)
        elif '```' in raw_out:
            match = re.search(r'```\s*(.*?)\s*```', raw_out, re.DOTALL)
            if match:
                json_str = match.group(1)
        
        try:
            papers_data = json.loads(json_str)
        except json.JSONDecodeError:
            print("Failed to parse LDR JSON:", json_str)
            papers_data = []

        papers = []
        for p in papers_data:
            abstract = p.get("abstract", "")
            paper = {
                "id": p.get("id", "unknown"),
                "title": p.get("title", "Unknown Title"),
                "authors": p.get("authors", "Unknown"),
                "category": p.get("category", "physics"),
                "affordance": _calculate_affordance(abstract),
                "heuristics": _get_heuristics(abstract),
                "provabilityScore": _calculate_provability(abstract),
                "summary": abstract[:150] + "..." if len(abstract) > 150 else abstract
            }
            papers.append(paper)

        return {
            "status": "success",
            "papers": papers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
