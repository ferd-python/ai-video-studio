"""
Config Manager demonstration for AI Video Studio.

Loads settings.yaml, paths.yaml and providers.yaml through ConfigManager,
prints the active configuration, checks that the providers match their
expected defaults, and reports which paths from paths.yaml exist on disk
(and which would need to be created). No AI model is involved.
"""

from config_manager import ConfigManager

EXPECTED_PROVIDERS = {
    "image_provider": "flux",
    "animation_provider": "wan",
    "voice_provider": "kokoro",
    "subtitle_provider": "whisper",
    "render_provider": "remotion",
}


def main() -> None:
    print("=" * 60)
    print("AI VIDEO STUDIO - CONFIG MANAGER DEMO")
    print("=" * 60)

    manager = ConfigManager()

    print("\nLoading config files...")
    manager.load_all()
    for name in ("settings", "paths", "providers"):
        print(f"  OK - {name}.yaml loaded ({len(manager.get(name))} keys)")

    print("\nActive configuration:")
    manager.print_active_config()

    print("\nValidating required keys...")
    validation = manager.validate_all()
    validation_ok = True
    for name, missing in validation.items():
        if missing:
            validation_ok = False
            print(f"  [INVALID] {name}.yaml is missing: {missing}")
        else:
            print(f"  [OK] {name}.yaml has every required key")

    print("\nChecking providers against expected defaults...")
    providers = manager.get("providers")
    providers_ok = True
    for key, expected_value in EXPECTED_PROVIDERS.items():
        actual_value = providers.get(key)
        match = actual_value == expected_value
        providers_ok &= match
        print(f"  [{'OK' if match else 'MISMATCH'}] {key}: {actual_value} (expected {expected_value})")

    print("\nChecking paths from paths.yaml...")
    path_report = manager.check_paths()
    missing_paths = []
    for key, info in path_report.items():
        status = "EXISTS" if info["exists"] else "MISSING - must be created"
        if not info["exists"]:
            missing_paths.append(str(info["path"]))
        print(f"  [{status}] {key} -> {info['path']}")

    if missing_paths:
        print("\nPaths that must be created:")
        for path in missing_paths:
            print(f"  - {path}")
    else:
        print("\nAll configured paths already exist on disk.")

    test_ok = validation_ok and providers_ok

    print("\n" + "=" * 60)
    print(f"TEST RESULT: {'PASSED' if test_ok else 'FAILED'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
