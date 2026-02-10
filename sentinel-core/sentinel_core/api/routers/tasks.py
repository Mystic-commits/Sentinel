"""
Tasks Router

Endpoints for listing and retrieving task details.
"""

from fastapi import APIRouter, HTTPException
from ..models.responses import TaskListResponse, TaskDetailResponse, TaskListItem
from sentinel_core.models.enums import TaskState
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(limit: int = 100, offset: int = 0):
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
    # Sort by timestamp (if available) or insertion order (reversed)
    sorted_ids = sorted(task_store.keys(), reverse=True)
    
    for task_id in sorted_ids[offset:offset+limit]:
        data = task_store[task_id]
        # Construct TaskListItem from stored data
        # Note: This is a simplification. Real implementation would map fields.
        tasks.append(TaskListItem(
            task_id=task_id,
            state=data.get("state", TaskState.SCANNING), # Default to scanning if state missing
            created_at=datetime.utcnow(), # Placeholder timestamp
            summary=data.get("summary", "Task in progress") if isinstance(data.get("summary"), str) else "Task in progress",
            total_files=data.get("summary", {}).get("total_files", 0) if isinstance(data.get("summary"), dict) else 0
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
    
    # Construct response
    # This needs to map dictionary fields to Pydantic model
    return TaskDetailResponse(
        task_id=task_id,
        state=task_data.get("state", TaskState.SCANNING),
        created_at=datetime.utcnow(), # Placeholder
        plan=task_data.get("plan"),
        summary=task_data.get("summary") if isinstance(task_data.get("summary"), dict) else {},
        result=task_data.get("result")
    )
