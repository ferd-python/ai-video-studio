"""
Project representation for AI Video Studio.

A Project groups one or more videos under a common goal (an ad campaign,
a YouTube series, a batch of UGC videos...), as described in
docs/SPEC.md section 11. This class only holds data and knows how to
(de)serialize itself to JSON; reading/writing to the right disk location
and creating the folder structure is the responsibility of
ProjectManager.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from project_config import DEFAULT_LANGUAGE, DEFAULT_STATUS, PROJECT_FILE_NAME


@dataclass
class Project:
    name: str
    type: str
    language: str = DEFAULT_LANGUAGE
    status: str = DEFAULT_STATUS
    project_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )
    assets: List[str] = field(default_factory=list)
    videos: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        return cls(
            name=data["name"],
            type=data["type"],
            language=data.get("language", DEFAULT_LANGUAGE),
            status=data.get("status", DEFAULT_STATUS),
            project_id=data.get("project_id", str(uuid.uuid4())[:8]),
            created_at=data.get(
                "created_at", datetime.now().isoformat(timespec="seconds")
            ),
            assets=data.get("assets", []),
            videos=data.get("videos", []),
        )

    def save(self, directory: Path) -> Path:
        """Write this project's project.json into `directory`."""
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / PROJECT_FILE_NAME
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        return file_path

    @classmethod
    def load(cls, directory: Path) -> "Project":
        file_path = directory / PROJECT_FILE_NAME
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
