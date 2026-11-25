"""Undo and execution history for the local dashboard."""

from fastapi import APIRouter, HTTPException

from ..models.requests import UndoRequest
from ..models.responses import UndoResponse
from ..receipts import history, undo_recorded
from sentinel_core.models.enums import TaskState

router = APIRouter()


@router.get("/history")
def execution_history():
    return history()


@router.post("/undo", response_model=UndoResponse)
def undo(request: UndoRequest):
    try:
        result = undo_recorded(request.task_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Execution receipt not found") from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=409, detail="Undo blocked because the receipt or files changed") from error

    failed = bool(result.failed_actions or result.error_message)
    return UndoResponse(
        task_id=request.task_id,
        state=TaskState.FAILED if failed else TaskState.COMPLETED,
        undone_operations=result.successful_actions if not failed else 0,
        failed_operations=result.failed_actions,
        message="Undo needs attention" if failed else "Files restored",
    )
