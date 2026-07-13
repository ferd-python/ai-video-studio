"""
Pollinations Provider demonstration for AI Video Studio.

Creates (or reuses) the "demo_pollinations" project, generates a real
image for the prompt "A cinematic view of the pyramids of Egypt at
sunset" through PollinationsProvider (as resolved by ProviderFactory from
config/providers.yaml), saves it under generated/images/, and registers
the result in the Asset Manager. Unlike image_service_demo.py, this hits
the real Pollinations AI API -- no mock involved -- per the step 17 spec.
"""

import sys
from pathlib import Path

CORE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CORE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from asset_manager import AssetManager  # noqa: E402
from config_manager import ConfigManager  # noqa: E402
from project_manager import ProjectManager  # noqa: E402
from providers.pollinations_provider import PollinationsProvider  # noqa: E402
from providers.provider_factory import ProviderFactory  # noqa: E402

DEMO_NAME = "demo_pollinations"
DEMO_TYPE = "youtube"
PROMPT = "A cinematic view of the pyramids of Egypt at sunset"
IMAGE_NAME = "pyramids_sunset.jpg"


def ensure_demo_project(manager: ProjectManager):
    try:
        return manager.load_project(DEMO_NAME)
    except FileNotFoundError:
        return manager.create_project(DEMO_NAME, DEMO_TYPE)


def main() -> None:
    print("=" * 60)
    print("AI VIDEO STUDIO - POLLINATIONS PROVIDER DEMO")
    print("=" * 60)

    project_manager = ProjectManager()
    project = ensure_demo_project(project_manager)
    project_path = project_manager._project_path(project.name)
    print(f"\nUsing project: {project.name} (project_id={project.project_id})")

    # 1. Config resolution: providers.yaml -> ProviderFactory -> PollinationsProvider
    config_manager = ConfigManager()
    configured_name = config_manager.get("providers", "image_provider", default="mock")
    provider = ProviderFactory.create_active(config_manager)
    provider_ok = configured_name == "pollinations" and isinstance(provider, PollinationsProvider)
    print(f"\nConfigured provider (config/providers.yaml): {configured_name}")
    print(f"Provider resolved by ProviderFactory: {type(provider).__name__} (name={provider.name})")
    print(f"  [{'OK' if provider_ok else 'FAIL'}] providers.yaml resolves to PollinationsProvider")

    # 2. Real generation call against the Pollinations AI API.
    images_dir = project_path / "generated" / "images"
    output_path = images_dir / IMAGE_NAME
    print(f"\nRequesting image for prompt: \"{PROMPT}\"")
    error = None
    try:
        provider.generate(PROMPT, output_path, metadata={"width": 1024, "height": 576})
        download_ok = True
    except Exception as exc:  # noqa: BLE001
        download_ok = False
        error = exc

    file_ok = download_ok and output_path.exists() and output_path.stat().st_size > 0
    print(f"  [{'OK' if download_ok else 'FAIL'}] download completed" + ("" if download_ok else f": {error}"))
    print(f"  [{'OK' if file_ok else 'MISSING'}] file written under generated/images/: {output_path}")
    if file_ok:
        print(f"  file size: {output_path.stat().st_size} bytes")

    # 3. Asset Manager registration.
    asset = None
    asset_ok = False
    if file_ok:
        asset_manager = AssetManager(project_path)
        asset = asset_manager.add_asset(
            project_id=project.project_id,
            name=IMAGE_NAME,
            type="image",
            source="ai",
            file_path=str(output_path),
            metadata={"prompt": PROMPT, "provider": provider.name},
        )
        registered = asset_manager.get_asset(asset.asset_id)
        asset_ok = registered is not None

    print(f"\n  [{'OK' if asset_ok else 'FAIL'}] Asset created and registered in Asset Manager")
    if asset is not None:
        print("\nAsset returned:")
        for key, value in asset.to_dict().items():
            print(f"  {key}: {value}")
        print(f"\nFile path: {Path(asset.file_path).resolve()}")

    test_ok = provider_ok and download_ok and file_ok and asset_ok

    print("\nFiles involved in this test:")
    print("  providers/pollinations_provider.py - PollinationsProvider (real Pollinations AI backend)")
    print("  providers/provider_factory.py      - registers 'pollinations' -> PollinationsProvider")
    print("  config/providers.yaml              - image_provider: pollinations")
    print("  core/asset_manager.py              - registers the resulting Asset")
    if asset is not None:
        print(f"  {asset.file_path}  (downloaded image)")
        print(f"  {project_path / 'assets.json'}  (asset registry)")

    print("\n" + "=" * 60)
    print(f"TEST RESULT: {'PASSED' if test_ok else 'FAILED'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
