import json

def extract_insights(title, abstract, category):
    """
    Simulates extracting structured claims, datasets, and cross-domain insights using an LLM.
    # TODO: Plug in google.generativeai or openai client here.
    """
    insights = {
        "claims": [],
        "datasets": []
    }
    
    # Simple keyword-based mock extraction
    abstract_lower = abstract.lower()
    
    # 1. Look for datasets
    if 'dataset' in abstract_lower or 'data' in abstract_lower:
        if 'atlas' in abstract_lower:
            insights['datasets'].append('ATLAS Open Data')
        elif 'cms' in abstract_lower:
            insights['datasets'].append('CMS Open Data')
        else:
            insights['datasets'].append('Generic arXiv Dataset')
            
    # 2. Look for claims & CS->HEP Bridge applicability
    if 'cs.' in category or 'stat.' in category:
        # It's a computer science paper. Assess applicability to HEP.
        if 'symbolic regression' in abstract_lower:
            insights['claims'].append({
                "text": "Symbolic Regression could be used to derive closed-form expressions for boson pT spectra.",
                "confidence": "HIGH",
                "type": "CS_HEP_BRIDGE"
            })
        elif 'neural network' in abstract_lower or 'deep learning' in abstract_lower:
            insights['claims'].append({
                "text": "Deep Neural Networks could be applied to constrain fits with boundary conditions.",
                "confidence": "MEDIUM",
                "type": "CS_HEP_BRIDGE"
            })
        else:
            insights['claims'].append({
                "text": f"Method from {title} might be applicable to HEP analysis.",
                "confidence": "LOW",
                "type": "CS_HEP_BRIDGE"
            })
    else:
        # It's a physics paper.
        if 'tsallis' in abstract_lower:
            insights['claims'].append({
                "text": "Mentions Tsallis distribution for pT spectra.",
                "confidence": "HIGH",
                "type": "HEP_LITERATURE"
            })
        if 'blast-wave' in abstract_lower:
            insights['claims'].append({
                "text": "Mentions Blast-Wave model.",
                "confidence": "HIGH",
                "type": "HEP_LITERATURE"
            })
        
        # Generic fallback
        if not insights['claims']:
            insights['claims'].append({
                "text": f"Physics paper on: {title[:50]}...",
                "confidence": "MEDIUM",
                "type": "HEP_LITERATURE"
            })
            
    return insights

if __name__ == '__main__':
    # Test
    res = extract_insights("A survey of symbolic regression", "We survey symbolic regression methods.", "cs.LG")
    print(json.dumps(res, indent=2))
