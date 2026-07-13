"""
Official pipeline definition for AI Video Studio.

Defines the ordered list of module keys that the orchestrator executes.
To extend the pipeline: add a new module to `modules.py`, then insert its
key at the right position in `PIPELINE` below.
"""

PIPELINE = [
    "storyboard",
    "scene_schema",
    "images",
    "animation",
    "voice",
    "subtitles",
    "remotion",
    "export",
]
