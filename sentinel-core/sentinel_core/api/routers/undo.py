"""Undo and execution history for the local dashboard."""

from fastapi import APIRouter, HTTPException

from sentinel_core.models.enums import TaskState

from ..models.requests import UndoRequest
from ..models.responses import UndoResponse
from ..receipts import WriterBusy, history, receipt_details, receipt_state, undo_recorded

router = APIRouter()


@router.get("/history")
def execution_history():
    return history()


@router.get("/history/{task_id}")
def execution_details(task_id: str):
    try:
        return receipt_details(task_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Execution receipt not found") from error


@router.post("/undo", response_model=UndoResponse)
def undo(request: UndoRequest):
    try:
        result = undo_recorded(request.task_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Execution receipt not found") from error
    except WriterBusy as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(
            status_code=409, detail="Undo blocked because the receipt or files changed"
        ) from error

    failed = bool(result.failed_actions or result.error_message)
    return UndoResponse(
        task_id=request.task_id,
        state=TaskState.FAILED if failed else TaskState.COMPLETED,
        undone_operations=result.successful_actions,
        failed_operations=result.failed_actions,
        message=(
            "Undo needs attention"
            if failed
            else (
                "Confirmed files restored. Check the remaining paths."
                if receipt_state(request.task_id) == "restored_with_uncertainty"
                else "Files restored"
            )
        ),
    )
