import os
import json
import requests

def extract_paper_claims(title: str, abstract: str, doi: str) -> dict:
    """
    Extracts claims, methods, datasets, limitations, and scores the paper 
    against AiSci's beliefs using an LLM.
    """
    prompt = f"""
    You are AiSci's literature intake analyzer.
    Analyze the following physics paper:
    Title: {title}
    Abstract: {abstract}
    DOI: {doi}
    
    Extract the following into a strictly valid JSON object:
    - "claims": [list of string claims]
    - "methods": [list of string methods]
    - "datasets": [list of string datasets mentioned]
    - "limitations": [list of string limitations]
    - "score_category": one of ["Confirms", "Contradicts", "Opens new line"]
    - "score_reason": A short string explaining why it fits the category.
    
    Treat contradictions to standard Blast-Wave, Tsallis, or Juttner fits in high-multiplicity pp collisions as most valuable.
    Return ONLY JSON.
    """
    
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
    model_name = os.environ.get("OLLAMA_MODEL", "gemma2:27b")
    
    try:
        resp = requests.post(
            ollama_url,
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=15
        )
        resp.raise_for_status()
        data = resp.json()
        result_text = data.get("response", "{}")
        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            # Attempt to strip markdown code blocks if the LLM returned any
            clean_text = result_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
            
    except Exception as e:
        print(f"LLM API failed ({e}). Returning fallback extraction for pipeline testing.")
        # Fallback mechanism so the pipeline is fully testable even if Ollama is down
        return {
            "claims": [f"Extracted claim from {title}"],
            "methods": ["Automated Extraction Fallback"],
            "datasets": ["Unknown Dataset"],
            "limitations": ["Abstract-only extraction due to API failure"],
            "score_category": "Opens new line",
            "score_reason": "Fallback categorization due to LLM unavailability."
        }
