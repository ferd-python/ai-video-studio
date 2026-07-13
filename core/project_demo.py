"""
Project Manager demonstration for AI Video Studio.

Creates a demo project ("demo_ugc_product"), verifies its folder structure
and project.json on disk, reloads it, and prints the result. No AI model
is involved.
"""

from pathlib import Path

from project_config import PROJECT_FILE_NAME, PROJECT_SUBDIRECTORIES
from project_manager import ProjectManager

DEMO_NAME = "demo_ugc_product"
DEMO_TYPE = "ugc_ads"


def list_created_files(project_path: Path) -> list:
    return sorted(
        str(p.relative_to(project_path)) for p in project_path.rglob("*")
    )


def print_tree(project_path: Path) -> None:
    print(f"{project_path.name}/")
    for entry in list_created_files(project_path):
        depth = entry.count("/")
        print("  " * (depth + 1) + Path(entry).name + ("/" if (project_path / entry).is_dir() else ""))


def main() -> None:
    print("=" * 60)
    print("AI VIDEO STUDIO - PROJECT MANAGER DEMO")
    print("=" * 60)

    manager = ProjectManager()
    project_path = manager._project_path(DEMO_NAME)

    if project_path.exists():
        import shutil

        shutil.rmtree(project_path)
        print(f"\nExisting demo project removed: {project_path}")

    print(f"\nCreating project '{DEMO_NAME}' (type={DEMO_TYPE})...")
    project = manager.create_project(DEMO_NAME, DEMO_TYPE)
    print(f"Project created: {project}")

    print("\nChecking folder structure...")
    all_ok = True
    for subdirectory in PROJECT_SUBDIRECTORIES:
        path = project_path / subdirectory
        ok = path.is_dir()
        all_ok &= ok
        print(f"  [{'OK' if ok else 'MISSING'}] {subdirectory}/")

    project_json_path = project_path / PROJECT_FILE_NAME
    json_ok = project_json_path.is_file()
    all_ok &= json_ok
    print(f"  [{'OK' if json_ok else 'MISSING'}] {PROJECT_FILE_NAME}")

    print("\nLoading project back from disk...")
    loaded = manager.load_project(DEMO_NAME)
    print(f"Loaded project: {loaded}")

    print("\nProject information:")
    for key, value in loaded.to_dict().items():
        print(f"  {key}: {value}")

    print("\nExisting projects on disk:")
    for name in manager.list_projects():
        print(f"  - {name}")

    print("\nFiles and folders created:")
    print_tree(project_path)

    print("\n" + "=" * 60)
    print(f"TEST RESULT: {'PASSED' if all_ok else 'FAILED'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
