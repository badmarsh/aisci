"""
DeerFlow community tool: report_proofreading

Provides tools for the `report-proofreader` agent to check grammar and citations.
"""
import json
import re
from pathlib import Path
from langchain_core.tools import tool

@tool
def citation_validator(document_path_container: str, bib_path_container: str) -> str:
    """
    Validates that all citations in a document exist in the .bib file.
    
    Args:
        document_path_container: Absolute container path to the .tex or .md file.
        bib_path_container: Absolute container path to the .bib file.
        
    Returns:
        JSON string containing missing citations.
    """
    doc_path = Path(document_path_container)
    bib_path = Path(bib_path_container)
    
    if not doc_path.exists():
        return json.dumps({"success": False, "error": f"Document not found: {document_path_container}"})
    if not bib_path.exists():
        return json.dumps({"success": False, "error": f"Bib file not found: {bib_path_container}"})
        
    try:
        doc_text = doc_path.read_text(encoding="utf-8")
        bib_text = bib_path.read_text(encoding="utf-8")
        
        # Find citations in text: \cite{key1,key2} or [@key]
        latex_cites = re.findall(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}', doc_text)
        md_cites = re.findall(r'\[@([^\]]+)\]', doc_text)
        
        cited_keys = set()
        for c in latex_cites:
            cited_keys.update([k.strip() for k in c.split(',')])
        cited_keys.update(md_cites)
        
        # Find defined keys in bib file
        bib_keys = set(re.findall(r'@\w+\{([^,]+),', bib_text))
        
        missing_keys = cited_keys - bib_keys
        
        return json.dumps({
            "success": True,
            "total_citations": len(cited_keys),
            "missing_citations": list(missing_keys)
        })
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})

@tool
def scientific_grammar_check(text: str) -> str:
    """
    A simple rule-based grammar and style checker for scientific text.
    In a real scenario, this might call an external API (like LanguageTool) or an LLM.
    
    Args:
        text: The text to check.
        
    Returns:
        JSON string with style suggestions.
    """
    suggestions = []
    
    # Very basic passive voice check
    passive_regex = re.compile(r'\b(am|is|are|was|were|be|been|being)\s+\w+ed\b', re.IGNORECASE)
    for match in passive_regex.finditer(text):
        suggestions.append(f"Consider rewriting passive voice: '{match.group()}'")
        
    # Check for informal words
    informal = ["really", "very", "a lot", "huge", "tiny"]
    for word in informal:
        if re.search(r'\b' + word + r'\b', text, re.IGNORECASE):
            suggestions.append(f"Consider replacing informal word '{word}' with a more precise term.")
            
    return json.dumps({
        "success": True,
        "suggestions": suggestions[:10] # Return top 10
    })
