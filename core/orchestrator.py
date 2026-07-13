"""
AI Video Studio - Pipeline Orchestrator.

Loads the official pipeline order (pipeline.py), runs each module in
sequence (modules.py), prints a clear execution log, and finishes with a
summary. This step only organizes and sequences the pipeline - it does not
generate any image, voice or AI video yet.
"""

from modules import MODULES, ModuleStatus
from pipeline import PIPELINE


def run_pipeline() -> list[dict]:
    results = []

    print("=" * 60)
    print("AI VIDEO STUDIO - PIPELINE ORCHESTRATOR")
    print("=" * 60)

    for step_number, key in enumerate(PIPELINE, start=1):
        module = MODULES[key]
        print(
            f"\n[{step_number}/{len(PIPELINE)}] {module.name} "
            f"- status: {module.status.value}"
        )

        if module.status == ModuleStatus.DISABLED:
            print("  Skipped (module disabled).")
            results.append(
                {
                    "step": step_number,
                    "module": module.name,
                    "status": module.status.value,
                    "executed": False,
                }
            )
            continue

        module.execute()
        results.append(
            {
                "step": step_number,
                "module": module.name,
                "status": module.status.value,
                "executed": True,
            }
        )

    return results


def print_summary(results: list[dict]) -> None:
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)

    for result in results:
        state = "executed" if result["executed"] else "skipped"
        print(
            f"  {result['step']}. {result['module']:<28} "
            f"[{result['status']}] -> {state}"
        )

    executed = sum(1 for r in results if r["executed"])
    print(f"\n{executed}/{len(results)} modules executed, "
          f"{len(results) - executed} skipped.")


def main() -> None:
    results = run_pipeline()
    print_summary(results)


if __name__ == "__main__":
    main()
