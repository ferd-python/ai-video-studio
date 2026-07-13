"""
Mock Image Provider for AI Video Studio.

Fictional provider used until a real one is connected. Simulates the
creation of an image file so the rest of the architecture
(Service -> Provider -> Asset Manager) can be built and tested without
depending on any external AI model, per docs/SPEC.md section 9. This is
the current default implementation, registered under the name "mock" in
providers/provider_factory.py.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from providers.image_provider import ImageProvider


class MockProvider(ImageProvider):
    """Simulates image generation by writing a placeholder text file."""

    name = "mock"

    def generate(
        self,
        prompt: str,
        output_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        content = (
            "MOCK IMAGE (simulated - no real AI model was called)\n"
            f"prompt: {prompt}\n"
            f"metadata: {metadata or {}}\n"
            f"generated_at: {datetime.now().isoformat(timespec='seconds')}\n"
        )
        output_path.write_text(content, encoding="utf-8")
        return output_path
