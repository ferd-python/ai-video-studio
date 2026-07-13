"""
Asset Registry for AI Video Studio.

In-memory catalog of Assets, with JSON persistence. The registry is a
pure data store: registering assets, validating files, and generating
identifiers is the responsibility of AssetManager, which is the only
module expected to write to it (see docs/SPEC.md section 5).
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from asset import Asset

REGISTRY_FILE_NAME = "assets.json"


class AssetRegistry:
    def __init__(self) -> None:
        self._assets: Dict[str, Asset] = {}

    def register(self, asset: Asset) -> Asset:
        self._assets[asset.asset_id] = asset
        return asset

    def get(self, asset_id: str) -> Optional[Asset]:
        return self._assets.get(asset_id)

    def list_all(self) -> List[Asset]:
        return list(self._assets.values())

    def list_by_project(self, project_id: str) -> List[Asset]:
        return [a for a in self._assets.values() if a.project_id == project_id]

    def filter_by_type(
        self, type: str, project_id: Optional[str] = None
    ) -> List[Asset]:
        assets = self.list_by_project(project_id) if project_id else self.list_all()
        return [a for a in assets if a.type == type]

    def filter_by_source(
        self, source: str, project_id: Optional[str] = None
    ) -> List[Asset]:
        assets = self.list_by_project(project_id) if project_id else self.list_all()
        return [a for a in assets if a.source == source]

    def save(self, directory: Path) -> Path:
        """Write every registered asset into `directory`/assets.json."""
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / REGISTRY_FILE_NAME
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                [asset.to_dict() for asset in self._assets.values()],
                f,
                indent=2,
                ensure_ascii=False,
            )
        return file_path

    @classmethod
    def load(cls, directory: Path) -> "AssetRegistry":
        """Load a registry from `directory`/assets.json, if it exists."""
        registry = cls()
        file_path = directory / REGISTRY_FILE_NAME
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for entry in data:
                registry.register(Asset.from_dict(entry))
        return registry
