"""
Execute Router

Endpoint for executing organization plans.

CRITICAL: This router enforces safety validation - execution cannot proceed without it.
"""

import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException

from sentinel_core.models.enums import TaskState

from ..models.requests import ExecuteRequest
from ..models.responses import ExecuteResponse
from ..websocket.manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest, background_tasks: BackgroundTasks):
    """
    Execute an organization plan.

    SAFETY GUARANTEE: This endpoint ALWAYS validates plans through SafetyValidator.
    The skip_safety parameter is rejected - it exists only to document that
    safety cannot be bypassed.

    Args:
        request: Execute request with task_id
        background_tasks: FastAPI background tasks

    Returns:
        ExecuteResponse with execution status

    Raises:
        HTTPException 403: If skip_safety is True
        HTTPException 400: If plan fails safety validation
        HTTPException 404: If task not found

    Example:
        POST /api/execute
        {
            "task_id": "task-abc-123"
        }
    """
    # CRITICAL SAFETY CHECK: NEVER allow skipping validation
    if request.skip_safety:
        logger.warning(f"Execution rejected: attempt to skip safety for {request.task_id}")
        raise HTTPException(
            status_code=403,
            detail="Safety validation cannot be skipped. This is a non-negotiable system invariant.",
        )

    # Load plan from memory store
    from ..memory import get_task, save_task

    task_data = get_task(request.task_id)

    if not task_data or "plan" not in task_data:
        raise HTTPException(
            status_code=404, detail=f"Task not found or no plan available: {request.task_id}"
        )

    plan = task_data["plan"]

    import asyncio
    from pathlib import Path

    from sentinel_core.safety import SafetyValidator

    from ..models.events import EventType, WebSocketEvent

    if task_data.get("state") != TaskState.REVIEW:
        raise HTTPException(status_code=409, detail="Task is no longer available for review")

    indices = request.approved_action_indices
    if len(set(indices)) != len(indices) or any(i < 0 or i >= len(plan.actions) for i in indices):
        raise HTTPException(status_code=422, detail="Invalid approved action indices")

    authorized_root = task_data.get("authorized_root")
    if not authorized_root or Path(plan.scope_path).resolve() != Path(authorized_root):
        raise HTTPException(status_code=409, detail="Plan scope does not match the selected folder")

    plan = plan.model_copy(
        update={
            "actions": [plan.actions[i] for i in sorted(indices)],
            "folders_to_create": [],
        },
        deep=True,
    )
    from sentinel_core.models.enums import ActionType

    if any(action.type not in (ActionType.MOVE, ActionType.RENAME) for action in plan.actions):
        raise HTTPException(status_code=422, detail="This preview supports moves and renames")
    if not SafetyValidator().validate_plan(plan).is_safe:
        raise HTTPException(status_code=409, detail="The approved actions failed safety validation")

    import sqlite3

    from ..receipts import record_start, run_recorded, verify_sources

    expected = task_data.get("source_identities", {})
    try:
        verify_sources(plan, expected)
        record_start(plan)
    except (OSError, ValueError) as error:
        raise HTTPException(
            status_code=409, detail="A source changed after review. Scan the folder again."
        ) from error
    except sqlite3.IntegrityError as error:
        raise HTTPException(
            status_code=409, detail="This task already has an execution receipt"
        ) from error

    save_task(request.task_id, {"state": TaskState.EXECUTING})

    async def perform_execution(task_id: str, plan):
        try:

            # Broadcast start
            await ws_manager.broadcast(
                WebSocketEvent(
                    event_type=EventType.EXECUTION_PROGRESS,
                    task_id=task_id,
                    message="Starting execution...",
                    data={"progress": 0},
                )
            )

            # Call the REAL executor directly — no pipeline, no class wrapper
            result = await asyncio.to_thread(run_recorded, plan, expected)

            logger.warning(
                f"[EXEC] Result: succeeded={result.successful_actions}, failed={result.failed_actions}, error={result.error_message}"
            )

            failed = bool(result.failed_actions or result.error_message)
            state = TaskState.FAILED if failed else TaskState.COMPLETED

            # Broadcast outcome
            await ws_manager.broadcast(
                WebSocketEvent(
                    event_type=EventType.TASK_FAILED if failed else EventType.TASK_COMPLETED,
                    task_id=task_id,
                    message=f"Execution completed: {result.successful_actions} succeeded, {result.failed_actions} failed",
                    data={
                        "result": {
                            "success": result.successful_actions,
                            "failed": result.failed_actions,
                            "error": result.error_message,
                        },
                        "progress": 100,
                    },
                )
            )

            # Update store
            save_task(
                task_id,
                {
                    "state": state,
                    "result": {
                        "success": result.successful_actions,
                        "failed": result.failed_actions,
                    },
                },
            )

        except Exception as e:
            import traceback

            logger.error(f"[EXEC] Execution FAILED: {e}")
            logger.error(f"[EXEC] Traceback: {traceback.format_exc()}")
            await ws_manager.broadcast(
                WebSocketEvent(
                    event_type=EventType.TASK_FAILED,
                    task_id=task_id,
                    message=f"Execution failed: {e!s}",
                    data={"error": str(e)},
                )
            )
            save_task(task_id, {"state": TaskState.FAILED, "error": str(e)})

    # Start execution in background
    background_tasks.add_task(perform_execution, request.task_id, plan)

    logger.info(f"Execution initiated: {request.task_id}")

    return ExecuteResponse(
        task_id=request.task_id,
        state=TaskState.EXECUTING,
        successful_actions=0,
        failed_actions=0,
        message="Execution initiated",
    )
