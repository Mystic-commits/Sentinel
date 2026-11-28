"""Run filesystem jobs in a worker that can be stopped at a deadline."""

import asyncio
import json
from collections.abc import Callable
from multiprocessing import get_context
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic

from .limits import MAX_MODEL_FILES, MAX_SCAN_ENTRIES, MAX_SCAN_SECONDS

SCAN_WORKER_TIMEOUT = 25
AI_WORKER_TIMEOUT = 90
WORKER_STARTUP_TIMEOUT = 45


def _write_result(job: Callable, args: tuple, result_path: Path, ready: Path) -> None:
    ready.touch()
    try:
        report = {"result": job(*args)}
    except Exception as error:
        report = {"error": str(error)}
    result_path.write_text(json.dumps(report), encoding="utf-8")


def run_file_job_sync(job: Callable, *args, timeout: float = SCAN_WORKER_TIMEOUT) -> dict:
    with TemporaryDirectory(prefix="sentinel-job-") as folder:
        result_path = Path(folder) / "result.json"
        ready = Path(folder) / "ready"
        worker = get_context("spawn").Process(
            target=_write_result, args=(job, args, result_path, ready), daemon=True
        )
        worker.start()
        try:
            startup_deadline = monotonic() + WORKER_STARTUP_TIMEOUT
            while not ready.exists() and worker.is_alive():
                remaining = startup_deadline - monotonic()
                if remaining <= 0:
                    raise TimeoutError("The folder worker timed out during startup.")
                worker.join(min(remaining, 0.05))
            worker.join(timeout)
            if worker.is_alive():
                raise TimeoutError("The folder job timed out. Check that the folder is available.")
            if worker.exitcode != 0:
                raise RuntimeError("The folder worker stopped before it could finish.")
            report = json.loads(result_path.read_text(encoding="utf-8"))
            if "error" in report:
                raise RuntimeError(report["error"])
            return report["result"]
        finally:
            if worker.is_alive():
                worker.kill()
                worker.join(1)
            if not worker.is_alive():
                worker.close()


async def run_file_job(job: Callable, *args, timeout: float = SCAN_WORKER_TIMEOUT) -> dict:
    return await asyncio.to_thread(run_file_job_sync, job, *args, timeout=timeout)


def _resolve_folder(path: str) -> Path:
    try:
        root = Path(path).resolve(strict=True)
        if root.is_dir():
            return root
    except (OSError, RuntimeError):
        pass
    raise ValueError("The selected folder is unavailable")


def scan_folder(path: str, max_depth: int) -> dict:
    from sentinel_core.scanner.scanner import Scanner

    root = _resolve_folder(path)
    scan = Scanner(
        str(root),
        max_depth=max_depth,
        include_previews=False,
        max_entries=MAX_SCAN_ENTRIES,
        max_seconds=MAX_SCAN_SECONDS,
    ).scan()
    return {
        "total_files": len(scan.files),
        "total_size_bytes": sum(file.size_bytes for file in scan.files),
        "errors": len(scan.errors),
        "truncated": scan.truncated,
    }


def plan_folder(task_id: str, path: str, use_ai: bool, instructions: str) -> dict:
    from sentinel_core.cleanpc.pipeline import CleanPCPipeline
    from sentinel_core.executor import Executor
    from sentinel_core.planner.ollama_client import OllamaClient
    from sentinel_core.planner.planner_agent import PlannerAgent
    from sentinel_core.safety import SafetyValidator

    from .receipts import snapshot_sources

    root = _resolve_folder(path)
    ollama = OllamaClient()
    try:
        pipeline = CleanPCPipeline(
            PlannerAgent(ollama, user_prompt=instructions), SafetyValidator(), Executor()
        )
        result = asyncio.run(
            pipeline.scan_and_plan(
                task_id,
                target_dirs=[str(root)],
                scoped_moves_only=True,
                max_entries=MAX_SCAN_ENTRIES,
                max_scan_seconds=MAX_SCAN_SECONDS,
                max_model_files=MAX_MODEL_FILES,
                use_ai=use_ai,
            )
        )
    finally:
        ollama.close()
    plan = result["plan"]
    return {
        "plan": plan.model_dump(mode="json"),
        "summary": result["summary"],
        "authorized_root": str(root),
        "source_identities": snapshot_sources(plan),
    }
