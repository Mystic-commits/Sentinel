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

    Provide an explicit folder path to scan first.

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

    from pathlib import Path

    target = Path(request.path).expanduser()
    if not target.is_absolute() or not target.is_dir():
        raise HTTPException(status_code=400, detail="Choose an existing absolute folder path.")

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
            # Limit planning to the explicitly selected folder.
            target_dirs = [path]

            logger.info(f"Running pipeline for {task_id}...")
            try:
                result = await pipeline.scan_and_plan(
                    task_id,
                    target_dirs=target_dirs,
                    user_prompt=request.user_prompt or "",
                    planning_strategy=request.strategy,
                )
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
            from ..memory import save_task

            save_task(task_id, {"state": TaskState.FAILED, "error": str(e)})
            logger.error(f"Planning failed: {e}")
            await ws_manager.broadcast(
                WebSocketEvent(
                    event_type=EventType.ERROR,
                    task_id=task_id,
                    message=f"Planning failed: {str(e)}",
                    data={"error": str(e)},
                )
            )

    from ..memory import save_task

    save_task(
        task_id,
        {
            "state": TaskState.PLANNING,
            "summary": request.user_prompt or "Preparing your organization preview",
        },
    )

    # Start background task
    background_tasks.add_task(perform_planning, task_id, str(target.resolve()))

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
