"""
Executor Module

Safely executes validated file operations with logging and undo support.
This is the ONLY module that performs filesystem operations.
"""

import os
import shutil
from typing import Optional, List
from pathlib import Path
from sqlmodel import Session
from send2trash import send2trash

from sentinel_core.models.planner import PlanSchema, PlanAction
from sentinel_core.models.executor import ExecutionResult
from sentinel_core.models.logging import ExecutionLogEntry
from sentinel_core.models.enums import ActionType
from sentinel_core.executor.log_writer import LogWriter


def execute_plan(
    plan: PlanSchema,
    approved_actions: Optional[List[int]] = None,
    db_session: Optional[Session] = None
) -> ExecutionResult:
    """
    Execute a validated plan with logging and error handling.
    
    This is the primary entry point for executing file operations.
    All operations are logged, and execution aborts on first error with rollback.
    
    Args:
        plan: The PlanSchema containing actions to execute
        approved_actions: Optional list of action indices to execute.
                         If None, all actions are executed.
        db_session: Optional SQLModel Session for logging.
                   If None, operations are not logged to database.
    
    Returns:
        ExecutionResult with operation outcomes and logs
        
    Raises:
        Does not raise exceptions - all errors captured in ExecutionResult
        
    Example:
        >>> from sentinel_core.models import PlanSchema, PlanAction, ActionType
        >>> plan = PlanSchema(
        ...     task_id="test_123",
        ...     scope_path="/tmp",
        ...     actions=[
        ...         PlanAction(
        ...             type=ActionType.MOVE,
        ...             source_path="/tmp/file.txt",
        ...             destination_path="/tmp/dest/file.txt",
        ...             reason="Organize",
        ...             confidence=0.9
        ...         )
        ...     ],
        ...     summary="Test"
        ... )
        >>> result = execute_plan(plan)
        >>> print(f"Success: {result.successful_actions}/{result.total_actions}")
    """
    # Initialize tracking
    execution_logs: List[ExecutionLogEntry] = []
    successful_actions = 0
    failed_actions = 0
    rollback_performed = False
    error_message = None
    
    # Initialize logger if session provided
    logger = LogWriter(db_session) if db_session else None
    
    # Determine which actions to execute
    if approved_actions is not None:
        # Filter to only approved action indices
        actions_to_execute = [
            plan.actions[i] for i in approved_actions
            if 0 <= i < len(plan.actions)
        ]
    else:
        # Execute all actions
        actions_to_execute = plan.actions
    
    total_actions = len(plan.folders_to_create) + len(actions_to_execute)
    
    # Track completed operations for potential rollback
    completed_operations: List[PlanAction] = []
    
    try:
        # Step 1: Create folders first
        for folder in plan.folders_to_create:
            try:
                _create_folder(folder)
                successful_actions += 1
                
                if logger:
                    log_entry = logger.log_action(
                        task_id=plan.task_id,
                        action_type=ActionType.CREATE_FOLDER,
                        source_path=folder,
                        destination_path=folder,
                        status="success"
                    )
                    execution_logs.append(log_entry)
                    
            except Exception as e:
                failed_actions += 1
                error_message = f"Failed to create folder {folder}: {str(e)}"
                
                if logger:
                    log_entry = logger.log_action(
                        task_id=plan.task_id,
                        action_type=ActionType.CREATE_FOLDER,
                        source_path=folder,
                        destination_path=folder,
                        status="failed",
                        error_message=str(e)
                    )
                    execution_logs.append(log_entry)
                
                # Abort on first error
                raise
        
        # Step 2: Execute file actions
        for action in actions_to_execute:
            try:
                # Execute the appropriate operation
                if action.type == ActionType.MOVE:
                    _move_file(action.source_path, action.destination_path)
                elif action.type == ActionType.RENAME:
                    _rename_file(action.source_path, action.destination_path)
                elif action.type == ActionType.DELETE:
                    _delete_file(action.source_path)
                elif action.type == ActionType.SKIP:
                    # Skip is a no-op, just log it
                    pass
                elif action.type == ActionType.CREATE_FOLDER:
                    # Should have been handled in folder creation phase
                    _create_folder(action.destination_path)
                else:
                    raise ValueError(f"Unknown action type: {action.type}")
                
                successful_actions += 1
                completed_operations.append(action)
                
                if logger:
                    log_entry = logger.log_action(
                        task_id=plan.task_id,
                        action_type=action.type,
                        source_path=action.source_path,
                        destination_path=action.destination_path,
                        status="success"
                    )
                    execution_logs.append(log_entry)
                    
            except Exception as e:
                failed_actions += 1
                error_message = f"Failed {action.type.value} operation on {action.source_path}: {str(e)}"
                
                if logger:
                    log_entry = logger.log_action(
                        task_id=plan.task_id,
                        action_type=action.type,
                        source_path=action.source_path,
                        destination_path=action.destination_path,
                        status="failed",
                        error_message=str(e)
                    )
                    execution_logs.append(log_entry)
                
                # Attempt rollback
                try:
                    _rollback_operations(completed_operations, logger, plan.task_id, execution_logs)
                    rollback_performed = True
                except Exception as rollback_error:
                    error_message += f" | Rollback also failed: {str(rollback_error)}"
                
                # Abort execution
                raise
    
    except Exception:
        # Error already captured in error_message
        pass
    
    return ExecutionResult(
        task_id=plan.task_id,
        total_actions=total_actions,
        successful_actions=successful_actions,
        failed_actions=failed_actions,
        execution_logs=execution_logs,
        error_message=error_message,
        rollback_performed=rollback_performed
    )


