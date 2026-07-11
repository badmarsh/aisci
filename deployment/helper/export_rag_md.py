from __future__ import annotations
import json
import os

json_file = "/home/ubuntu/aisci/docs/ops/rag-baselines/rag-baseline-2026-06-04T18-56-55Z-persona-2-post-v4-qwen-balanced-128k-final-recreate.json"
output_md = "/home/ubuntu/aisci/docs/ops/rag-baselines/rag-128k-final-results.md"

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

md_lines = []
md_lines.append("# RAG Baseline Tests: 128k Context Run\n")
md_lines.append("This document exports the exact queries, metadata, and responses from the fully-enabled 128k context RAG test using `qwen-rag-balanced`.\n")

for q in data.get("results", []):
    md_lines.append(f"## {q.get('id', 'Unknown ID')}: {q.get('topic', 'Unknown Topic')}\n")
    md_lines.append(f"**What is tested and why:** This tests the model's ability to retrieve and synthesize information regarding '{q.get('topic')}'. With the expanded 128k context, it tests if the model can parse up to 10 dense PDF chunks without hitting token limits.\n")
    md_lines.append(f"**Prompt (Question):**\n> {q.get('question', '')}\n")
    md_lines.append(f"**Response:**\n```text\n{q.get('answer', 'NO ANSWER GENERATED')}\n```\n")
    md_lines.append("---\n")

with open(output_md, 'w', encoding='utf-8') as f:
    f.write("\n".join(md_lines))

print(f"Exported to {output_md}")
