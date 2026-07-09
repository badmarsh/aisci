import os
from datetime import datetime

LEDGER_PATH = "/home/ubuntu/aisci/research/robert/evidence-ledger.md"

def update_evidence_ledger(paper_data: dict, extraction: dict):
    """
    Appends a new paper's extraction to the evidence ledger.
    """
    if not os.path.exists(LEDGER_PATH):
        print(f"Ledger not found at {LEDGER_PATH}")
        return
        
    with open(LEDGER_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check if section exists
    section_header = "## 🤖 Agent-Proposed Intake"
    if section_header not in content:
        content += f"\n\n---\n\n{section_header}\n\n"
        content += "| Claim | Evidence Required | Current Evidence | Status | Next Gate |\n"
        content += "|-------|-------------------|------------------|--------|-----------|\n"
        
    # Combine claims for display
    claims_str = " ".join(extraction.get("claims", []))
    claim_cell = f"**{paper_data['title']}**<br>{claims_str}"
    
    methods_str = ", ".join(extraction.get("methods", []))
    datasets_str = ", ".join(extraction.get("datasets", []))
    evidence_req_cell = f"Methods: {methods_str}<br>Datasets: {datasets_str}"
    
    limitations_str = ", ".join(extraction.get("limitations", []))
    current_evidence_cell = f"Limitations: {limitations_str}<br>DOI: {paper_data['doi']}"
    
    status_cell = extraction.get("score_category", "Unknown")
    next_gate_cell = extraction.get("score_reason", "Review needed")
    
    # Sanitize pipes and newlines
    def sanitize(text):
        return str(text).replace("|", "\\|").replace("\n", " ").strip()
        
    row = f"| {sanitize(claim_cell)} | {sanitize(evidence_req_cell)} | {sanitize(current_evidence_cell)} | {sanitize(status_cell)} | {sanitize(next_gate_cell)} |\n"
    
    # Simple append logic: just add it to the end of the file. 
    # Since we add the section header at the very bottom if missing, 
    # we can safely assume appending to the end keeps it in the table.
    
    with open(LEDGER_PATH, 'a', encoding='utf-8') as f:
        # If the file didn't have the section, we need to rewrite to ensure the section is added
        pass
        
    if section_header not in content[:-len(row)-200]:
        # Just write the whole modified content if we added the section header
        with open(LEDGER_PATH, 'w', encoding='utf-8') as f:
            if not content.endswith('\n'):
                content += "\n"
            f.write(content + row)
    else:
        # If section already existed, maybe we just append to the end. But the table might not be at the very end of the file.
        # Actually, let's just do a string replacement right after the section header table definition
        table_header = "|-------|-------------------|------------------|--------|-----------|\n"
        # Find the last occurrence of the table header
        idx = content.rfind(table_header)
        if idx != -1:
            insert_pos = idx + len(table_header)
            new_content = content[:insert_pos] + row + content[insert_pos:]
            with open(LEDGER_PATH, 'w', encoding='utf-8') as f:
                f.write(new_content)
        else:
            with open(LEDGER_PATH, 'a', encoding='utf-8') as f:
                f.write(row)

if __name__ == "__main__":
    # Test
    update_evidence_ledger({"title": "Test Paper", "doi": "10.123/456"}, {"claims": ["C1"], "score_category": "Confirms"})
