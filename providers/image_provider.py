"""
Image Provider interface for AI Video Studio.

Any image generation backend (Flux, a stock library, ...) implements
this interface so that services/image_service.py can call it without
knowing which concrete tool produced the image, per docs/SPEC.md
section 9. Turning a provider *name* into an instance is
ProviderFactory's job (providers/provider_factory.py); this module only
defines the image-specific contract and keeps get_provider() around as
the entry point ImageService already depends on, so it never has to
change when a provider is added or swapped.
"""

from providers.base_provider import BaseProvider


class ImageProvider(BaseProvider):
    """Common interface every image provider must implement."""


def get_provider(name: str) -> ImageProvider:
    """Instantiate the image provider registered under `name`."""
    from providers.provider_factory import ProviderFactory

    return ProviderFactory.create(name)
