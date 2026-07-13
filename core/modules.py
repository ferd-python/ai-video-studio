"""
Module definitions for the AI Video Studio pipeline.

Each module represents one stage of the video generation pipeline and
carries:
  - name:    human-readable label ;
  - status:  READY (already implemented elsewhere in the project),
             PENDING (not developed yet) or DISABLED (not an active step) ;
  - execute: the function the orchestrator calls for that stage.

At this stage, every module's `execute` function is simulated: it only
prints what the stage would do. No image, voice or AI video is generated,
and no file outside `workflow/` is modified.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable


class ModuleStatus(str, Enum):
    READY = "READY"
    PENDING = "PENDING"
    DISABLED = "DISABLED"


@dataclass
class Module:
    name: str
    status: ModuleStatus
    execute: Callable[[], None]


def _simulate(message: str) -> Callable[[], None]:
    """Build a placeholder execution function that only prints a message."""

    def _run() -> None:
        print(f"  [SIMULATED] {message}")

    return _run


MODULES = {
    "storyboard": Module(
        name="Storyboard",
        status=ModuleStatus.READY,
        execute=_simulate(
            "Storyboard generation is implemented "
            "(scripts/generator/create_storyboard.py)."
        ),
    ),
    "scene_schema": Module(
        name="Storyboard -> Scene Schema",
        status=ModuleStatus.READY,
        execute=_simulate(
            "Storyboard -> Scene Schema conversion is implemented "
            "(scripts/converter/storyboard_to_scene.py)."
        ),
    ),
    "images": Module(
        name="Images",
        status=ModuleStatus.PENDING,
        execute=_simulate("Image generation module not yet developed."),
    ),
    "animation": Module(
        name="Animation",
        status=ModuleStatus.PENDING,
        execute=_simulate("Animation module not yet developed."),
    ),
    "voice": Module(
        name="Voice",
        status=ModuleStatus.PENDING,
        execute=_simulate("Voice synthesis module not yet developed."),
    ),
    "subtitles": Module(
        name="Subtitles",
        status=ModuleStatus.PENDING,
        execute=_simulate("Subtitles module not yet developed."),
    ),
    "remotion": Module(
        name="Remotion",
        status=ModuleStatus.READY,
        execute=_simulate(
            "Remotion rendering engine is implemented "
            "(remotion/src/compositions/DynamicVideo.tsx)."
        ),
    ),
    "export": Module(
        name="Export",
        status=ModuleStatus.DISABLED,
        execute=_simulate(
            "Export is currently folded into the Remotion render step "
            "and is disabled as a standalone module."
        ),
    ),
}
