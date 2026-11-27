"""Durable apply and undo receipts shared by the dashboard and CLI."""

import json
import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path
from stat import FILE_ATTRIBUTE_REPARSE_POINT, S_ISDIR, S_ISREG

from sentinel_core.executor.executor import execute_plan
from sentinel_core.models.enums import ActionType
from sentinel_core.models.executor import ExecutionResult
from sentinel_core.models.planner import PlanAction, PlanSchema
from sentinel_core.safety import SafetyValidator

from .config import settings


class WriterBusyError(ValueError):
    """Another Sentinel process owns the local filesystem writer."""


WriterBusy = WriterBusyError


def database_path() -> Path:
    path = Path(settings.database_url).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def writer():
    # Keep the lock in a separate database so receipts can commit between moves.
    path = database_path()
    with closing(sqlite3.connect(path.with_name(f"{path.name}.writer"), timeout=0)) as connection:
        try:
            connection.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as error:
            if error.sqlite_errorcode not in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED):
                raise
            raise WriterBusyError(
                "Another file operation is running. Try again after it finishes."
            ) from error
        yield


@contextmanager
def database():
    with closing(sqlite3.connect(database_path())) as connection, connection:
        connection.row_factory = sqlite3.Row
        connection.execute("""
            CREATE TABLE IF NOT EXISTS api_receipts (
                task_id TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                plan TEXT NOT NULL,
                identities TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS receipt_operations (
                task_id TEXT NOT NULL,
                action_index INTEGER NOT NULL,
                apply_state TEXT NOT NULL DEFAULT 'pending',
                undo_state TEXT NOT NULL DEFAULT 'pending',
                destination_identity TEXT,
                PRIMARY KEY (task_id, action_index)
            )
        """)
        yield connection


def identity(path: str) -> tuple[int, ...]:
    info = Path(path).lstat()
    if not S_ISREG(info.st_mode):
        raise ValueError("Expected a regular file")
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def snapshot_sources(plan: PlanSchema) -> dict[str, tuple[int, ...]]:
    snapshot = {}
    for action in plan.actions:
        source = action.source_path
        if not source:
            continue
        try:
            snapshot[source] = identity(source)
        except (OSError, ValueError):
            continue
    return snapshot


def verify_sources(plan: PlanSchema, expected: dict[str, tuple[int, ...]]) -> None:
    for action in plan.actions:
        path = action.source_path
        if not path or path not in expected or identity(path) != expected[path]:
            raise ValueError("A source changed after the plan was prepared")


def record_start(plan: PlanSchema) -> None:
    with database() as connection:
        connection.execute(
            "INSERT INTO api_receipts (task_id, state, plan) VALUES (?, 'queued', ?)",
            (plan.task_id, plan.model_dump_json()),
        )
        connection.executemany(
            "INSERT INTO receipt_operations (task_id, action_index) VALUES (?, ?)",
            [(plan.task_id, index) for index in range(len(plan.actions))],
        )


def _set_state(task_id: str, state: str) -> None:
    with database() as connection:
        connection.execute("UPDATE api_receipts SET state = ? WHERE task_id = ?", (state, task_id))


def _reconcile_interrupted() -> None:
    # The caller holds the writer lock. Any unfinished running receipt is stale.
    with database() as connection:
        connection.execute("""
            UPDATE api_receipts SET state = CASE state
                WHEN 'executing' THEN 'interrupted'
                WHEN 'undoing' THEN 'undo_interrupted'
            END WHERE state IN ('executing', 'undoing')
        """)


def _check_directory_chain(root: Path, file: Path) -> None:
    """Reject links and Windows reparse points within the approved folder."""
    if not root.is_absolute() or not file.is_absolute() or not file.is_relative_to(root):
        raise ValueError("A move failed folder safety validation")
    relative = file.relative_to(root)
    if not relative.parts or ".." in relative.parts:
        raise ValueError("A move failed folder safety validation")
    directory = root
    for part in ("", *relative.parts[:-1]):
        directory /= part
        try:
            entry = directory.lstat()
        except FileNotFoundError:
            if directory == root:
                raise
            break
        if not S_ISDIR(entry.st_mode) or (
            getattr(entry, "st_file_attributes", 0) & FILE_ATTRIBUTE_REPARSE_POINT
        ):
            raise ValueError("A folder in the move path is a link or reparse point")


