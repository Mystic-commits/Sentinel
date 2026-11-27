"""
Response Schemas

Pydantic models for API responses.
"""

from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel

from sentinel_core.models.enums import TaskState
from sentinel_core.models.planner import PlanSchema


class ScanResponse(BaseModel):
    """Response from scan endpoint."""

    scan_id: str
    root_path: str
    total_files: int
    total_size_bytes: int
    state: TaskState

    class Config:
        json_schema_extra: ClassVar = {
            "example": {
                "scan_id": "scan-abc-123",
                "root_path": "/Users/test/Downloads",
                "total_files": 247,
                "total_size_bytes": 1234567890,
                "state": "SCANNING",
            }
        }


class PlanResponse(BaseModel):
    """Response from plan endpoint."""

    task_id: str
    summary: str
    total_actions: int
    folders_to_create: int
    state: TaskState
    safety_approved: bool
    ambiguous_count: int = 0

    class Config:
        json_schema_extra: ClassVar = {
            "example": {
                "task_id": "task-abc-123",
                "summary": "Organize Downloads folder by file type",
                "total_actions": 142,
                "folders_to_create": 5,
                "state": "PLANNING",
                "safety_approved": False,
                "ambiguous_count": 3,
            }
        }


class PreviewResponse(BaseModel):
    """Response from preview endpoint."""

    task_id: str
    preview_text: str
    format: str


class ExecuteResponse(BaseModel):
    """Response from execute endpoint."""

    task_id: str
    state: TaskState
    successful_actions: int
    failed_actions: int
    message: str | None = None

    class Config:
        json_schema_extra: ClassVar = {
            "example": {
                "task_id": "task-abc-123",
                "state": "EXECUTING",
                "successful_actions": 0,
                "failed_actions": 0,
                "message": "Execution started",
            }
        }


class UndoResponse(BaseModel):
    """Response from undo endpoint."""

    task_id: str
    state: TaskState
    undone_operations: int
    failed_operations: int
    message: str | None = None


class TaskListItem(BaseModel):
    """Single task in list."""

    task_id: str
    state: TaskState
    summary: str
    created_at: datetime
    completed_at: datetime | None = None


class TaskListResponse(BaseModel):
    """Response from tasks list endpoint."""

    tasks: list[TaskListItem]
    total: int


class TaskDetailResponse(BaseModel):
    """Response from task detail endpoint."""

    task_id: str
    state: TaskState
    summary: str
    created_at: datetime
    plan: PlanSchema | None = None
    planning_source: str | None = None
    completed_at: datetime | None = None
    total_actions: int
    successful_actions: int
    failed_actions: int


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    database_connected: bool = True

    class Config:
        json_schema_extra: ClassVar = {
            "example": {"status": "healthy", "version": "0.1.0", "database_connected": True}
        }
