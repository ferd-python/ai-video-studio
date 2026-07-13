"""
Image Service demonstration for AI Video Studio.

Reuses (or creates) the "demo_ugc_product" project, asks the Image
Service for an image for one scene, verifies the active provider falls
back to the fictional MockImageProvider (config/providers.yaml still
points to "flux", which isn't implemented yet), and shows the resulting
Asset registered in the Asset Manager. No real image model is involved.
"""

import sys
from pathlib import Path

CORE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CORE_DIR.parent
SERVICES_DIR = PROJECT_ROOT / "services"
for _path in (str(SERVICES_DIR), str(PROJECT_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from image_service import ImageService  # noqa: E402
from project_manager import ProjectManager  # noqa: E402

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
    print("AI VIDEO STUDIO - IMAGE SERVICE DEMO")
    print("=" * 60)

    project_manager = ProjectManager()
    project = ensure_demo_project(project_manager)
    project_path = project_manager._project_path(project.name)
    print(f"\nUsing project: {project.name} (project_id={project.project_id})")

    image_service = ImageService(project_id=project.project_id, project_path=project_path)
    print(f"\nConfigured provider (config/providers.yaml): {image_service.configured_provider_name}")
    print(f"Provider actually used by the service: {image_service.provider.name}")
    provider_ok = image_service.provider.name == "mock"
    print(f"  [{'OK' if provider_ok else 'MISMATCH'}] service uses MockImageProvider")

    print(f"\nRequesting an image for scene '{SCENE_NAME}'...")
    asset = image_service.get_image_for_scene(
        SCENE_NAME, PROMPT, metadata={"style": "product_shot"}
    )

    print("\nAsset returned by the Image Service:")
    for key, value in asset.to_dict().items():
        print(f"  {key}: {value}")

    registered = image_service.asset_manager.get_asset(asset.asset_id)
    registered_ok = registered is not None
    print(f"\n  [{'OK' if registered_ok else 'MISSING'}] asset found in Asset Manager registry")

    file_ok = Path(asset.file_path).exists()
    print(f"  [{'OK' if file_ok else 'MISSING'}] simulated image file exists on disk: {asset.file_path}")

    print("\nRequesting the same scene again (should reuse, not duplicate)...")
    asset_again = image_service.get_image_for_scene(
        SCENE_NAME, PROMPT, metadata={"style": "product_shot"}
    )
    reuse_ok = asset_again.asset_id == asset.asset_id
    print(f"  [{'OK' if reuse_ok else 'DUPLICATE'}] same asset_id reused: {asset_again.asset_id}")

    test_ok = provider_ok and registered_ok and file_ok and reuse_ok

    print("\nFiles involved in this test:")
    print("  providers/image_provider.py  - ImageProvider interface + MockImageProvider")
    print("  services/image_service.py    - ImageService (reuse-or-generate logic)")
    print("  core/config_manager.py       - reads the active provider from config/providers.yaml")
    print("  core/asset_manager.py        - registers the resulting Asset")
    print(f"  {asset.file_path}  (simulated image file)")
    print(f"  {project_path / 'assets.json'}  (asset registry)")

    print("\n" + "=" * 60)
    print(f"TEST RESULT: {'PASSED' if test_ok else 'FAILED'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