def _check_move(plan: PlanSchema, action: PlanAction, expected: tuple[int, ...]) -> None:
    if (
        action.type not in (ActionType.MOVE, ActionType.RENAME)
        or not action.source_path
        or not action.destination_path
    ):
        raise ValueError("Only file moves and renames are supported")
    root = Path(plan.scope_path)
    _check_directory_chain(root, Path(action.source_path))
    _check_directory_chain(root, Path(action.destination_path))
    if identity(action.source_path) != expected:
        raise ValueError("A source file changed before the move")
    destination = Path(action.destination_path)
    if destination.exists() or destination.is_symlink():
        raise ValueError("A destination is already occupied")
    if not SafetyValidator().validate_plan(_single_move(plan, action)).is_safe:
        raise ValueError("A move failed folder safety validation")


def _single_move(plan: PlanSchema, action: PlanAction) -> PlanSchema:
    return plan.model_copy(update={"actions": [action], "folders_to_create": []})


def _recorded_moves(plan, operations, *, undo: bool = False) -> ExecutionResult:
    state_column = "undo_state" if undo else "apply_state"
    succeeded = 0
    error_message = None
    for index, action, expected in operations:
        try:
            _check_move(plan, action, expected)
            with database() as connection:
                connection.execute(
                    f"UPDATE receipt_operations SET {state_column} = 'started' "
                    "WHERE task_id = ? AND action_index = ?",
                    (plan.task_id, index),
                )
            _check_move(plan, action, expected)
            result = execute_plan(_single_move(plan, action))
            if result.failed_actions or result.error_message:
                raise ValueError(result.error_message or "File operation did not complete")
            _check_directory_chain(Path(plan.scope_path), Path(action.destination_path))
            moved = identity(action.destination_path)
            # Rename can change ctime. The device, inode, size and mtime should match.
            if moved[:-1] != expected[:-1]:
                raise ValueError("The destination changed during the move. Inspect the receipt.")
            with database() as connection:
                if undo:
                    connection.execute(
                        "UPDATE receipt_operations SET undo_state = 'done' WHERE task_id = ? AND action_index = ?",
                        (plan.task_id, index),
                    )
                else:
                    connection.execute(
                        "UPDATE receipt_operations SET apply_state = 'done', destination_identity = ? "
                        "WHERE task_id = ? AND action_index = ?",
                        (json.dumps(moved), plan.task_id, index),
                    )
            succeeded += 1
        except (OSError, ValueError, sqlite3.Error) as error:
            error_message = str(error)
            break

    return ExecutionResult(
        task_id=plan.task_id,
        total_actions=len(operations),
        successful_actions=succeeded,
        failed_actions=int(error_message is not None),
        execution_logs=[],
        error_message=error_message,
    )


def run_recorded(plan: PlanSchema, expected: dict[str, tuple[int, ...]]) -> ExecutionResult:
    try:
        with writer():
            _reconcile_interrupted()
            _set_state(plan.task_id, "executing")
            verify_sources(plan, expected)
            operations = [
                (i, action, expected[action.source_path]) for i, action in enumerate(plan.actions)
            ]
            for _, action, fingerprint in operations:
                _check_move(plan, action, fingerprint)
            result = _recorded_moves(plan, operations)
            if result.error_message is None:
                _set_state(plan.task_id, "completed")
            else:
                _set_state(plan.task_id, "partial" if result.successful_actions else "failed")
            return result
    except Exception:
        _set_state(plan.task_id, "failed")
        raise


