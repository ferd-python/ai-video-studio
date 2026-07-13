"""
Configuration constants for the Project Manager.

Defines where projects live on disk, the standard folder layout created
for every project, and a few sane defaults. Python standard library only.
"""

from pathlib import Path

CORE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CORE_DIR.parent
PROJECTS_DIR = PROJECT_ROOT / "projects"

PROJECT_FILE_NAME = "project.json"

DEFAULT_LANGUAGE = "fr"
DEFAULT_STATUS = "CREATED"

# Folder structure created inside every projects/<name>/ directory.
PROJECT_SUBDIRECTORIES = [
    "input/images",
    "input/videos",
    "input/audio",
    "generated",
    "scripts",
    "output",
]

# Known project types, aligned with docs/SPEC.md section 3 (Types de vidéos).
KNOWN_PROJECT_TYPES = [
    "youtube",
    "tiktok",
    "shorts",
    "ads",
    "ugc_ads",
    "product_demo",
    "documentary",
    "training",
]
