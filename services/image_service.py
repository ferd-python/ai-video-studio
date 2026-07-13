"""
Image Service for AI Video Studio.

Resolves the image for a scene: reuse an image already registered for
that scene in the Asset Manager (a user-provided one takes priority),
otherwise ask the active Image Provider to produce one and register the
result. This wires the Service -> Provider -> Asset Manager chain
described in docs/SPEC.md sections 8-9. The active provider is read from
ConfigManager (config/providers.yaml); the provider itself is still a
fictional placeholder for now (see providers/image_provider.py).
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CORE_DIR = PROJECT_ROOT / "core"
for _path in (str(CORE_DIR), str(PROJECT_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from asset import Asset  # noqa: E402
from asset_manager import AssetManager  # noqa: E402
from config_manager import ConfigManager  # noqa: E402
from providers.image_provider import get_provider  # noqa: E402


class ImageService:
    def __init__(
        self,
        project_id: str,
        project_path: Path,
        asset_manager: Optional[AssetManager] = None,
        config_manager: Optional[ConfigManager] = None,
    ) -> None:
        self.project_id = project_id
        self.project_path = Path(project_path)
        self.asset_manager = asset_manager or AssetManager(self.project_path)
        self.config_manager = config_manager or ConfigManager()

        self.configured_provider_name = self.config_manager.get(
            "providers", "image_provider", default="mock"
        )
        self.provider = get_provider(self.configured_provider_name)

    def _find_existing_image(self, scene_name: str) -> Optional[Asset]:
        """Return a previously registered image for `scene_name`, user assets first."""
        candidates = [
            asset
            for asset in self.asset_manager.list_assets(self.project_id)
            if asset.type == "image" and asset.metadata.get("scene") == scene_name
        ]
        user_assets = [asset for asset in candidates if asset.source == "user"]
        if user_assets:
            return user_assets[0]
        return candidates[0] if candidates else None

    def get_image_for_scene(
        self,
        scene_name: str,
        prompt: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Asset:
        """Return the Asset to use for `scene_name`: a reused image, or a generated one."""
        existing = self._find_existing_image(scene_name)
        if existing is not None:
            return existing

        output_path = self.project_path / "generated" / f"{scene_name}.png"
        self.provider.generate(prompt, output_path, metadata=metadata)

        return self.asset_manager.add_asset(
            project_id=self.project_id,
            name=f"{scene_name}.png",
            type="image",
            source="ai",
            file_path=str(output_path),
            metadata={
                "scene": scene_name,
                "prompt": prompt,
                "provider": self.provider.name,
                **(metadata or {}),
            },
        )
