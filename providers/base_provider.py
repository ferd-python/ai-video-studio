"""
Base Provider interface for AI Video Studio.

Common contract shared by every generation provider (image today,
animation/voice/subtitle/render later), so services depend on this
abstraction instead of on any concrete generation backend, per
docs/SPEC.md section 9. Media-specific interfaces (see
providers/image_provider.py) subclass this rather than redefine it.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional


class BaseProvider(ABC):
    """Common interface every provider must implement."""

    name: str = "unknown"

    @abstractmethod
    def generate(
        self,
        prompt: str,
        output_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Produce a file for `prompt`, write it to `output_path`, and return it."""
        raise NotImplementedError
