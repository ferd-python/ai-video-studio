"""
Asset Manager demonstration for AI Video Studio.

Reuses (or creates) the "demo_ugc_product" project, registers a handful
of fictional assets (a user image, a logo, a stock video) exclusively
through the AssetManager, then prints the registry content filtered by
type and by source. No AI model is involved.
"""

from pathlib import Path

from asset_manager import AssetManager
from project_manager import ProjectManager

DEMO_NAME = "demo_ugc_product"
DEMO_TYPE = "ugc_ads"


def ensure_demo_project(manager: ProjectManager):
    try:
        return manager.load_project(DEMO_NAME)
    except FileNotFoundError:
        return manager.create_project(DEMO_NAME, DEMO_TYPE)


def write_fake_file(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def print_assets(title: str, assets) -> None:
    print(f"\n{title}")
    if not assets:
        print("  (none)")
    for asset in assets:
        print(
            f"  - [{asset.asset_id}] {asset.name} "
            f"(type={asset.type}, source={asset.source}) -> {asset.file_path}"
        )


def main() -> None:
    print("=" * 60)
    print("AI VIDEO STUDIO - ASSET MANAGER DEMO")
    print("=" * 60)

    project_manager = ProjectManager()
    project = ensure_demo_project(project_manager)
    project_path = project_manager._project_path(project.name)
    print(f"\nUsing project: {project.name} (project_id={project.project_id})")

    registry_file = project_path / "assets.json"
    if registry_file.exists():
        registry_file.unlink()
        print(f"Existing registry removed: {registry_file}")

    # The AssetManager is the only object that will touch these paths from
    # this point on.
    asset_manager = AssetManager(project_path)

    fake_files = [
        write_fake_file(
            project_path / "input" / "images" / "user_photo.jpg",
            "fake user image bytes",
        ),
        write_fake_file(
            project_path / "input" / "images" / "brand_logo.png",
            "fake logo bytes",
        ),
        write_fake_file(
            project_path / "input" / "videos" / "product_clip.mp4",
            "fake video bytes",
        ),
    ]
    print("\nFictional source files written to disk:")
    for f in fake_files:
        print(f"  - {f}")

    print("\nRegistering assets through AssetManager only...")
    asset_manager.add_asset(
        project_id=project.project_id,
        name="user_photo.jpg",
        type="image",
        source="user",
        file_path=str(fake_files[0]),
        metadata={"width": 1080, "height": 1920},
    )
    asset_manager.add_asset(
        project_id=project.project_id,
        name="brand_logo.png",
        type="logo",
        source="user",
        file_path=str(fake_files[1]),
        metadata={"transparent": True},
    )
    asset_manager.add_asset(
        project_id=project.project_id,
        name="product_clip.mp4",
        type="video",
        source="stock",
        file_path=str(fake_files[2]),
        metadata={"duration_s": 12},
    )

    print_assets(
        "Registry content (all assets for this project):",
        asset_manager.list_assets(project.project_id),
    )
    print_assets(
        "Assets filtered by type='image':",
        asset_manager.filter_by_type("image", project.project_id),
    )
    print_assets(
        "Assets filtered by source='user':",
        asset_manager.filter_by_source("user", project.project_id),
    )
    print_assets(
        "Assets filtered by source='stock':",
        asset_manager.filter_by_source("stock", project.project_id),
    )

    print("\nAttempting to register a missing file (should be rejected)...")
    try:
        asset_manager.add_asset(
            project_id=project.project_id,
            name="ghost.mp3",
            type="audio",
            source="ai",
            file_path=str(project_path / "input" / "audio" / "ghost.mp3"),
        )
        print("  UNEXPECTED: no error raised")
        test_ok = False
    except FileNotFoundError as exc:
        print(f"  OK - rejected as expected: {exc}")
        test_ok = True

    print(f"\nRegistry persisted at: {registry_file} (exists={registry_file.exists()})")
    test_ok &= registry_file.exists()
    test_ok &= len(asset_manager.list_assets(project.project_id)) == 3

    print("\n" + "=" * 60)
    print(f"TEST RESULT: {'PASSED' if test_ok else 'FAILED'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
