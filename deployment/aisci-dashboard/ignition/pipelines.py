import os
from pydantic import BaseModel
from typing import List, Optional

class PipelineSpec(BaseModel):
    id: str
    name: str
    command: List[str]
    working_dir: str

class PipelineRegistry:
    def __init__(self):
        self._pipelines = {}
        # Hardcode registered pipelines for Robert's manuscript project
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        robert_root = os.path.join(repo_root, "research", "robert")
        
        self.register(PipelineSpec(
            id="fit-validation",
            name="Run Fits and Validations",
            command=["python", "run_all_fits.py"],
            working_dir=robert_root
        ))
        self.register(PipelineSpec(
            id="symbolic-validation",
            name="Run PySR Symbolic Regression",
            command=["python", "run_pysr.py"],
            working_dir=robert_root
        ))

    def register(self, spec: PipelineSpec):
        self._pipelines[spec.id] = spec

    def get_pipeline(self, pipeline_id: str) -> PipelineSpec:
        if pipeline_id not in self._pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        return self._pipelines[pipeline_id]

registry = PipelineRegistry()
