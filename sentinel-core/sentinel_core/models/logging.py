from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, JSON
from sentinel_core.models.enums import ActionType, TaskStatus
from typing import List

class ExecutionLogEntry(SQLModel, table=True):
    """Audit log of every action taken."""
    __tablename__ = "execution_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: str = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.now)
    action_type: ActionType
    source_path: str
    destination_path: Optional[str] = None
    status: str # "success", "failed", "rolled_back"
    error_message: Optional[str] = None
    
class TaskRecord(SQLModel, table=True):
    """Record of a high-level user task."""
    __tablename__ = "tasks"
    
    task_id: str = Field(primary_key=True)
    user_prompt: str
    created_at: datetime = Field(default_factory=datetime.now)
    status: TaskStatus = Field(default=TaskStatus.SCANNING)
    
    # Store large blobs as JSON strings or separate file references
    scan_result_json: Optional[str] = Field(default=None, sa_type=JSON) # type: ignore
    plan_json: Optional[str] = Field(default=None, sa_type=JSON) # type: ignore
    
    undo_available: bool = True
