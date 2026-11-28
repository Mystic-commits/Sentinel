"""
Plan Router

Endpoint for creating organization plans.
"""

import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException

from sentinel_core.models.enums import TaskState
from sentinel_core.models.planner import PlanSchema

from ..file_jobs import AI_WORKER_TIMEOUT, SCAN_WORKER_TIMEOUT, plan_folder, run_file_job
from ..limits import schedule_scan_job
from ..memory import save_task
from ..models.requests import PlanRequest
from ..models.responses import PlanResponse
from ..websocket.manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/plan", response_model=PlanResponse)
async def plan(request: PlanRequest, background_tasks: BackgroundTasks):
    """
    Create an AI-powered organization plan.

    Provide the absolute path of the folder to scan.

    Args:
        request: Plan request
        background_tasks: FastAPI background tasks

    Returns:
        PlanResponse with task_id and plan summary

    Example:
        POST /api/plan
        {
            "path": "/Users/test/Downloads",
            "user_prompt": "Organize by file type"
        }
    """
    from ..models.events import EventType, WebSocketEvent

    if not request.use_ai and request.user_prompt:
        raise HTTPException(status_code=422, detail="Custom instructions require local AI")

    task_id = f"task-{uuid.uuid4()}"

    async def perform_planning(task_id: str, path: str):
        try:
            await ws_manager.broadcast(
                WebSocketEvent(
                    event_type=EventType.PLANNING,
                    task_id=task_id,
                    message="Creating organization plan...",
                    data={},
                )
            )
            result = await run_file_job(
                plan_folder,
                task_id,
                path,
                request.use_ai,
                request.user_prompt or "",
                timeout=AI_WORKER_TIMEOUT if request.use_ai else SCAN_WORKER_TIMEOUT,
            )
            summary = result["summary"]
            plan_data = result["plan"]
            save_task(
                task_id,
                {
                    "plan": PlanSchema.model_validate(plan_data),
                    "summary": summary,
                    "state": TaskState.REVIEW,
                    "authorized_root": result["authorized_root"],
                    "source_identities": {
                        source: tuple(values)
                        for source, values in result["source_identities"].items()
                    },
                },
            )

            await ws_manager.broadcast(
                WebSocketEvent(
                    event_type=EventType.PLAN_READY,
                    task_id=task_id,
                    message=(
                        f"Partial scan: {summary.get('operations', 0)} operations proposed"
                        if summary["truncated"]
                        else f"Plan ready: {summary.get('operations', 0)} operations proposed"
                    ),
                    data={"plan": plan_data, "summary": summary},
                )
            )

        except Exception as e:
            save_task(task_id, {"state": TaskState.FAILED, "summary": str(e)})
            logger.error(f"Planning failed: {e}")
            await ws_manager.broadcast(
                WebSocketEvent(
                    event_type=EventType.ERROR,
                    task_id=task_id,
                    message=f"Planning failed: {e!s}",
                    data={"error": str(e)},
                )
            )

    # Start background task
    schedule_scan_job(background_tasks, perform_planning, task_id, request.path)

    save_task(task_id, {"state": TaskState.PLANNING})

    # Return initial response
    return PlanResponse(
        task_id=task_id,
        summary="Plan creation in progress...",
        total_actions=0,
        folders_to_create=0,
        state=TaskState.PLANNING,
        safety_approved=False,
        ambiguous_count=0,
    )
