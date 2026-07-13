"""
Hugging Face Image Provider for AI Video Studio.

Real image-generation backend built on the official, free Hugging Face
Inference API (https://api-inference.huggingface.co), replacing/complementing
PollinationsProvider as an implementation of ImageProvider, per
docs/SPEC.md section 9. Defaults to a Flux model (the reference image
generator named in the spec), which is the same family a future local
ComfyUI/Flux provider would serve -- so switching from this hosted
provider to "Flux Local" later is a config.yaml + REGISTERED_PROVIDERS
change, never an ImageService change. Downloads the generated image
straight to `output_path`; registering the result as an Asset is the
caller's job (see services/image_service.py). Uses only the Python
standard library (urllib), no extra dependency required.
"""

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

from providers.image_provider import ImageProvider

HF_API_BASE_URL = "https://api-inference.huggingface.co/models"
DEFAULT_MODEL = "black-forest-labs/FLUX.1-schnell"
DEFAULT_TIMEOUT = 120
DEFAULT_MAX_WAIT_FOR_COLD_START = 180
TOKEN_ENV_VARS = ("HF_TOKEN", "HUGGINGFACE_API_TOKEN", "HUGGINGFACEHUB_API_TOKEN")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"


def _read_env_file(path: Path) -> Dict[str, str]:
    """Parse a simple KEY=VALUE .env file. Never raises if the file is absent."""
    values: Dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


class HuggingFaceProvider(ImageProvider):
    """Generates images by calling the Hugging Face Inference API."""

    name = "huggingface"

    def generate(
        self,
        prompt: str,
        output_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Path:
        metadata = metadata or {}
        token = self._resolve_token(metadata)
        model = metadata.get("model", DEFAULT_MODEL)
        timeout = metadata.get("timeout", DEFAULT_TIMEOUT)
        max_wait = metadata.get("max_wait_for_cold_start", DEFAULT_MAX_WAIT_FOR_COLD_START)

        image_bytes = self._request_image(prompt, model, token, metadata, timeout, max_wait)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(image_bytes)
        return output_path

    @staticmethod
    def _resolve_token(metadata: Dict[str, Any]) -> str:
        token = metadata.get("hf_token")
        if not token:
            for var in TOKEN_ENV_VARS:
                token = os.environ.get(var)
                if token:
                    break
        if not token:
            # Fallback for local dev: a project-root .env file (see .env.example),
            # never committed (see .gitignore) and never touches os.environ.
            token = _read_env_file(ENV_FILE).get(TOKEN_ENV_VARS[0])
        if not token:
            raise RuntimeError(
                "Hugging Face API token missing. Create a free account at "
                "https://huggingface.co, generate a token at "
                "https://huggingface.co/settings/tokens, then set it in the "
                f"{TOKEN_ENV_VARS[0]} environment variable."
            )
        return token

    def _request_image(
        self,
        prompt: str,
        model: str,
        token: str,
        metadata: Dict[str, Any],
        timeout: int,
        max_wait: int,
    ) -> bytes:
        url = f"{HF_API_BASE_URL}/{model}"
        payload: Dict[str, Any] = {"inputs": prompt}
        parameters = {
            key: metadata[key]
            for key in ("width", "height", "negative_prompt", "num_inference_steps", "guidance_scale")
            if key in metadata
        }
        if parameters:
            payload["parameters"] = parameters

        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "image/png",
            "User-Agent": "ai-video-studio/1.0",
        }

        waited = 0
        while True:
            request = urllib.request.Request(url, data=body, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    content_type = response.headers.get("Content-Type", "")
                    payload_bytes = response.read()
            except urllib.error.HTTPError as exc:
                error_bytes = exc.read()
                if exc.code == 503 and waited < max_wait:
                    wait_seconds = self._estimated_wait(error_bytes)
                    time.sleep(wait_seconds)
                    waited += wait_seconds
                    continue
                raise RuntimeError(
                    f"Hugging Face API request failed for prompt '{prompt}' "
                    f"(model={model}, status={exc.code}): {error_bytes.decode('utf-8', 'replace')}"
                ) from exc
            except (urllib.error.URLError, TimeoutError) as exc:
                raise RuntimeError(
                    f"Hugging Face API request failed for prompt '{prompt}' (model={model}): {exc}"
                ) from exc

            if "image" not in content_type:
                raise RuntimeError(
                    f"Hugging Face API returned a non-image response for prompt '{prompt}' "
                    f"(model={model}, content-type={content_type}): "
                    f"{payload_bytes[:200].decode('utf-8', 'replace')}"
                )
            if not payload_bytes:
                raise RuntimeError(f"Hugging Face API returned an empty image for prompt '{prompt}'")
            return payload_bytes

    @staticmethod
    def _estimated_wait(error_bytes: bytes) -> float:
        try:
            data = json.loads(error_bytes.decode("utf-8"))
            return min(float(data.get("estimated_time", 5)), 30.0)
        except (ValueError, TypeError):
            return 5.0
