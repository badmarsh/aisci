import os
import sys
import subprocess
import tomllib
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PipelineSpec(BaseModel):
    id: str
    name: str
    owner: str = "System"
    description: Optional[str] = None
    citation: Optional[str] = None
    entrypoint: Optional[str] = None
    command: List[str]
    working_dir: str
    requires_input: Optional[str] = None

    def validate_safety(self):
        unsafe_commands = {"rm -rf", "mkfs", "dd", ">", ">>"}
        cmd_str = " ".join(self.command)
        for unsafe in unsafe_commands:
            if unsafe in cmd_str:
                raise ValueError(f"Unsafe command detected: {unsafe}")

    def dry_run(self) -> dict:
        try:
            self.validate_safety()
            is_safe = True
            msg = "Safe"
        except Exception as e:
            is_safe = False
            msg = str(e)

        checks = []
        checks.append({
            "name": "Command Safety",
            "passed": is_safe,
            "message": msg
        })

        has_venv = False
        if self.command and "physics-core/.venv/bin/python" in self.command[0]:
            venv_python = self.command[0]
            has_venv = os.path.exists(venv_python)
            checks.append({
                "name": "Virtual Environment",
                "passed": has_venv,
                "message": f"Found" if has_venv else "Missing python at venv"
            })

            has_iminuit = False
            if has_venv:
                try:
                    res = subprocess.run([venv_python, "-c", "import iminuit"], capture_output=True, text=True, timeout=5)
                    has_iminuit = (res.returncode == 0)
                except Exception:
                    pass
            checks.append({
                "name": "Dependency: iminuit",
                "passed": has_iminuit,
                "message": "Installed" if has_iminuit else "Failed to import"
            })

        if self.requires_input:
            input_path = os.path.join(self.working_dir, self.requires_input)
            has_input = os.path.exists(input_path)
            checks.append({
                "name": f"Input: {self.requires_input}",
                "passed": has_input,
                "message": "Found" if has_input else "Missing"
            })

        all_passed = all(c['passed'] for c in checks)

        return {
            "id": self.id,
            "name": self.name,
            "owner": self.owner,
            "description": self.description,
            "citation": self.citation,
            "entrypoint": self.entrypoint,
            "command": " ".join(self.command),
            "working_dir": self.working_dir,
            "requires_input": self.requires_input,
            "status": "available" if all_passed else "unavailable",
            "available": all_passed,
            "checks": checks
        }

class PipelineRegistry:
    def __init__(self):
        pass

    def get_pipelines_for_project(self, project_spec) -> List[PipelineSpec]:
        pipelines_file = os.path.join(project_spec.get_absolute_root(), "pipelines.toml")
        if not os.path.exists(pipelines_file):
            return []

        with open(pipelines_file, "rb") as f:
            data = tomllib.load(f)

        specs = []
        for p_id, p_data in data.get("pipelines", {}).items():
            try:
                wdir = p_data.get("working_dir", ".")
                if not os.path.isabs(wdir):
                    wdir = os.path.normpath(os.path.join(project_spec.get_absolute_root(), wdir))

                command = p_data.get("command", [])

                # Intercept fit-validation to use real venv and cli.py
                if p_id == "fit-validation":
                    venv_python = os.path.normpath(os.path.join(project_spec.get_absolute_root(), "../../libs/physics-core/.venv/bin/python"))
                    cli_py = os.path.normpath(os.path.join(project_spec.get_absolute_root(), "../../libs/physics-core/cli.py"))
                    runs_dir = os.path.normpath(os.path.join(project_spec.get_absolute_root(), "runs/latest-auto"))
                    command = [venv_python, cli_py, "--run-dir", runs_dir]
                    wdir = os.path.normpath(os.path.join(project_spec.get_absolute_root(), "../.."))
                elif p_id == "sensitivity-scan":
                    venv_python = os.path.normpath(os.path.join(project_spec.get_absolute_root(), "../../libs/physics-core/.venv/bin/python"))
                    scan_py = os.path.normpath(os.path.join(project_spec.get_absolute_root(), "../../libs/physics-core/src/exact_be_fit_range_scan.py"))
                    command = [venv_python, scan_py]
                    wdir = os.path.normpath(os.path.join(project_spec.get_absolute_root(), "../.."))
                elif p_id == "ingest-validation":
                    venv_python = sys.executable
                    ingest_py = os.path.normpath(os.path.join(project_spec.get_absolute_root(), "../../deployment/aisci-dashboard/ignition/ingest_pipeline.py"))
                    command = [venv_python, ingest_py]
                    wdir = os.path.normpath(os.path.join(project_spec.get_absolute_root(), "../.."))

                spec = PipelineSpec(
                    id=p_id,
                    name=p_data.get("name", p_id),
                    owner=p_data.get("owner", "System"),
                    description=p_data.get("description"),
                    citation=p_data.get("citation"),
                    entrypoint=p_data.get("entrypoint"),
                    command=command,
                    working_dir=wdir,
                    requires_input=p_data.get("requires_input")
                )
                specs.append(spec)
            except Exception as e:
                print(f"Failed to load pipeline {p_id}: {e}")
        return specs

    def get_pipeline(self, project_spec, pipeline_id: str) -> PipelineSpec:
        pipelines = self.get_pipelines_for_project(project_spec)
        for p in pipelines:
            if p.id == pipeline_id:
                return p
        raise ValueError(f"Pipeline {pipeline_id} not found for project {project_spec.id}")

registry = PipelineRegistry()
