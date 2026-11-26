"""Compare Sentinel planners using generated fixtures without applying changes."""

import argparse
import asyncio
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from sentinel_core.cleanpc.pipeline import CleanPCPipeline
from sentinel_core.executor import Executor
from sentinel_core.planner.ollama_client import OllamaClient
from sentinel_core.planner.planner_agent import PlannerAgent
from sentinel_core.safety import SafetyValidator

CASES = {
    "group_by_type": (
        ("invoice.txt", "coast.jpg", "opaque.unknown"),
        "Group the invoice into document and the photo into image. Leave opaque.unknown alone.",
        {"invoice.txt": "document/invoice.txt", "coast.jpg": "image/coast.jpg"},
    ),
    "custom_destination": (
        ("Résumé notes.txt",),
        "Move the notes into a subfolder named Projects and preserve the filename.",
        {"Résumé notes.txt": "Projects/Résumé notes.txt"},
    ),
    "already_organized": (
        ("document/report.txt", "unclassified.unknown"),
        "Leave files that are already organized or whose type is unclear in place.",
        {},
    ),
}


def score_plan(plan, folder: Path, expected: dict[str, str]) -> dict:
    proposed = []
    outside_scope = 0
    for action in plan.actions:
        source = Path(action.source_path or "").resolve()
        destination = Path(action.destination_path or "").resolve()
        if not source.is_relative_to(folder) or not destination.is_relative_to(folder):
            outside_scope += 1
            continue
        proposed.append((source.relative_to(folder).as_posix(), destination.relative_to(folder).as_posix()))

    targets = set(expected.items())
    observed = set(proposed)
    return {
        "expected": len(targets),
        "matched": len(targets & observed),
        "unexpected": len(observed - targets),
        "duplicates": len(proposed) - len(observed),
        "outside_scope": outside_scope,
        "moves": [{"from": source, "to": destination} for source, destination in sorted(observed)],
    }


async def evaluate(mode: str, model: str) -> list[dict]:
    results = []
    with TemporaryDirectory(prefix="sentinel-planner-eval-") as directory:
        for name, (inventory, instructions, expected) in CASES.items():
            folder = (Path(directory) / name).resolve()
            for filename in inventory:
                path = folder / filename
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("Synthetic evaluation fixture", encoding="utf-8")

            for requested in ("rules", "ai") if mode == "both" else (mode,):
                ollama = OllamaClient()
                try:
                    pipeline = CleanPCPipeline(
                        PlannerAgent(ollama, model_name=model, user_prompt=instructions),
                        SafetyValidator(), Executor(),
                    )
                    start = perf_counter()
                    result = await pipeline.scan_and_plan(
                        f"eval-{name}-{requested}", target_dirs=[str(folder)],
                        scoped_moves_only=True, use_ai=requested == "ai",
                    )
                    results.append({
                        "case": name,
                        "requested": requested,
                        "actual": result["summary"]["planning_source"],
                        "elapsed_seconds": round(perf_counter() - start, 3),
                        **score_plan(result["plan"], folder, expected),
                    })
                finally:
                    ollama.close()
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("rules", "ai", "both"), default="rules")
    parser.add_argument("--model", default="llama2")
    args = parser.parse_args()
    results = asyncio.run(evaluate(args.mode, args.model))
    print(json.dumps({"model": args.model, "results": results}, ensure_ascii=False, indent=2))
    return int(any(result["outside_scope"] for result in results))


if __name__ == "__main__":
    raise SystemExit(main())
