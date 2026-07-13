"""
Asset Manager for AI Video Studio.

Single entry point for registering and retrieving media files for a
project. No other module should build or read a file path directly:
they go through the AssetManager to add an asset or resolve its path,
as described in docs/SPEC.md section 5.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from asset import Asset
from asset_registry import AssetRegistry


class AssetManager:
    def __init__(self, project_path: Path) -> None:
        self.project_path = Path(project_path)
        self.registry = AssetRegistry.load(self.project_path)

    def add_asset(
        self,
        project_id: str,
        name: str,
        type: str,
        source: str,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Asset:
        """Validate the file exists, register it, and persist the registry."""
        resolved = Path(file_path)
        if not resolved.exists():
            raise FileNotFoundError(f"Asset file not found: {resolved}")

        asset = Asset(
            project_id=project_id,
            name=name,
            type=type,
            source=source,
            file_path=str(resolved),
            metadata=metadata or {},
        )
        self.registry.register(asset)
        self.registry.save(self.project_path)
        return asset

    def get_asset(self, asset_id: str) -> Optional[Asset]:
        return self.registry.get(asset_id)

    def get_asset_path(self, asset_id: str) -> Optional[Path]:
        asset = self.get_asset(asset_id)
        return Path(asset.file_path) if asset else None

    def list_assets(self, project_id: Optional[str] = None) -> List[Asset]:
        if project_id:
            return self.registry.list_by_project(project_id)
        return self.registry.list_all()

    def filter_by_type(
        self, type: str, project_id: Optional[str] = None
    ) -> List[Asset]:
        return self.registry.filter_by_type(type, project_id)

    def filter_by_source(
        self, source: str, project_id: Optional[str] = None
    ) -> List[Asset]:
        return self.registry.filter_by_source(source, project_id)
