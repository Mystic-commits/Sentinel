"""Read persisted task history and execution receipts."""

from fastapi import APIRouter, HTTPException, Query
from ..memory import task_store
from ..models.responses import TaskListResponse, TaskListItem, TaskDetailResponse

router = APIRouter()


def title(data):
    summary = data.get("summary")
    if isinstance(summary, str):
        return summary
    plan = data.get("plan")
    return plan.summary if plan else "Task in progress"


@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    items = sorted(
        ((key, task_store[key]) for key in task_store),
        key=lambda item: item[1]["created_at"],
        reverse=True,
    )
    return TaskListResponse(
        total=len(items),
        tasks=[
            TaskListItem(
                task_id=key,
                state=data["state"],
                summary=title(data),
                created_at=data["created_at"],
                completed_at=data.get("completed_at"),
            )
            for key, data in items[offset : offset + limit]
        ],
    )


@router.get("/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_task(task_id: str):
    data = task_store.get(task_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Task not found")
    result = data.get("result") or {}
    plan = data.get("plan")
    return TaskDetailResponse(
        task_id=task_id,
        state=data["state"],
        summary=title(data),
        created_at=data["created_at"],
        completed_at=data.get("completed_at"),
        total_actions=len(plan.actions) if plan else 0,
        successful_actions=result.get("success", 0),
        failed_actions=result.get("failed", 0),
        plan=plan.model_dump(mode="json") if plan else None,
        result=result,
        receipts=data.get("receipts", []),
        approved_actions=data.get("approved_actions", []),
        planning_warning=(
            data.get("summary", {}).get("planning_warning")
            if isinstance(data.get("summary"), dict)
            else None
        ),
        recovery_required=data.get("recovery_required", False),
        error=data.get("error"),
    )