def _history():
    with database() as connection:
        rows = connection.execute("""
            SELECT r.task_id, r.state, r.created_at, COUNT(o.action_index) AS operation_count,
                   SUM(CASE WHEN o.apply_state = 'done' THEN 1 ELSE 0 END) AS applied_count,
                   SUM(CASE WHEN o.undo_state = 'done' THEN 1 ELSE 0 END) AS restored_count,
                   SUM(CASE WHEN o.apply_state = 'started' OR o.undo_state = 'started' THEN 1 ELSE 0 END) AS uncertain_count
            FROM api_receipts AS r LEFT JOIN receipt_operations AS o ON r.task_id = o.task_id
            GROUP BY r.task_id
            ORDER BY r.created_at DESC, r.task_id
        """).fetchall()
    return [dict(row) for row in rows]


def history():
    try:
        with writer():
            _reconcile_interrupted()
            return _history()
    except WriterBusyError:
        return _history()


def receipt_details(task_id: str):
    with database() as connection:
        receipt = connection.execute(
            "SELECT plan FROM api_receipts WHERE task_id = ?", (task_id,)
        ).fetchone()
        if receipt is None:
            raise KeyError(task_id)
        rows = connection.execute(
            "SELECT action_index, apply_state, undo_state FROM receipt_operations "
            "WHERE task_id = ? ORDER BY action_index",
            (task_id,),
        ).fetchall()
    plan = PlanSchema.model_validate_json(receipt["plan"])
    return [
        {
            "index": row["action_index"] + 1,
            "source": plan.actions[row["action_index"]].source_path,
            "destination": plan.actions[row["action_index"]].destination_path,
            "apply_state": row["apply_state"],
            "undo_state": row["undo_state"],
        }
        for row in rows
    ]


def receipt_state(task_id: str) -> str | None:
    with database() as connection:
        row = connection.execute(
            "SELECT state FROM api_receipts WHERE task_id = ?", (task_id,)
        ).fetchone()
    return row["state"] if row else None


def undo_recorded(task_id: str) -> ExecutionResult:
    with writer(), database() as connection:
        _reconcile_interrupted()
        row = connection.execute(
            "SELECT state, plan, identities FROM api_receipts WHERE task_id = ?", (task_id,)
        ).fetchone()
        if row is None:
            raise KeyError(task_id)
        if row["state"] not in ("completed", "partial"):
            raise ValueError("Only a completed or partially completed receipt can be undone")

        plan = PlanSchema.model_validate_json(row["plan"])
        completed = connection.execute(
            """SELECT action_index, destination_identity FROM receipt_operations
               WHERE task_id = ? AND apply_state = 'done' ORDER BY action_index DESC""",
            (task_id,),
        ).fetchall()
        if not completed and row["state"] == "completed" and row["identities"]:
            # Receipts written before per-operation journaling stored one identity list.
            identities = json.loads(row["identities"])
            if len(identities) != len(plan.actions):
                raise ValueError("The saved receipt is incomplete")
            legacy = [(index, json.dumps(value)) for index, value in enumerate(identities)]
            connection.executemany(
                """INSERT INTO receipt_operations (task_id, action_index, apply_state, destination_identity)
                   VALUES (?, ?, 'done', ?)""",
                [(task_id, index, value) for index, value in legacy],
            )
            completed = list(reversed(legacy))
        if not completed:
            raise ValueError("The receipt has no confirmed moves to undo")

        operations = []
        for index, stored in completed:
            action = plan.actions[index]
            reversal = action.model_copy(
                update={
                    "source_path": action.destination_path,
                    "destination_path": action.source_path,
                }
            )
            fingerprint = tuple(json.loads(stored))
            _check_move(plan, reversal, fingerprint)
            operations.append((index, reversal, fingerprint))
        connection.execute(
            "UPDATE api_receipts SET state = 'undoing' WHERE task_id = ?", (task_id,)
        )
        connection.commit()

        result = _recorded_moves(plan, operations, undo=True)
        uncertain = connection.execute(
            "SELECT 1 FROM receipt_operations WHERE task_id = ? AND apply_state = 'started'",
            (task_id,),
        ).fetchone()
        if result.error_message:
            _set_state(task_id, "undo_failed")
        else:
            _set_state(task_id, "restored_with_uncertainty" if uncertain else "undone")
        return result
