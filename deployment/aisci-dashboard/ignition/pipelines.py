import os
import tomllib
from pydantic import BaseModel
from typing import List, Optional, Dict

class PipelineSpec(BaseModel):
    id: str
    name: str
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
        self.validate_safety()
        return {
            "id": self.id,
            "name": self.name,
            "command": " ".join(self.command),
            "working_dir": self.working_dir,
            "requires_input": self.requires_input,
            "is_safe": True
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
                # If working_dir is a relative path like ".", resolve to project root
                wdir = p_data.get("working_dir", ".")
                if not os.path.isabs(wdir):
                    wdir = os.path.normpath(os.path.join(project_spec.get_absolute_root(), wdir))
                
                spec = PipelineSpec(
                    id=p_id,
                    name=p_data.get("name", p_id),
                    command=p_data.get("command", []),
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
