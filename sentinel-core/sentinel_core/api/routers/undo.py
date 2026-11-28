"""Undo and execution history for the local dashboard."""

from fastapi import APIRouter, HTTPException

from sentinel_core.models.enums import TaskState
from sentinel_core.models.executor import ExecutionResult

from ..config import settings
from ..file_jobs import run_file_job
from ..models.requests import UndoRequest
from ..models.responses import UndoResponse
from ..mutation_jobs import MUTATION_TIMEOUT, undo_moves
from ..receipts import history, receipt_details

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
async def undo(request: UndoRequest):
    try:
        outcome = await run_file_job(
            undo_moves,
            request.task_id,
            settings.database_url,
            timeout=MUTATION_TIMEOUT,
        )
    except TimeoutError as error:
        raise HTTPException(
            504, "Restore timed out. Check execution history before retrying."
        ) from error
    except RuntimeError as error:
        raise HTTPException(503, "Restore could not finish. Check execution history.") from error
    if "error" in outcome:
        raise HTTPException(outcome["status"], outcome["error"])
    result = ExecutionResult.model_validate(outcome["result"])

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
                if outcome["uncertain"]
                else "Files restored"
            )
        ),
    )
