import os
import glob

skills = glob.glob('agent-skills/*/SKILL.md')
expected_headers = ['## Read First', '## Rules', '## Workflow', '## Output & Approval Gates']

for skill in skills:
    with open(skill, 'r') as f:
        content = f.read()
        missing = [h for h in expected_headers if h not in content]
        if missing:
            print(f"{skill} is missing: {missing}")

print("Check complete.")
