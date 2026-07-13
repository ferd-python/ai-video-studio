"""
Global configuration system for AI Video Studio.

Loads config/settings.yaml, config/paths.yaml and config/providers.yaml
and exposes them to every module through a single ConfigManager. YAML
syntax is not part of the standard library, so instead of depending on
PyYAML, this module ships a small parser covering the practical subset
of YAML actually used by this project's config files: nested mappings
(2-space indentation), lists of scalars (`- item`) and `#` comments.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

CORE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CORE_DIR.parent
CONFIG_DIR = PROJECT_ROOT / "config"

CONFIG_FILES = {
    "settings": "settings.yaml",
    "paths": "paths.yaml",
    "providers": "providers.yaml",
}

# Keys every config file must define, used by ConfigManager.validate().
REQUIRED_KEYS = {
    "settings": ["language", "fps", "resolution", "format", "codec", "quality"],
    "paths": ["assets", "projects", "output", "logs", "remotion", "workflow"],
    "providers": [
        "image_provider",
        "animation_provider",
        "voice_provider",
        "subtitle_provider",
        "render_provider",
    ],
}


def _parse_scalar(raw: str) -> Any:
    raw = raw.strip()
    if raw == "" or raw == "~" or raw.lower() == "null":
        return None
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
        return raw[1:-1]
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        pass
    return raw


def _strip_comment(line: str) -> str:
    in_single = in_double = False
    for i, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:i]
    return line


def parse_simple_yaml(text: str) -> Dict[str, Any]:
    """Parse a flat or nested `key: value` document, no dependency needed."""
    lines = []
    for raw_line in text.splitlines():
        line = _strip_comment(raw_line).rstrip()
        if line.strip() == "":
            continue
        indent = len(line) - len(line.lstrip(" "))
        lines.append((indent, line.strip()))

    def parse_block(index: int, indent: int):
        result: Dict[str, Any] = {}
        while index < len(lines):
            line_indent, content = lines[index]
            if line_indent < indent:
                break
            if line_indent > indent:
                raise ValueError(f"Unexpected indentation: '{content}'")

            key, _, value = content.partition(":")
            key = key.strip()
            value = value.strip()
            index += 1

            if value != "":
                result[key] = _parse_scalar(value)
                continue

            if index < len(lines) and lines[index][0] > indent and lines[index][1].startswith("- "):
                items: List[Any] = []
                while index < len(lines) and lines[index][0] > indent and lines[index][1].startswith("- "):
                    items.append(_parse_scalar(lines[index][1][2:]))
                    index += 1
                result[key] = items
            elif index < len(lines) and lines[index][0] > indent:
                sub_result, index = parse_block(index, lines[index][0])
                result[key] = sub_result
            else:
                result[key] = None
        return result, index

    if not lines:
        return {}
    parsed, _ = parse_block(0, lines[0][0])
    return parsed


class ConfigManager:
    """Loads and exposes every config/*.yaml file used across the project."""

    def __init__(self, config_dir: Path = CONFIG_DIR) -> None:
        self.config_dir = Path(config_dir)
        self._config: Dict[str, Dict[str, Any]] = {}

    def load(self, name: str) -> Dict[str, Any]:
        """Load a single config file (e.g. "settings") and cache it."""
        file_name = CONFIG_FILES.get(name, f"{name}.yaml")
        file_path = self.config_dir / file_name
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")
        data = parse_simple_yaml(file_path.read_text(encoding="utf-8"))
        self._config[name] = data
        return data

    def load_all(self) -> Dict[str, Dict[str, Any]]:
        """Load every known config file (settings, paths, providers)."""
        for name in CONFIG_FILES:
            self.load(name)
        return self._config

    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """Get a whole section, or a single key within it, loading it if needed."""
        if section not in self._config:
            self.load(section)
        section_data = self._config[section]
        if key is None:
            return section_data
        return section_data.get(key, default)

    def validate(self, name: str, required_keys: Optional[List[str]] = None) -> List[str]:
        """Return the list of required keys missing from a loaded section."""
        if name not in self._config:
            self.load(name)
        expected = required_keys if required_keys is not None else REQUIRED_KEYS.get(name, [])
        return [key for key in expected if key not in self._config[name]]

    def validate_all(self) -> Dict[str, List[str]]:
        """Validate every known config file; empty list means it's valid."""
        return {name: self.validate(name) for name in CONFIG_FILES}

    def resolve_path(self, key: str) -> Path:
        """Resolve a `paths.yaml` entry to an absolute Path under the project root."""
        paths = self.get("paths")
        if key not in paths:
            raise KeyError(f"Unknown path key: '{key}'")
        return PROJECT_ROOT / paths[key]

    def check_paths(self) -> Dict[str, Dict[str, Any]]:
        """For every entry in paths.yaml, report its resolved path and existence."""
        report = {}
        for key in self.get("paths"):
            resolved = self.resolve_path(key)
            report[key] = {"path": resolved, "exists": resolved.exists()}
        return report

    def print_active_config(self) -> None:
        """Print every loaded config section and key/value pair."""
        for name in CONFIG_FILES:
            if name not in self._config:
                self.load(name)
            print(f"[{name}]")
            for key, value in self._config[name].items():
                print(f"  {key}: {value}")
