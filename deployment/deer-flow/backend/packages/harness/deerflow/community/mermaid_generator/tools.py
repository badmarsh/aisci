"""Mermaid Diagram Generator Tool — generate architecture, flow, and data diagrams as Mermaid code."""

import json
import logging

from langchain.tools import tool

logger = logging.getLogger(__name__)


@tool("generate_mermaid", parse_docstring=True)
def mermaid_generator_tool(
    diagram_type: str,
    title: str,
    description: str,
    nodes: list[dict],
    edges: list[dict] | None = None,
) -> str:
    """Generate a Mermaid diagram as markdown code. Use this for architecture diagrams, flowcharts, sequence diagrams, and data flow visualizations in reports.

    Args:
        diagram_type: Type of diagram. Options: "flowchart", "sequence", "class", "state", "er", "gantt", "pie".
        title: Title for the diagram.
        description: Brief description of what the diagram shows.
        nodes: List of node definitions. Each dict: {"id": "A", "label": "Component Name", "style": "fill:#f9f"}.
        edges: Optional list of edge definitions. Each dict: {"from": "A", "to": "B", "label": "connects to"}.
    """
    try:
        lines = [f"%% {title}", f"%% {description}", ""]

        if diagram_type == "flowchart":
            lines.append("graph TD")
            for node in nodes:
                style = f":::{node['id'].lower()}" if "style" in node else ""
                lines.append(f"    {node['id']}[\"{node['label']}\"]{style}")
            if edges:
                for edge in edges:
                    label = f" -- {edge['label']} -->" if edge.get("label") else " -->"
                    lines.append(f"    {edge['from']}{label} {edge['to']}")
        elif diagram_type == "sequence":
            lines.append("sequenceDiagram")
            for node in nodes:
                lines.append(f"    participant {node['id']} as {node['label']}")
            if edges:
                for edge in edges:
                    arrow = edge.get("label", "->>") or "->>"
                    lines.append(f"    {edge['from']} {arrow} {edge['to']}: {edge.get('message', '')}")
        elif diagram_type == "er":
            lines.append("erDiagram")
            for node in nodes:
                fields = node.get("fields", [])
                field_lines = [f"        {f.get('type', 'string')} {f.get('name', 'field')}" for f in fields]
                lines.append(f"    {node['label']} {{")
                lines.extend(field_lines)
                lines.append("    }")
            if edges:
                for edge in edges:
                    rel = edge.get("label", "") or "||--o{"
                    lines.append(f"    {edge['from']} {rel} {edge['to']}")
        elif diagram_type == "state":
            lines.append("stateDiagram-v2")
            for node in nodes:
                lines.append(f"    state \"{node['label']}\" as {node['id']}")
            if edges:
                for edge in edges:
                    lines.append(f"    {edge['from']} --> {edge['to']}: {edge.get('label', '')}")
        elif diagram_type == "gantt":
            lines.append("gantt")
            lines.append("    title " + title)
            lines.append("    dateFormat  YYYY-MM-DD")
            for node in nodes:
                start = node.get("start", "2026-01-01")
                end = node.get("end", "2026-01-07")
                lines.append(f"    section {node.get('section', 'Tasks')}")
                lines.append(f"    {node['label']} :{start}, {end}")
        elif diagram_type == "pie":
            lines.append("pie title " + title)
            for node in nodes:
                val = node.get("value", 1)
                lines.append(f"    \"{node['label']}\" : {val}")
        else:
            return json.dumps({"error": f"Unknown diagram type: {diagram_type}. Options: flowchart, sequence, class, state, er, gantt, pie"}, ensure_ascii=False)

        mermaid_code = "\n".join(lines)
        return json.dumps({
            "title": title,
            "type": diagram_type,
            "mermaid": mermaid_code,
            "usage": "Embed in markdown as:\n```mermaid\n" + mermaid_code + "\n```",
        }, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Mermaid generation failed: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)
