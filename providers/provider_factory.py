"""
Provider Factory for AI Video Studio.

Single place that turns a provider name (as read from
config/providers.yaml through ConfigManager) into a concrete provider
instance. Adding a new provider is a two-line change here -- implement
it against providers/base_provider.py, then register its class in
REGISTERED_PROVIDERS -- no other module (ImageService included) ever
needs to change, per docs/SPEC.md section 9.
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Type

PROVIDERS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PROVIDERS_DIR.parent
CORE_DIR = PROJECT_ROOT / "core"
for _path in (str(CORE_DIR), str(PROJECT_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from config_manager import ConfigManager  # noqa: E402
from providers.base_provider import BaseProvider  # noqa: E402
from providers.huggingface_provider import HuggingFaceProvider  # noqa: E402
from providers.mock_provider import MockProvider  # noqa: E402
from providers.pollinations_provider import PollinationsProvider  # noqa: E402

# Providers actually implemented today. A future provider becomes
# available to the whole app by implementing it against BaseProvider
# and adding one entry here.
REGISTERED_PROVIDERS: Dict[str, Type[BaseProvider]] = {
    "mock": MockProvider,
    "pollinations": PollinationsProvider,
    "huggingface": HuggingFaceProvider,
}

# Names already reserved for a future step (see docs/SPEC.md section 9)
# but not implemented yet: no class exists for them. Requesting one of
# these today falls back to MockProvider, same as any other name absent
# from REGISTERED_PROVIDERS -- see ProviderFactory.create().
PLANNED_PROVIDERS = {
    "user_image": "UserImageProvider",
    "comfyui": "ComfyUIProvider",
    "openrouter": "OpenRouterProvider",
}


class ProviderFactory:
    """Resolves a provider name (or the active config entry) into an instance."""

    @staticmethod
    def create(name: str) -> BaseProvider:
        """Instantiate the provider registered under `name`, or Mock as a fallback."""
        provider_class = REGISTERED_PROVIDERS.get(name, MockProvider)
        return provider_class()

    @classmethod
    def create_active(
        cls,
        config_manager: Optional[ConfigManager] = None,
        config_key: str = "image_provider",
    ) -> BaseProvider:
        """Read the active provider name from config/providers.yaml and instantiate it."""
        config_manager = config_manager or ConfigManager()
        name = config_manager.get("providers", config_key, default="mock")
        return cls.create(name)
