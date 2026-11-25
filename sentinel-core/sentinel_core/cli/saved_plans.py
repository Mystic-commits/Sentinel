"""Persist the reviewed CLI plan and its source snapshot together."""

import json

from sentinel_core.api.receipts import database, snapshot_sources
from sentinel_core.models.planner import PlanSchema


def save_plan(plan: PlanSchema) -> None:
    snapshot = snapshot_sources(plan)
    with database() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS cli_plans (
                task_id TEXT PRIMARY KEY,
                plan TEXT NOT NULL,
                source_snapshot TEXT NOT NULL
            )
        """)
        connection.execute(
            "INSERT INTO cli_plans VALUES (?, ?, ?)",
            (plan.task_id, plan.model_dump_json(), json.dumps(snapshot)),
        )


def load_plan(task_id: str) -> tuple[PlanSchema, dict[str, tuple[int, ...]]] | None:
    with database() as connection:
        exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'cli_plans'"
        ).fetchone()
        if not exists:
            return None
        row = connection.execute(
            "SELECT plan, source_snapshot FROM cli_plans WHERE task_id = ?", (task_id,)
        ).fetchone()
    if row is None:
        return None
    return PlanSchema.model_validate_json(row[0]), {
        path: tuple(identity) for path, identity in json.loads(row[1]).items()
    }
