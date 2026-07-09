import json
import urllib.request
import urllib.parse
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from database import get_connection as get_db

def log_activity(action, user, details):
    conn = get_db()
    from datetime import datetime
    conn.execute("INSERT INTO ActivityLogs (timestamp, action, user, details) VALUES (?, ?, ?, ?)",
                 (datetime.now().isoformat() + "Z", action, user, details))
    conn.commit()
    conn.close()

def extract_insights(title, abstract, category):
    insights = {
        "claims": [],
        "datasets": []
    }
    
    # Try OpenRouter
    prompt = f"""
    Analyze the following scientific paper.
    Title: {title}
    Abstract: {abstract}
    Category: {category}
    
    Extract key scientific claims and any datasets used. Return pure JSON format:
    {{
      "claims": [
        {{"text": "Claim description", "confidence": "HIGH/MEDIUM/LOW", "type": "HEP_LITERATURE or CS_HEP_BRIDGE"}}
      ],
      "datasets": ["Dataset Name"]
    }}
    IMPORTANT: Ensure all LaTeX commands in the JSON strings are properly double-escaped (e.g. \\\\alpha instead of \\alpha).
    Do not output markdown code blocks or explanations, just the JSON.
    """
    
    import time
    import re
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                'https://openrouter.ai/api/v1/chat/completions',
                data=json.dumps({
                    "model": "openai/gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}]
                }).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {os.environ.get("OPENROUTER_API_KEY", "")}'
                },
                method='POST'
            )
            response = urllib.request.urlopen(req, timeout=30)
            data = json.loads(response.read())
            resp_text = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            
            # Strip markdown formatting if any
            resp_text = resp_text.strip()
            if resp_text.startswith("```json"):
                resp_text = resp_text[7:]
            elif resp_text.startswith("```"):
                resp_text = resp_text[3:]
            if resp_text.endswith("```"):
                resp_text = resp_text[:-3]
            resp_text = resp_text.strip()
            
            # Fix unescaped backslashes (e.g., \to, \pi) which are common in LaTeX
            # This regex finds a backslash that is not followed by a valid JSON escape char
            resp_text = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', resp_text)
                
            parsed = json.loads(resp_text)
            insights['claims'] = parsed.get("claims", [])
            insights['datasets'] = parsed.get("datasets", [])
            
            # Log successful LLM
            try:
                log_activity("OpenRouter Extraction", "AI", f"Successfully extracted {len(insights['claims'])} claims using OpenRouter.")
            except:
                pass
                
            return insights
            
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(10)  # Wait 10 seconds before retrying
                continue
            err_body = e.read().decode('utf-8')
            try:
                log_activity("OpenRouter Failed", "AI", f"Fallback activated. HTTP Error {e.code}: {err_body}")
            except:
                pass
            print(f"OpenRouter extraction failed: HTTP Error {e.code}: {err_body}. Falling back to keywords.")
            break
        except Exception as e:
            # Fallback to mock on connection error or parse error
            try:
                log_activity("OpenRouter Failed", "AI", f"Fallback activated. Error: {str(e)}")
            except:
                pass
            print(f"OpenRouter extraction failed: {e}. Falling back to keywords.")
            break
    
    abstract_lower = abstract.lower()
    
    if 'dataset' in abstract_lower or 'data' in abstract_lower:
        if 'atlas' in abstract_lower:
            insights['datasets'].append('ATLAS Open Data')
        elif 'cms' in abstract_lower:
            insights['datasets'].append('CMS Open Data')
        else:
            insights['datasets'].append('Generic arXiv Dataset')
            
    if 'cs.' in category or 'stat.' in category:
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
