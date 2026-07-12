import os
import glob

files = [
    "mcp-endpoints.md",
    "mcp-hep-servers.md",
    "rag-evaluation-results.md",
    "rag-evaluation-set.md",
    "model-optimization-report.md",
    "model-selection-guide.md",
    "activepieces-integration.md",
    "k-dense-skills-reference.md",
    "kdense-agent-skills.md",
    "literature-corpus-policy.md",
    "semantic-scholar-asta-api.md",
    "subtree-management.md",
]

prefix = "> Historical record only — not active operational guidance.\n\n"

for f in files:
    path = f"docs/ops/{f}"
    if not os.path.exists(path): continue
    
    with open(path, 'r') as file:
        content = file.read()
    
    # Check if already has the prefix
    if "> Historical record only — not active operational guidance." in content:
        continue
    
    # Add after the first heading
    lines = content.split('\n')
    if len(lines) > 0 and lines[0].startswith('# '):
        lines.insert(1, "\n" + prefix.strip())
        with open(path, 'w') as file:
            file.write('\n'.join(lines))
        print(f"Updated {f}")
