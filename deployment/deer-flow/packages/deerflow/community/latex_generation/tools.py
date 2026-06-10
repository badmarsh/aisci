"""
DeerFlow community tool: latex_generation

Bridges DeerFlow agents to a LaTeX compilation environment within the sandbox.

Tools exposed:
  - latex_init_project   : Scaffold a new poster project by copying a template.
  - latex_update_content : Safely replace or inject content blocks.
  - latex_compile        : Run pdflatex or latexmk.
  - latex_export_pdf     : Move the generated .pdf to the final output directory.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from langchain_core.tools import tool

# ─── constants ────────────────────────────────────────────────────────────────

# Container-side paths
CONTAINER_AISCI = "/mnt/host/aisci"
HOST_AISCI = "/home/ubuntu/aisci"

def _to_host_path(container_path: str) -> str:
    """Convert a container path back to a user-visible host path."""
    return container_path.replace(CONTAINER_AISCI, HOST_AISCI)

def _to_container_path(host_path: str) -> str:
    """Convert a host path to a container-visible path."""
    return host_path.replace(HOST_AISCI, CONTAINER_AISCI)

def _run(cmd: list[str], cwd: str | Path | None = None, timeout: int = 300) -> dict:
    """Run a subprocess and return a structured result dict."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd) if cwd else None,
        )
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Timed out after {timeout}s", "returncode": -1}
    except Exception as exc:
        return {"success": False, "error": str(exc), "returncode": -1}

# ─── tool: latex_init_project ───────────────────────────────────────────────────

@tool
def latex_init_project(
    project_dir_host: str,
    template_path_host: str,
) -> str:
    """
    Scaffold a new poster project by copying a Beamer template.
    
    Args:
        project_dir_host: Absolute host path to the new project workspace.
        template_path_host: Absolute host path to the template .tex file.

    Returns:
        JSON with keys: success, project_path, tex_file_path.
    """
    project_dir = Path(_to_container_path(project_dir_host))
    template_path = Path(_to_container_path(template_path_host))

    if not template_path.exists():
        return json.dumps({
            "success": False,
            "error": f"Template not found at {template_path_host}.",
        })

    try:
        project_dir.mkdir(parents=True, exist_ok=True)
        tex_filename = template_path.name
        dest_tex_path = project_dir / tex_filename
        shutil.copy2(template_path, dest_tex_path)
        
        return json.dumps({
            "success": True,
            "project_path": project_dir_host,
            "tex_file_path": _to_host_path(str(dest_tex_path)),
        })
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})

# ─── tool: latex_update_content ─────────────────────────────────────────────────

@tool
def latex_update_content(
    tex_file_path_host: str,
    target_pattern: str,
    new_content: str,
) -> str:
    """
    Safely replace or inject content blocks into the .tex file using simple string replacement.
    
    Args:
        tex_file_path_host: Absolute host path to the .tex file.
        target_pattern: The exact string block in the .tex file to be replaced.
        new_content: The content to replace the target pattern with.

    Returns:
        JSON with keys: success, file_written.
    """
    tex_path = Path(_to_container_path(tex_file_path_host))
    
    if not tex_path.exists():
        return json.dumps({"success": False, "error": f"File not found: {tex_file_path_host}"})

    try:
        content = tex_path.read_text(encoding="utf-8")
        if target_pattern not in content:
            return json.dumps({"success": False, "error": "Target pattern not found in the file."})
            
        content = content.replace(target_pattern, new_content)
        tex_path.write_text(content, encoding="utf-8")
        
        return json.dumps({
            "success": True,
            "file_written": tex_file_path_host,
        })
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})

# ─── tool: latex_compile ────────────────────────────────────────────────────────

@tool
def latex_compile(
    project_dir_host: str,
    tex_filename: str,
) -> str:
    """
    Run pdflatex inside the project directory, capturing stdout/stderr.
    
    Args:
        project_dir_host: Absolute host path to the project workspace.
        tex_filename: The name of the .tex file to compile.

    Returns:
        JSON with keys: success, returncode, stdout, stderr.
    """
    project_dir = Path(_to_container_path(project_dir_host))
    
    if not project_dir.exists():
        return json.dumps({"success": False, "error": f"Project directory not found: {project_dir_host}"})

    # Run pdflatex non-interactively
    cmd = [
        "pdflatex", 
        "-interaction=nonstopmode",
        "-halt-on-error",
        tex_filename
    ]
    
    return json.dumps(_run(cmd, cwd=project_dir))

# ─── tool: latex_export_pdf ─────────────────────────────────────────────────────

@tool
def latex_export_pdf(
    project_dir_host: str,
    pdf_filename: str,
    output_dir_host: str,
) -> str:
    """
    Move the generated .pdf to the final output directory.
    
    Args:
        project_dir_host: Absolute host path to the project workspace where PDF was compiled.
        pdf_filename: Name of the generated .pdf file.
        output_dir_host: Absolute host path to the final destination directory.

    Returns:
        JSON with keys: success, exported_pdf_path.
    """
    project_dir = Path(_to_container_path(project_dir_host))
    output_dir = Path(_to_container_path(output_dir_host))
    pdf_path = project_dir / pdf_filename
    
    if not pdf_path.exists():
        return json.dumps({"success": False, "error": f"PDF not found at {pdf_path}"})

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        dest_pdf_path = output_dir / pdf_filename
        shutil.copy2(pdf_path, dest_pdf_path)
        
        return json.dumps({
            "success": True,
            "exported_pdf_path": _to_host_path(str(dest_pdf_path)),
        })
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})
