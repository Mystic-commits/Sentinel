"""
Tasks Router

Endpoints for listing and retrieving task details.
"""

from fastapi import APIRouter, HTTPException, Query
from ..models.responses import TaskListResponse, TaskDetailResponse, TaskListItem
from sentinel_core.models.enums import TaskState
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(limit: int = Query(100, ge=1, le=100), offset: int = Query(0, ge=0)):
    """
    List all tasks.
    
    Args:
        limit: Maximum number of tasks to return
        offset: Number of tasks to skip
        
    Returns:
        TaskListResponse with list of tasks
        
    Example:
        GET /api/tasks?limit=10&offset=0
    """
    # Load from memory store
    from ..memory import task_store
    
    logger.info(f"Tasks list requested (limit={limit}, offset={offset})")
    
    tasks = []
    # Tasks are inserted when accepted and keep their position through state updates.
    for task_id in list(reversed(task_store))[offset:offset + limit]:
        data = task_store[task_id]
        plan = data.get("plan")
        summary = data.get("summary")
        tasks.append(TaskListItem(
            task_id=task_id,
            state=data["state"],
            created_at=data["created_at"],
            summary=plan.summary if plan else summary if isinstance(summary, str) else "",
        ))

    return TaskListResponse(
        tasks=tasks,
        total=len(task_store)
    )


@router.get("/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_task(task_id: str):
    """
    Get details for a specific task.
    
    Args:
        task_id: Task ID to retrieve
        
    Returns:
        TaskDetailResponse with task details
        
    Raises:
        HTTPException 404: If task not found
        
    Example:
        GET /api/tasks/task-abc-123
    """
    # Load from memory store
    from ..memory import get_task
    
    logger.info(f"Task detail requested: {task_id}")
    
    task_data = get_task(task_id)
    
    if not task_data:
        raise HTTPException(
            status_code=404,
            detail=f"Task not found: {task_id}"
        )
    
    plan = task_data.get("plan")
    summary = task_data.get("summary")
    result = task_data.get("result") or {}
    return TaskDetailResponse(
        task_id=task_id,
        state=task_data.get("state", TaskState.SCANNING),
        created_at=task_data.get("created_at") or datetime.utcnow(),
        plan=plan,
        summary=plan.summary if plan else summary if isinstance(summary, str) else "",
        planning_source=summary.get("planning_source") if isinstance(summary, dict) else None,
        total_actions=len(plan.actions) if plan else 0,
        successful_actions=result.get("success", 0),
        failed_actions=result.get("failed", 0),
    )
