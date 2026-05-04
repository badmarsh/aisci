import os
import re

SKILLS_DIR = '/home/ubuntu/aisci/agent-skills'
REPORT_PATH = '/home/ubuntu/aisci/docs/ops/agent-skills-audit-report.md'

required_sections = [
    ('Read First', r'##\s*Read First'),
    ('Rules', r'##\s*Rules'),
    ('Workflow', r'##\s*Workflow'),
    ('Output & Approval Gates', r'##\s*Output & Approval Gates')
]

report_lines = []
report_lines.append("# Agent Skills Audit Report\n")
report_lines.append("This report checks all `SKILL.md` files against `TEMPLATE.md` compliance.\n")
report_lines.append("| Skill | YAML `name` | YAML `desc` | Title | Read First | Rules | Workflow | Output & Approval | Notes |")
report_lines.append("|---|---|---|---|---|---|---|---|---|")

for item in sorted(os.listdir(SKILLS_DIR)):
    skill_dir = os.path.join(SKILLS_DIR, item)
    if not os.path.isdir(skill_dir):
        continue
    skill_file = os.path.join(skill_dir, 'SKILL.md')
    if not os.path.isfile(skill_file):
        continue
        
    with open(skill_file, 'r') as f:
        content = f.read()
        
    # Check YAML frontmatter
    yaml_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    has_name = '❌'
    has_desc = '❌'
    if yaml_match:
        yaml_content = yaml_match.group(1)
        if re.search(r'^name:\s*\S+', yaml_content, re.MULTILINE):
            has_name = '✅'
        if re.search(r'^description:\s*\S+', yaml_content, re.MULTILINE):
            has_desc = '✅'
            
    # Check H1 Title
    has_title = '✅' if re.search(r'^#\s+\S+', content, re.MULTILINE) else '❌'
    
    # Check Sections
    checks = []
    for sec_name, sec_regex in required_sections:
        if re.search(sec_regex, content):
            checks.append('✅')
        else:
            checks.append('❌')
            
    notes = []
    if '❌' in checks or has_name == '❌' or has_desc == '❌' or has_title == '❌':
        notes.append("Missing sections")
        
    # Check if AGENTS.md is in Read First
    read_first_block = re.search(r'##\s*Read First(.*?)(?:##|$)', content, re.DOTALL)
    if read_first_block and 'AGENTS.md' not in read_first_block.group(1):
        notes.append("Missing AGENTS.md in Read First")
        
    notes_str = ", ".join(notes) if notes else "Compliant"
    
    report_lines.append(f"| {item} | {has_name} | {has_desc} | {has_title} | {checks[0]} | {checks[1]} | {checks[2]} | {checks[3]} | {notes_str} |")

with open(REPORT_PATH, 'w') as f:
    f.write("\n".join(report_lines) + "\n")
    
print(f"Report written to {REPORT_PATH}")
