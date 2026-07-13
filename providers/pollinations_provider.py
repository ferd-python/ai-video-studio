"""
Pollinations Image Provider for AI Video Studio.

Real image-generation backend built on the free Pollinations AI HTTP API
(https://image.pollinations.ai), replacing MockProvider as the day-to-day
implementation of ImageProvider, per docs/SPEC.md section 9. Downloads the
generated image straight to `output_path`; registering the result as an
Asset is the caller's job (see services/image_service.py). Uses only the
Python standard library (urllib), no extra dependency required.
"""

import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

from providers.image_provider import ImageProvider

POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"
DEFAULT_TIMEOUT = 60
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 1024


class PollinationsProvider(ImageProvider):
    """Generates images by calling the Pollinations AI text-to-image API."""

    name = "pollinations"

    def generate(
        self,
        prompt: str,
        output_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Path:
        metadata = metadata or {}
        url = self._build_url(prompt, metadata)
        timeout = metadata.get("timeout", DEFAULT_TIMEOUT)

        request = urllib.request.Request(url, headers={"User-Agent": "ai-video-studio/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                image_bytes = response.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError(
                f"Pollinations AI request failed for prompt '{prompt}': {exc}"
            ) from exc

        if not image_bytes:
            raise RuntimeError(f"Pollinations AI returned an empty response for prompt '{prompt}'")

        # Pollinations always serves image/jpeg regardless of the query params
        # or the extension requested here; callers should name output_path
        # accordingly (e.g. ".jpg").
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(image_bytes)
        return output_path

    @staticmethod
    def _build_url(prompt: str, metadata: Dict[str, Any]) -> str:
        encoded_prompt = urllib.parse.quote(prompt)
        params = {
            "width": metadata.get("width", DEFAULT_WIDTH),
            "height": metadata.get("height", DEFAULT_HEIGHT),
            "nologo": "true",
        }
        if "seed" in metadata:
            params["seed"] = metadata["seed"]
        if "model" in metadata:
            params["model"] = metadata["model"]
        query = urllib.parse.urlencode(params)
        return f"{POLLINATIONS_BASE_URL}/{encoded_prompt}?{query}"
