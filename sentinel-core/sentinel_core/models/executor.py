"""
Executor module models.

Defines result types for plan execution and undo operations.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from sentinel_core.models.enums import ActionType
from sentinel_core.models.logging import ExecutionLogEntry


class ExecutionResult(BaseModel):
    """
    Result of executing a plan.
    
    Attributes:
        task_id: Unique identifier for the task
        total_actions: Total number of actions attempted
        successful_actions: Number of successfully completed actions
        failed_actions: Number of failed actions
        execution_logs: List of all execution log entries
        error_message: Error message if execution failed
        rollback_performed: Whether rollback was attempted after error
    """
    task_id: str
    total_actions: int
    successful_actions: int
    failed_actions: int
    execution_logs: List[ExecutionLogEntry]
    error_message: Optional[str] = None
    rollback_performed: bool = False


class UndoOperation(BaseModel):
    """
    Represents an operation that can be undone.
    
    Attributes:
        task_id: Task this operation belongs to
        action_type: Type of action performed
        original_path: Original path before operation
        new_path: New path after operation (if applicable)
        timestamp: When the operation was performed
        can_undo: Whether this operation can be undone
        undo_reason: Explanation if undo is not possible
    """
    task_id: str
    action_type: ActionType
    original_path: str
    new_path: Optional[str] = None
    timestamp: datetime
    can_undo: bool
    undo_reason: Optional[str] = None  # Why undo might not be possible
