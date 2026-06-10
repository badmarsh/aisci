"""
POSER Pipeline tool.

Wraps the physical physics scripts execution inside the sandbox
and returns structured JSON.
"""
import os
import subprocess
import json
from typing import Dict, Any, Optional

def poser_run_tool(
    script_path: str,
    pdf_path: Optional[str] = None,
    run_dir: Optional[str] = None
) -> str:
    """
    Run a physics script inside the DeerFlow sandbox.

    Args:
        script_path: Absolute path to the physics script (e.g. /mnt/host/aisci/physics/src/data_loader.py)
        pdf_path: Optional path to manuscript PDF
        run_dir: Optional path to run directory for outputs

    Returns:
        JSON string containing the stdout, stderr, and return code.
    """
    # Enforce safe paths
    if not script_path.startswith("/mnt/host/aisci/physics/src/"):
        return json.dumps({
            "error": "Invalid script_path. Must be under /mnt/host/aisci/physics/src/"
        })
    if not os.path.exists(script_path):
        return json.dumps({
            "error": f"Script not found: {script_path}"
        })

    cmd = ["python3", script_path]
    
    if pdf_path:
        if not os.path.exists(pdf_path):
            return json.dumps({
                "error": f"PDF not found: {pdf_path}"
            })
        cmd.extend(["--pdf-path", pdf_path])
    if run_dir:
        os.makedirs(run_dir, exist_ok=True)
        cmd.extend(["--run-dir", run_dir])
        
    try:
        # We run this in the container, so paths are already correct for the container context
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return json.dumps({
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        })
    except subprocess.TimeoutExpired:
        return json.dumps({
            "success": False,
            "error": "Script execution timed out after 300 seconds."
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })
