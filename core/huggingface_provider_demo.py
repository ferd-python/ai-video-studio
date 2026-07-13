"""
Hugging Face Provider demonstration for AI Video Studio.

Creates (or reuses) the "demo_huggingface" project, generates a real
image for the prompt "A cinematic view of the pyramids of Egypt at
sunset" through HuggingFaceProvider (as resolved by ProviderFactory),
saves it under generated/images/, and registers the result in the Asset
Manager -- mirroring core/pollinations_provider_demo.py for step 17's
second provider. It then re-runs the whole flow through ImageService
itself, with the active provider switched to "huggingface" via a
ConfigManager override (config/providers.yaml is left untouched, so the
project-wide default provider is unaffected), to prove ImageService
needs no code change to pick up a new provider.

Requires a free Hugging Face account token in the HF_TOKEN environment
variable (see providers/huggingface_provider.py).
"""

import sys
from pathlib import Path

CORE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CORE_DIR.parent
SERVICES_DIR = PROJECT_ROOT / "services"
for _path in (str(SERVICES_DIR), str(PROJECT_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from asset_manager import AssetManager  # noqa: E402
from config_manager import ConfigManager  # noqa: E402
from image_service import ImageService  # noqa: E402
from project_manager import ProjectManager  # noqa: E402
from providers.huggingface_provider import HuggingFaceProvider  # noqa: E402
from providers.provider_factory import ProviderFactory  # noqa: E402

DEMO_NAME = "demo_huggingface"
DEMO_TYPE = "youtube"
PROMPT = "A cinematic view of the pyramids of Egypt at sunset"
IMAGE_NAME = "pyramids_sunset.jpg"
SCENE_NAME = "scene_pyramids"


class HuggingFaceConfigManager(ConfigManager):
    """Same config/providers.yaml, with image_provider forced to huggingface.

    Demo-only: proves ImageService picks up a different provider purely
    through the config_manager it is handed, without editing the shared
    config/providers.yaml file (which stays on its real default) or
    ImageService's own code.
    """

    def get(self, section, key=None, default=None):
        if section == "providers" and key == "image_provider":
            return "huggingface"
        return super().get(section, key, default)


def ensure_demo_project(manager: ProjectManager):
    try:
        return manager.load_project(DEMO_NAME)
    except FileNotFoundError:
        return manager.create_project(DEMO_NAME, DEMO_TYPE)


def main() -> None:
    print("=" * 60)
    print("AI VIDEO STUDIO - HUGGING FACE PROVIDER DEMO")
    print("=" * 60)

    project_manager = ProjectManager()
    project = ensure_demo_project(project_manager)
    project_path = project_manager._project_path(project.name)
    print(f"\nUsing project: {project.name} (project_id={project.project_id})")

    # 1. ProviderFactory resolves "huggingface" -> HuggingFaceProvider.
    provider = ProviderFactory.create("huggingface")
    provider_ok = isinstance(provider, HuggingFaceProvider)
    print(f"\nProvider resolved by ProviderFactory.create('huggingface'): "
          f"{type(provider).__name__} (name={provider.name})")
    print(f"  [{'OK' if provider_ok else 'FAIL'}] resolves to HuggingFaceProvider")

    # 2. Real generation call against the Hugging Face Inference API.
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

    # 4. ImageService, unmodified, driven by a config_manager whose
    #    "providers.image_provider" resolves to "huggingface".
    print("\n" + "-" * 60)
    print("ImageService end-to-end check (no ImageService code change)")
    print("-" * 60)
    service_ok = False
    service_asset = None
    service_error = None
    try:
        hf_config_manager = HuggingFaceConfigManager()
        image_service = ImageService(
            project_id=project.project_id,
            project_path=project_path,
            config_manager=hf_config_manager,
        )
        service_provider_ok = (
            image_service.configured_provider_name == "huggingface"
            and isinstance(image_service.provider, HuggingFaceProvider)
        )
        print(f"  ImageService.provider: {type(image_service.provider).__name__} "
              f"(configured_provider_name={image_service.configured_provider_name})")
        print(f"  [{'OK' if service_provider_ok else 'FAIL'}] ImageService resolved HuggingFaceProvider")

        service_asset = image_service.get_image_for_scene(SCENE_NAME, PROMPT)
        service_ok = service_provider_ok and service_asset is not None
    except Exception as exc:  # noqa: BLE001
        service_error = exc

    print(f"  [{'OK' if service_ok else 'FAIL'}] ImageService.get_image_for_scene succeeded"
          + ("" if service_ok else f": {service_error}"))
    if service_asset is not None:
        print(f"  Asset: {service_asset.asset_id} -> {service_asset.file_path}")

    test_ok = provider_ok and download_ok and file_ok and asset_ok and service_ok

    print("\nFiles involved in this test:")
    print("  providers/huggingface_provider.py - HuggingFaceProvider (real Hugging Face Inference API)")
    print("  providers/provider_factory.py     - registers 'huggingface' -> HuggingFaceProvider")
    print("  config/providers.yaml             - image_provider default left untouched (pollinations)")
    print("  services/image_service.py         - unmodified, provider swapped via config_manager only")
    print("  core/asset_manager.py             - registers the resulting Asset(s)")
    if asset is not None:
        print(f"  {asset.file_path}  (downloaded image)")
        print(f"  {project_path / 'assets.json'}  (asset registry)")

    print("\n" + "=" * 60)
    print(f"TEST RESULT: {'PASSED' if test_ok else 'FAILED'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