def _create_folder(path: str) -> None:
    """
    Create a folder and all parent directories.
    
    Args:
        path: Path to folder to create
        
    Raises:
        OSError: If folder creation fails
    """
    os.makedirs(path, exist_ok=True)


def _move_file(source: str, destination: str) -> None:
    """
    Move a file from source to destination.
    
    Creates parent directories if needed.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Raises:
        FileNotFoundError: If source doesn't exist
        OSError: If move operation fails
    """
    # Ensure source exists
    if not os.path.exists(source):
        raise FileNotFoundError(f"Source file not found: {source}")
    
    # Create destination directory if needed
    dest_dir = os.path.dirname(destination)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)
    
    # Move the file
    shutil.move(source, destination)


def _rename_file(source: str, destination: str) -> None:
    """
    Rename a file.
    
    This is essentially the same as move within the same directory.
    
    Args:
        source: Original file path
        destination: New file path
        
    Raises:
        FileNotFoundError: If source doesn't exist
        OSError: If rename operation fails
    """
    # Rename is the same as move
    _move_file(source, destination)


def _delete_file(path: str) -> None:
    """
    Safely delete a file by sending to Trash/Recycle Bin.
    
    Uses send2trash for cross-platform safe deletion.
    Never permanently deletes files.
    
    Args:
        path: Path to file or folder to delete
        
    Raises:
        FileNotFoundError: If path doesn't exist
        OSError: If deletion fails
    """
    # Ensure path exists
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path not found: {path}")
    
    # Send to trash (cross-platform)
    send2trash(path)


def _rollback_operations(
    completed_operations: List[PlanAction],
    logger: Optional[LogWriter],
    task_id: str,
    execution_logs: List[ExecutionLogEntry]
) -> None:
    """
    Attempt to rollback completed operations in reverse order.
    
    Best-effort rollback - some operations may not be reversible.
    
    Args:
        completed_operations: List of successfully completed operations
        logger: Optional LogWriter for logging rollback attempts
        task_id: Task identifier for logging
        execution_logs: List to append rollback log entries
        
    Raises:
        Exception: If critical rollback operations fail
    """
    # Reverse the operations
    for action in reversed(completed_operations):
        try:
            if action.type == ActionType.MOVE:
                # Move back to original location
                if os.path.exists(action.destination_path):
                    shutil.move(action.destination_path, action.source_path)
                    
            elif action.type == ActionType.RENAME:
                # Rename back to original name
                if os.path.exists(action.destination_path):
                    shutil.move(action.destination_path, action.source_path)
                    
            elif action.type == ActionType.DELETE:
                # Cannot rollback delete - file is in trash
                # User must manually restore from trash
                pass
            
            if logger:
                log_entry = logger.log_action(
                    task_id=task_id,
                    action_type=action.type,
                    source_path=action.destination_path if action.destination_path else action.source_path,
                    destination_path=action.source_path,
                    status="rolled_back"
                )
                execution_logs.append(log_entry)
                
        except Exception as e:
            # Log rollback failure but continue trying to rollback others
            if logger:
                log_entry = logger.log_action(
                    task_id=task_id,
                    action_type=action.type,
                    source_path=action.destination_path if action.destination_path else action.source_path,
                    destination_path=action.source_path,
                    status="failed",
                    error_message=f"Rollback failed: {str(e)}"
                )
                execution_logs.append(log_entry)
