"""
DeerFlow community tool: ppt_generation

Bridges DeerFlow agents to the ppt-master presentation pipeline located at
/mnt/host/aisci/deployment/ppt-master (inside the container).

Tools exposed:
  - ppt_init_project   : Create a new ppt-master project directory.
  - ppt_write_svg      : Write one SVG slide file into a project's svg_output/.
  - ppt_finalize_svg   : Run finalize_svg.py (copies svg_output → svg_final, applies tweaks).
  - ppt_export_pptx    : Run svg_to_pptx.py to produce the final .pptx.
  - ppt_run_step       : Generic step runner for any ppt-master script.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from langchain_core.tools import tool

# ─── constants ────────────────────────────────────────────────────────────────

# Container-side paths (the /mnt/host/aisci mount covers the entire aisci repo)
PPT_MASTER_ROOT = Path("/mnt/host/aisci/deployment/ppt-master")
PPT_MASTER_SCRIPTS = PPT_MASTER_ROOT / "skills" / "ppt-master" / "scripts"
PPT_MASTER_PROJECTS = PPT_MASTER_ROOT / "projects"

# Host-visible path prefix (for return values shown to users)
HOST_AISCI = "/home/ubuntu/aisci"
CONTAINER_AISCI = "/mnt/host/aisci"


def _to_host_path(container_path: str) -> str:
    """Convert a container path back to a user-visible host path."""
    return container_path.replace(CONTAINER_AISCI, HOST_AISCI)


def _run(cmd: list[str], cwd: str | Path | None = None, timeout: int = 300) -> dict:
    """Run a subprocess and return a structured result dict."""
    cwd = str(cwd or PPT_MASTER_ROOT)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
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


# ─── tool: ppt_init_project ───────────────────────────────────────────────────

@tool
def ppt_init_project(
    project_name: str,
    canvas_format: str = "ppt169",
) -> str:
    """
    Create a new ppt-master project directory inside the shared projects folder.

    Args:
        project_name:   Short slug for the project (e.g. "poser_poster_2026").
        canvas_format:  Canvas format string accepted by project_manager.py.
                        Defaults to "ppt169" (16:9, 1280×720 px).

    Returns:
        JSON with keys: success, project_path (host-visible), stdout, stderr.
    """
    if not PPT_MASTER_ROOT.exists():
        return json.dumps({
            "success": False,
            "error": f"ppt-master not found at {PPT_MASTER_ROOT}. "
                     "Make sure the /mnt/host/aisci volume is mounted.",
        })

    script = str(PPT_MASTER_SCRIPTS / "project_manager.py")
    cmd = [
        "python3", script, "init", project_name,
        "--format", canvas_format,
        "--dir", str(PPT_MASTER_PROJECTS),
    ]
    result = _run(cmd)

    # project_manager prints the project path in stdout as "Project created: <path>"
    project_path_container = ""
    for line in result.get("stdout", "").splitlines():
        if line.startswith("Project created:"):
            project_path_container = line.split(":", 1)[1].strip()
            break

    result["project_path"] = _to_host_path(project_path_container) if project_path_container else ""
    result["project_path_container"] = project_path_container
    return json.dumps(result)


# ─── tool: ppt_write_svg ──────────────────────────────────────────────────────

@tool
def ppt_write_svg(
    project_path_container: str,
    slide_number: int,
    svg_content: str,
) -> str:
    """
    Write a single SVG slide into a ppt-master project's svg_output/ directory.

    Args:
        project_path_container: Absolute container path to the project
                                (e.g. "/mnt/host/aisci/deployment/ppt-master/projects/...").
        slide_number:           1-based slide index (→ written as slide_001.svg etc.).
        svg_content:            Full SVG XML string to write.

    Returns:
        JSON with keys: success, file_written (host path).
    """
    project = Path(project_path_container)
    svg_dir = project / "svg_output"

    if not project.exists():
        return json.dumps({"success": False, "error": f"Project not found: {project_path_container}"})

    svg_dir.mkdir(exist_ok=True)
    filename = f"slide_{slide_number:03d}.svg"
    dest = svg_dir / filename

    try:
        dest.write_text(svg_content, encoding="utf-8")
        return json.dumps({
            "success": True,
            "file_written": _to_host_path(str(dest)),
        })
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


# ─── tool: ppt_finalize_svg ───────────────────────────────────────────────────

@tool
def ppt_finalize_svg(project_path_container: str) -> str:
    """
    Run the ppt-master finalize_svg.py post-processor on a project.

    This copies SVG files from svg_output/ → svg_final/, resolves asset paths,
    and applies any pending annotation fixes.

    Args:
        project_path_container: Absolute container path to the project.

    Returns:
        JSON with keys: success, stdout, stderr.
    """
    project = Path(project_path_container)
    if not project.exists():
        return json.dumps({"success": False, "error": f"Project not found: {project_path_container}"})

    script = str(PPT_MASTER_SCRIPTS / "finalize_svg.py")
    cmd = ["python3", script, str(project)]
    return json.dumps(_run(cmd))


# ─── tool: ppt_export_pptx ────────────────────────────────────────────────────

@tool
def ppt_export_pptx(project_path_container: str) -> str:
    """
    Convert a finalized ppt-master project into a .pptx file.

    Runs svg_to_pptx.py which reads svg_final/ and writes a .pptx into exports/.

    Args:
        project_path_container: Absolute container path to the project.

    Returns:
        JSON with keys: success, pptx_path (host-visible), stdout, stderr.
    """
    project = Path(project_path_container)
    if not project.exists():
        return json.dumps({"success": False, "error": f"Project not found: {project_path_container}"})

    script = str(PPT_MASTER_SCRIPTS / "svg_to_pptx.py")
    cmd = ["python3", script, str(project)]
    result = _run(cmd, timeout=600)

    # Find the exported .pptx
    exports_dir = project / "exports"
    pptx_files = sorted(exports_dir.glob("*.pptx")) if exports_dir.exists() else []
    if pptx_files:
        result["pptx_path"] = _to_host_path(str(pptx_files[-1]))
    else:
        result["pptx_path"] = ""

    return json.dumps(result)


# ─── tool: ppt_run_step ───────────────────────────────────────────────────────

@tool
def ppt_run_step(
    script_name: str,
    project_path_container: str,
    extra_args: Optional[str] = None,
) -> str:
    """
    Run any ppt-master post-processing script by name for a given project.

    Allowed script names:
        total_md_split, finalize_svg, svg_to_pptx, svg_quality_checker,
        analyze_images, batch_validate, pptx_animations

    Args:
        script_name:            Name of the script (without .py extension).
        project_path_container: Absolute container path to the project.
        extra_args:             Optional additional CLI arguments as a space-separated string.

    Returns:
        JSON with keys: success, returncode, stdout, stderr.
    """
    ALLOWED = {
        "total_md_split", "finalize_svg", "svg_to_pptx",
        "svg_quality_checker", "analyze_images", "batch_validate",
        "pptx_animations",
    }
    if script_name not in ALLOWED:
        return json.dumps({
            "success": False,
            "error": f"Script '{script_name}' is not in allowed list: {sorted(ALLOWED)}",
        })

    project = Path(project_path_container)
    if not project.exists():
        return json.dumps({"success": False, "error": f"Project not found: {project_path_container}"})

    script = str(PPT_MASTER_SCRIPTS / f"{script_name}.py")
    cmd = ["python3", script, str(project)]
    if extra_args:
        cmd.extend(extra_args.split())

    return json.dumps(_run(cmd, timeout=600))
