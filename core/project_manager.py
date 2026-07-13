"""
Project Manager for AI Video Studio.

Creates, loads, saves and lists Projects on disk, following the folder
layout defined in project_config.py and described in docs/SPEC.md
(section 11 - Projects).
"""

from pathlib import Path
from typing import List, Optional

from project import Project
from project_config import PROJECT_FILE_NAME, PROJECT_SUBDIRECTORIES, PROJECTS_DIR


class ProjectManager:
    def __init__(self, projects_dir: Path = PROJECTS_DIR) -> None:
        self.projects_dir = Path(projects_dir)

    def _project_path(self, name: str) -> Path:
        return self.projects_dir / name

    def create_project(
        self, name: str, type: str, language: Optional[str] = None
    ) -> Project:
        """Create a new project on disk, with its standard folder structure."""
        project_path = self._project_path(name)

        if project_path.exists():
            raise FileExistsError(
                f"Project '{name}' already exists at {project_path}"
            )

        kwargs = {"name": name, "type": type}
        if language:
            kwargs["language"] = language
        project = Project(**kwargs)

        for subdirectory in PROJECT_SUBDIRECTORIES:
            (project_path / subdirectory).mkdir(parents=True, exist_ok=True)

        project.save(project_path)
        return project

    def load_project(self, name: str) -> Project:
        """Load a project by reading its project.json."""
        project_path = self._project_path(name)
        if not (project_path / PROJECT_FILE_NAME).exists():
            raise FileNotFoundError(
                f"No project.json found for '{name}' in {project_path}"
            )
        return Project.load(project_path)

    def save_project(self, project: Project) -> Path:
        """Persist a project's current state back to its project.json."""
        project_path = self._project_path(project.name)
        return project.save(project_path)

    def list_projects(self) -> List[str]:
        """List the names of every existing project on disk."""
        if not self.projects_dir.exists():
            return []
        return sorted(
            entry.name
            for entry in self.projects_dir.iterdir()
            if entry.is_dir() and (entry / PROJECT_FILE_NAME).exists()
        )
