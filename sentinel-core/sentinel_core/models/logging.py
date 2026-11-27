from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import JSON, Field, SQLModel

from sentinel_core.models.enums import ActionType, TaskStatus


class ExecutionLogEntry(SQLModel, table=True):
    """Audit log of every action taken."""

    __tablename__ = "execution_logs"

    id: int | None = Field(
        default=None, primary_key=True
    )  # explicit annotation required by Pydantic v2
    task_id: str = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.now, sa_type=DateTime)
    action_type: ActionType
    source_path: str
    destination_path: str | None = None
    status: str  # "success", "failed", "rolled_back"
    error_message: str | None = None


class TaskRecord(SQLModel, table=True):
    """Record of a high-level user task."""

    __tablename__ = "tasks"

    task_id: str = Field(primary_key=True)
    user_prompt: str
    created_at: datetime = Field(default_factory=datetime.now, sa_type=DateTime)
    status: TaskStatus = Field(default=TaskStatus.SCANNING)

    # Store large blobs as JSON strings or separate file references
    scan_result_json: str | None = Field(default=None, sa_type=JSON)  # type: ignore
    plan_json: str | None = Field(default=None, sa_type=JSON)  # type: ignore

    undo_available: bool = True
