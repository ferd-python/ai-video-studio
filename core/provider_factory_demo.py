"""
Provider Factory demonstration for AI Video Studio.

Shows that ProviderFactory (providers/provider_factory.py) correctly
resolves the "mock" provider name to MockProvider, that it falls back to
MockProvider for the still-unimplemented "flux" name configured in
config/providers.yaml, and that ImageService (services/image_service.py)
keeps working exactly as before -- it was not touched to add this
Provider system, per docs/SPEC.md section 9.
"""

import sys
from pathlib import Path

CORE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CORE_DIR.parent
SERVICES_DIR = PROJECT_ROOT / "services"
for _path in (str(SERVICES_DIR), str(PROJECT_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from config_manager import ConfigManager  # noqa: E402
from image_service import ImageService  # noqa: E402
from project_manager import ProjectManager  # noqa: E402
from providers.base_provider import BaseProvider  # noqa: E402
from providers.image_provider import ImageProvider  # noqa: E402
from providers.mock_provider import MockProvider  # noqa: E402
from providers.provider_factory import (  # noqa: E402
    PLANNED_PROVIDERS,
    REGISTERED_PROVIDERS,
    ProviderFactory,
)

DEMO_NAME = "demo_ugc_product"
DEMO_TYPE = "ugc_ads"
SCENE_NAME = "scene_01_intro"
PROMPT = "A close-up product shot on a clean white background, studio lighting"


def ensure_demo_project(manager: ProjectManager):
    try:
        return manager.load_project(DEMO_NAME)
    except FileNotFoundError:
        return manager.create_project(DEMO_NAME, DEMO_TYPE)


def main() -> None:
    print("=" * 60)
    print("AI VIDEO STUDIO - PROVIDER FACTORY DEMO")
    print("=" * 60)

    # 1. Interface hierarchy: BaseProvider -> ImageProvider -> MockProvider.
    print("\n[1] Interface hierarchy")
    hierarchy_ok = issubclass(ImageProvider, BaseProvider) and issubclass(
        MockProvider, ImageProvider
    )
    print(f"  ImageProvider subclasses BaseProvider: {issubclass(ImageProvider, BaseProvider)}")
    print(f"  MockProvider subclasses ImageProvider: {issubclass(MockProvider, ImageProvider)}")
    print(f"  [{'OK' if hierarchy_ok else 'FAIL'}] hierarchy is correct")

    # 2. ProviderFactory.create("mock") resolves directly to MockProvider.
    print("\n[2] ProviderFactory.create('mock')")
    direct_provider = ProviderFactory.create("mock")
    direct_ok = isinstance(direct_provider, MockProvider) and direct_provider.name == "mock"
    print(f"  instance type: {type(direct_provider).__name__}")
    print(f"  [{'OK' if direct_ok else 'FAIL'}] resolves to MockProvider")

    # 3. ProviderFactory.create_active() reads config/providers.yaml.
    # That file still points image_provider to "flux" (not implemented),
    # so the factory must fall back to MockProvider, same as before.
    print("\n[3] ProviderFactory.create_active() via ConfigManager")
    config_manager = ConfigManager()
    configured_name = config_manager.get("providers", "image_provider", default="mock")
    active_provider = ProviderFactory.create_active(config_manager)
    fallback_ok = isinstance(active_provider, MockProvider)
    print(f"  configured name (config/providers.yaml): {configured_name}")
    print(f"  provider resolved by the factory: {active_provider.name}")
    print(f"  [{'OK' if fallback_ok else 'FAIL'}] unimplemented name falls back to MockProvider")

    # 4. Planned providers are reserved, not implemented, per the spec.
    print("\n[4] Providers reserved for future steps (not implemented)")
    for key, class_name in PLANNED_PROVIDERS.items():
        print(f"  {key} -> {class_name} (planned)")
    planned_ok = all(key not in REGISTERED_PROVIDERS for key in PLANNED_PROVIDERS)
    print(f"  [{'OK' if planned_ok else 'FAIL'}] none of them are registered/implemented yet")

    # 5. ImageService, entirely unmodified, still works end to end.
    print("\n[5] ImageService (unmodified) end-to-end")
    project_manager = ProjectManager()
    project = ensure_demo_project(project_manager)
    project_path = project_manager._project_path(project.name)
    print(f"  using project: {project.name} (project_id={project.project_id})")

    image_service = ImageService(project_id=project.project_id, project_path=project_path)
    print(f"  configured provider (config/providers.yaml): {image_service.configured_provider_name}")
    print(f"  provider actually used by the service: {image_service.provider.name}")
    service_provider_ok = isinstance(image_service.provider, MockProvider)
    print(f"  [{'OK' if service_provider_ok else 'FAIL'}] service resolved MockProvider through get_provider()")

    asset = image_service.get_image_for_scene(
        SCENE_NAME, PROMPT, metadata={"style": "product_shot"}
    )
    registered = image_service.asset_manager.get_asset(asset.asset_id)
    registered_ok = registered is not None
    file_ok = Path(asset.file_path).exists()
    print(f"  [{'OK' if registered_ok else 'MISSING'}] asset registered in Asset Manager")
    print(f"  [{'OK' if file_ok else 'MISSING'}] simulated image file exists: {asset.file_path}")

    asset_again = image_service.get_image_for_scene(
        SCENE_NAME, PROMPT, metadata={"style": "product_shot"}
    )
    reuse_ok = asset_again.asset_id == asset.asset_id
    print(f"  [{'OK' if reuse_ok else 'DUPLICATE'}] same asset_id reused on a second call")

    service_ok = service_provider_ok and registered_ok and file_ok and reuse_ok

    test_ok = hierarchy_ok and direct_ok and fallback_ok and planned_ok and service_ok

    print("\nFiles involved in this test:")
    print("  providers/base_provider.py      - BaseProvider common interface")
    print("  providers/image_provider.py     - ImageProvider interface + get_provider()")
    print("  providers/mock_provider.py      - MockProvider (current implementation)")
    print("  providers/provider_factory.py   - ProviderFactory (loads active provider)")
    print("  services/image_service.py       - ImageService, not modified")
    print("  core/config_manager.py          - reads the active provider from config/providers.yaml")

    print("\n" + "=" * 60)
    print(f"TEST RESULT: {'PASSED' if test_ok else 'FAILED'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
