"""
Asset representation for AI Video Studio.

An Asset is any media file (image, video, audio, logo, music, subtitle)
used by a project, whatever its origin (user-provided, AI-generated,
stock, or otherwise generated), as described in docs/SPEC.md section 5.
This class only holds data and knows how to (de)serialize itself to
JSON; validating the underlying file and maintaining the catalog is the
responsibility of AssetManager / AssetRegistry.
"""

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict

# Known values, aligned with docs/SPEC.md section 5 (Sources média).
ASSET_TYPES = ["image", "video", "audio", "logo", "music", "subtitle"]
ASSET_SOURCES = ["user", "ai", "stock", "generated"]


@dataclass
class Asset:
    project_id: str
    name: str
    type: str
    source: str
    file_path: str
    asset_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Asset":
        return cls(
            project_id=data["project_id"],
            name=data["name"],
            type=data["type"],
            source=data["source"],
            file_path=data["file_path"],
            asset_id=data.get("asset_id", str(uuid.uuid4())[:8]),
            created_at=data.get(
                "created_at", datetime.now().isoformat(timespec="seconds")
            ),
            metadata=data.get("metadata", {}),
        )
