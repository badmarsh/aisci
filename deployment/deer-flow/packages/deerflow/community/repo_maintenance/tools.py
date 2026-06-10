"""
DeerFlow community tool: repo_maintenance

Provides tools for the `repo-maintainer` agent to perform git operations.
"""
import json
import os
import subprocess
from pathlib import Path
from langchain_core.tools import tool

def _run(cmd: list[str], cwd: str | Path) -> dict:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }
    except Exception as exc:
        return {"success": False, "error": str(exc)}

@tool
def git_commit_push(repo_path_container: str, branch_name: str, commit_message: str) -> str:
    """
    Commits all changes and pushes to a specific branch.
    
    Args:
        repo_path_container: Absolute container path to the repository.
        branch_name: Name of the branch to push to.
        commit_message: Commit message.
        
    Returns:
        JSON string with result.
    """
    repo = Path(repo_path_container)
    if not repo.exists():
        return json.dumps({"success": False, "error": f"Repo not found at {repo_path_container}"})
        
    res_checkout = _run(["git", "checkout", "-b", branch_name], cwd=repo)
    if not res_checkout["success"] and "already exists" not in res_checkout["stderr"]:
        # Try to just checkout if it already exists
        _run(["git", "checkout", branch_name], cwd=repo)
        
    _run(["git", "add", "."], cwd=repo)
    res_commit = _run(["git", "commit", "-m", commit_message], cwd=repo)
    res_push = _run(["git", "push", "-u", "origin", branch_name], cwd=repo)
    
    return json.dumps({
        "success": res_push["success"],
        "commit_output": res_commit["stdout"],
        "push_output": res_push["stderr"] or res_push["stdout"]
    })

@tool
def create_pr(repo_path_container: str, title: str, body: str, base_branch: str = "main") -> str:
    """
    Creates a Pull Request using the gh cli.
    
    Args:
        repo_path_container: Absolute container path to the repository.
        title: PR title.
        body: PR description body.
        base_branch: Base branch to target.
        
    Returns:
        JSON string with result and PR URL.
    """
    repo = Path(repo_path_container)
    res = _run(["gh", "pr", "create", "--title", title, "--body", body, "--base", base_branch], cwd=repo)
    return json.dumps(res)
