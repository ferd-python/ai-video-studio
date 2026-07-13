"""
Storyboard generator for AI Video Studio.

Phase 1 (current): builds a storyboard from example/placeholder text and a
project template, without any external API.

Future: `generate_section_text` will be replaced by a call to the Claude
API to write real narration for each section, using the same signature.
"""

import argparse
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = PROJECT_ROOT / "templates" / "youtube_documentary" / "template.json"
OUTPUT_PATH = PROJECT_ROOT / "output" / "storyboard.json"


def load_template() -> dict:
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_section_text(subject: str, section: str) -> str:
    """Placeholder narration text for a given section and subject."""
    placeholders = {
        "intro": f"Découvrez {subject}, une histoire méconnue qui mérite d'être racontée.",
        "main_content": f"Plongeons au cœur de {subject} pour en comprendre les origines et l'héritage.",
        "conclusion": f"{subject} continue d'influencer notre compréhension du monde aujourd'hui.",
    }
    return placeholders.get(section, f"Contenu à propos de {subject}.")


def build_scenes(subject: str, template: dict) -> list:
    scenes = []
    for index, section in enumerate(template["structure"], start=1):
        scenes.append(
            {
                "id": index,
                "section": section["section"],
                "duration": section["duration_seconds"],
                "text": generate_section_text(subject, section["section"]),
                "media": {
                    "type": "image",
                    "path": f"assets/images/scene{index:02d}.png",
                },
            }
        )
    return scenes


def generate_storyboard(subject: str) -> dict:
    template = load_template()
    return {
        "title": subject,
        "description": f"Documentaire sur {subject}, généré à partir du template {template['type']}.",
        "style": template["style"],
        "scenes": build_scenes(subject, template),
    }


def save_storyboard(storyboard: dict) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(storyboard, f, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a storyboard for an AI Video Studio video."
    )
    parser.add_argument("subject", type=str, help="Subject of the video")
    args = parser.parse_args()

    storyboard = generate_storyboard(args.subject)
    save_storyboard(storyboard)
    print(f"Storyboard generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
