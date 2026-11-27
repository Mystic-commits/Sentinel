"""Run journaled filesystem changes in the isolated API worker."""

import sqlite3
from pathlib import Path

from sentinel_core.models.planner import PlanSchema
from sentinel_core.safety import SafetyValidator

from .config import settings
from .receipts import (
    WriterBusy,
    receipt_state,
    record_start,
    run_recorded,
    undo_recorded,
    verify_sources,
)

MUTATION_TIMEOUT = 90
PREFLIGHT_TIMEOUT = 15


def prepare_apply(
    plan: PlanSchema, expected: dict, root: str, database_url: str, record: bool = True
) -> dict:
    settings.database_url = database_url
    try:
        if Path(plan.scope_path).resolve(strict=True) != Path(root):
            return {"error": "Plan scope does not match the selected folder"}
        if not SafetyValidator().validate_plan(plan).is_safe:
            return {"error": "The approved actions failed safety validation"}
        verify_sources(plan, expected)
        if record:
            record_start(plan)
    except sqlite3.IntegrityError:
        return {"error": "This task already has an execution receipt"}
    except (OSError, ValueError):
        return {"error": "A source changed after the plan was prepared. Scan the folder again."}
    return {}


def apply_moves(plan: PlanSchema, expected: dict, database_url: str) -> dict:
    settings.database_url = database_url
    return run_recorded(plan, expected).model_dump(mode="json")


def undo_moves(task_id: str, database_url: str) -> dict:
    settings.database_url = database_url
    try:
        result = undo_recorded(task_id)
    except KeyError:
        return {"status": 404, "error": "Execution receipt not found"}
    except WriterBusy as error:
        return {"status": 409, "error": str(error)}
    except (OSError, ValueError):
        return {"status": 409, "error": "Undo blocked because the receipt or files changed"}
    return {
        "result": result.model_dump(mode="json"),
        "uncertain": receipt_state(task_id) == "restored_with_uncertainty",
    }
