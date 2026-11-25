"""Durable receipts for dashboard moves with conservative recovery."""

import json
import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path

from sentinel_core.executor.executor import execute_plan
from sentinel_core.models.planner import PlanSchema
from sentinel_core.safety import SafetyValidator

from .config import settings


@contextmanager
def database():
    path = Path(settings.database_url).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS api_receipts (
                task_id TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                plan TEXT NOT NULL,
                identities TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        yield connection


def identity(path: str) -> tuple[int, ...]:
    file = Path(path)
    if file.is_symlink() or not file.is_file():
        raise ValueError("Expected a regular file")
    info = file.stat()
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def record_start(plan: PlanSchema) -> None:
    with database() as connection:
        connection.execute(
            "INSERT INTO api_receipts (task_id, state, plan) VALUES (?, 'executing', ?)",
            (plan.task_id, plan.model_dump_json()),
        )


def run_recorded(plan: PlanSchema):
    try:
        if not SafetyValidator().validate_plan(plan).is_safe:
            raise ValueError("The approved plan failed filesystem revalidation")
        result = execute_plan(plan)
        failed = bool(result.failed_actions or result.error_message)
        identities = None if failed else [identity(action.destination_path) for action in plan.actions]
        with database() as connection:
            connection.execute(
                "UPDATE api_receipts SET state = ?, identities = ? WHERE task_id = ?",
                ("failed" if failed else "completed", json.dumps(identities), plan.task_id),
            )
        return result
    except Exception:
        with database() as connection:
            connection.execute(
                "UPDATE api_receipts SET state = 'failed' WHERE task_id = ?", (plan.task_id,)
            )
        raise


def history():
    with database() as connection:
        rows = connection.execute(
            "SELECT task_id, state, created_at FROM api_receipts ORDER BY created_at DESC, task_id"
        ).fetchall()
    return [{"task_id": task_id, "state": state, "created_at": created_at}
            for task_id, state, created_at in rows]


def undo_recorded(task_id: str):
    with database() as connection:
        row = connection.execute(
            "SELECT state, plan, identities FROM api_receipts WHERE task_id = ?", (task_id,)
        ).fetchone()
        if not row:
            raise KeyError(task_id)
        state, plan_json, identities_json = row
        if state != "completed":
            raise ValueError("Only a completed, eligible receipt can be undone")
        plan = PlanSchema.model_validate_json(plan_json)
        identities = json.loads(identities_json)
        reverse_actions = []
        for action, expected in reversed(list(zip(plan.actions, identities, strict=True))):
            if list(identity(action.destination_path)) != expected:
                raise ValueError("A destination file changed since execution")
            original = Path(action.source_path)
            if original.exists() or original.is_symlink():
                raise ValueError("An original path is occupied")
            reverse_actions.append(action.model_copy(update={
                "source_path": action.destination_path,
                "destination_path": action.source_path,
            }))
        reversal = plan.model_copy(update={"actions": reverse_actions})
        if not SafetyValidator().validate_plan(reversal).is_safe:
            raise ValueError("The reversal failed folder safety validation")
        claimed = connection.execute(
            "UPDATE api_receipts SET state = 'undoing' WHERE task_id = ? AND state = 'completed'",
            (task_id,),
        ).rowcount
        if claimed != 1:
            raise ValueError("The receipt changed before undo")

    result = execute_plan(reversal)
    failed = bool(result.failed_actions or result.error_message)
    with database() as connection:
        connection.execute(
            "UPDATE api_receipts SET state = ? WHERE task_id = ?",
            ("undo_failed" if failed else "undone", task_id),
        )
    return result
