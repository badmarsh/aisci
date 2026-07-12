import os
import tomllib
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, field_validator

class ProjectSpec(BaseModel):
    id: str
    title: str
    owner: str
    research_type: str
    root: str
    sensitivity: str
    capabilities: List[str]

    @field_validator('root')
    def validate_root(cls, v):
        # Ensure root doesn't break out of the repository.
        # Assuming the repository root is two levels up from ignition/
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        abs_root = os.path.abspath(os.path.join(repo_root, v))
        if not abs_root.startswith(repo_root):
            raise ValueError(f"Project root '{v}' escapes repository root '{repo_root}'")
        return v

    def get_absolute_root(self) -> str:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        return os.path.abspath(os.path.join(repo_root, self.root))

    def get_canonical_path(self, filename: str) -> str:
        # Some projects may have canonical docs in <root>/canonical/, 
        # while Robert has them in <root>/
        path = os.path.join(self.get_absolute_root(), filename)
        if os.path.exists(path):
            return path
        path_canonical = os.path.join(self.get_absolute_root(), "canonical", filename)
        return path_canonical

    def get_runs_dir(self) -> str:
        return os.path.join(self.get_absolute_root(), "runs")

class ProjectRegistry:
    def __init__(self, registry_path: str):
        self.registry_path = registry_path
        self._projects: Dict[str, ProjectSpec] = {}
        self.reload()

    def reload(self):
        self._projects.clear()
        if not os.path.exists(self.registry_path):
            return

        with open(self.registry_path, "rb") as f:
            data = tomllib.load(f)
        
        for p_data in data.get("projects", []):
            try:
                spec = ProjectSpec(**p_data)
                self._projects[spec.id] = spec
            except Exception as e:
                print(f"Failed to load project {p_data.get('id', 'unknown')}: {e}")

    def get_project(self, project_id: str) -> ProjectSpec:
        if project_id not in self._projects:
            raise ValueError(f"Project not found: {project_id}")
        return self._projects[project_id]

    def list_projects(self) -> List[ProjectSpec]:
        return list(self._projects.values())

# Global registry instance
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
registry_file = os.path.join(repo_root, "research", "projects.toml")
registry = ProjectRegistry(registry_file)
