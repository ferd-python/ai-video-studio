"""
Storyboard -> Scene Schema converter for AI Video Studio.

Reads output/storyboard.json (produced by scripts/generator/create_storyboard.py)
and converts it into workflow/scene_schema.json, the format consumed by the
Remotion Scene Engine (remotion/src/data/loadScenes.ts).
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STORYBOARD_PATH = PROJECT_ROOT / "output" / "storyboard.json"
SCENE_SCHEMA_PATH = PROJECT_ROOT / "workflow" / "scene_schema.json"

DEFAULT_FORMAT = "horizontal"
DEFAULT_RESOLUTION = "4K"
DEFAULT_FPS = 30
DEFAULT_ANIMATION = "fadeIn"
DEFAULT_TRANSITION = "fade"


def load_storyboard() -> dict:
    with open(STORYBOARD_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def section_to_title(section: str) -> str:
    return section.replace("_", " ").title()


def convert_scene(scene: dict) -> dict:
    return {
        "id": scene["id"],
        "duration": scene["duration"],
        "title": section_to_title(scene.get("section", "")),
        "text": scene["text"],
        "media": scene["media"],
        "animation": DEFAULT_ANIMATION,
        "transition": DEFAULT_TRANSITION,
    }


def convert_storyboard(storyboard: dict) -> dict:
    return {
        "project": {
            "title": storyboard.get("title", ""),
            "format": DEFAULT_FORMAT,
            "resolution": DEFAULT_RESOLUTION,
            "fps": DEFAULT_FPS,
        },
        "scenes": [convert_scene(scene) for scene in storyboard.get("scenes", [])],
    }


def save_scene_schema(scene_schema: dict) -> None:
    SCENE_SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SCENE_SCHEMA_PATH, "w", encoding="utf-8") as f:
        json.dump(scene_schema, f, indent=2, ensure_ascii=False)


def main() -> None:
    storyboard = load_storyboard()
    scene_schema = convert_storyboard(storyboard)
    save_scene_schema(scene_schema)
    print(f"Scene schema generated: {SCENE_SCHEMA_PATH}")


if __name__ == "__main__":
    main()
