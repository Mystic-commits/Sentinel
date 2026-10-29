"""
Plan Router

Endpoint for creating organization plans.
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from ..models.requests import PlanRequest
from ..models.responses import PlanResponse
from ..websocket.manager import ws_manager
from sentinel_core.models.enums import TaskState
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/plan", response_model=PlanResponse)
async def plan(request: PlanRequest, background_tasks: BackgroundTasks):
    """
    Create an AI-powered organization plan.

    Either provide a scan_id from a previous scan, or a path to scan first.

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
    import asyncio
    from ..models.events import WebSocketEvent, EventType, PlanReadyEvent
    from sentinel_core.cleanpc.pipeline import CleanPCPipeline
    from sentinel_core.planner.planner_agent import PlannerAgent
    from sentinel_core.safety.safety import SafetyValidator
    from sentinel_core.executor import Executor
    from sentinel_core.planner.ollama_client import OllamaClient

    # If neither provided, we assume default Clean My PC behavior (scan standard dirs)
    # if not request.scan_id and not request.path:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Either scan_id or path must be provided"
    #     )

    task_id = f"task-{uuid.uuid4()}"

    # Broadcast planning started
    await ws_manager.broadcast(
        WebSocketEvent(
            event_type=EventType.PLANNING,
            task_id=task_id,
            message="Creating organization plan...",
            data={"path": request.path or "from_scan"},
        )
    )

    logger.info(f"Plan creation initiated: {task_id}")

    async def perform_planning(task_id: str, path: str):
        try:
            # Initialize pipeline components
            # Note: In a real app, these should be dependency injected or singletons
            from ..config import settings

            ollama = OllamaClient(settings.ollama_url, timeout=settings.ollama_timeout)
            planner = PlannerAgent(ollama, model_name=settings.ollama_model)
            safety = SafetyValidator()
            executor = Executor()

            pipeline = CleanPCPipeline(planner, safety, executor)

            # Execute pipeline in thread to avoid blocking
            # Logic: If path provided, use it. If not, default to standard dirs.
            target_dirs = [path] if path else None

            logger.info(f"Running pipeline for {task_id}...")
            try:
                result = await pipeline.scan_and_plan(task_id, target_dirs=target_dirs)
            finally:
                ollama.close()

            # Extract results
            plan = result["plan"]
            summary = result["summary"]

            # Save plan to memory store
            from ..memory import save_task

            save_task(task_id, {"plan": plan, "summary": summary, "state": TaskState.REVIEW})

            # Broadcast plan ready

            # Convert PlanSchema to dict for JSON serialization
            plan_data = plan.dict() if hasattr(plan, "dict") else plan

            await ws_manager.broadcast(
                WebSocketEvent(
                    event_type=EventType.PLAN_READY,
                    task_id=task_id,
                    message=f"Plan ready: {summary.get('operations', 0)} operations proposed",
                    data={"plan": plan_data, "summary": summary},
                )
            )

        except Exception as e:
            logger.error(f"Planning failed: {e}")
            await ws_manager.broadcast(
                WebSocketEvent(
                    event_type=EventType.ERROR,
                    task_id=task_id,
                    message=f"Planning failed: {str(e)}",
                    data={"error": str(e)},
                )
            )

    # Start background task
    background_tasks.add_task(perform_planning, task_id, request.path)

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


@router.post("/plan/{task_id}/approve-all")
async def approve_all_plan(task_id: str):
    """
    Approve all pending operations in a plan.
    """
    from ..memory import get_task, save_task

    task_data = get_task(task_id)

    if not task_data or "plan" not in task_data:
        raise HTTPException(status_code=404, detail="Task not found")

    plan = task_data["plan"]

    # Update all pending operations to approved
    updated_actions = []
    for action in plan.actions:
        # Pydantic model dump/dict might be needed if plan is object
        # Assuming plan is Pydantic model or dict. In memory it's usually dict if loaded from json,
        # but here it might be kept as object if in-memory store is simple dict.
        # Let's assume it handles both.

        # Check if action is object or dict
        if hasattr(action, "status"):
            if action.status == "pending":
                action.status = "approved"
        elif isinstance(action, dict):
            if action.get("status") == "pending":
                action["status"] = "approved"

    # Save back to store
    save_task(task_id, {"plan": plan})

    return {"message": "All operations approved"}
