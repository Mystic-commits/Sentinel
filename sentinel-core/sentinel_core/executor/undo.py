"""
Undo Module

Handles reversing executed file operations.
"""

import os
import shutil
from typing import List, Optional, Tuple
from datetime import datetime
from sqlmodel import Session, select

from sentinel_core.models.logging import ExecutionLogEntry, TaskRecord
from sentinel_core.models.executor import ExecutionResult, UndoOperation
from sentinel_core.models.enums import ActionType
from sentinel_core.executor.log_writer import LogWriter


class UndoManager:
    """
    Manages undo operations for executed tasks.
    
    Provides functionality to reverse file operations based on execution logs.
    Handles validation and safety checks before performing undo.
    
    Attributes:
        session: SQLModel database session
        logger: LogWriter for logging undo operations
    """
    
    def __init__(self, session: Session):
        """
        Initialize UndoManager with a database session.
        
        Args:
            session: SQLModel Session for database operations
        """
        self.session = session
        self.logger = LogWriter(session)
    
    def undo_task(self, task_id: str) -> ExecutionResult:
        """
        Undo all operations from a task in reverse order.
        
        Only moves and renames can be undone. Deletes cannot be automatically
        reversed as files are in the Trash.
        
        Args:
            task_id: Task identifier to undo
            
        Returns:
            ExecutionResult with undo operation outcomes
            
        Raises:
            ValueError: If task cannot be undone
            
        Example:
            >>> undo_mgr = UndoManager(session)
            >>> result = undo_mgr.undo_task("task_123")
            >>> print(f"Undid {result.successful_actions} operations")
        """
        # Check if task can be undone
        can_undo, reason = self.can_undo_task(task_id)
        if not can_undo:
            raise ValueError(f"Cannot undo task {task_id}: {reason}")
        
        # Get execution logs in reverse order
        statement = select(ExecutionLogEntry).where(
            ExecutionLogEntry.task_id == task_id,
            ExecutionLogEntry.status == "success"
        ).order_by(ExecutionLogEntry.timestamp.desc())
        
        results = self.session.exec(statement)
        logs = list(results.all())
        
        execution_logs: List[ExecutionLogEntry] = []
        successful_actions = 0
        failed_actions = 0
        error_message = None
        
        # Undo operations in reverse order
        for log in logs:
            try:
                if log.action_type == ActionType.MOVE:
                    # Move back to original location
                    if os.path.exists(log.destination_path):
                        # Check if original path is free
                        if os.path.exists(log.source_path):
                            raise FileExistsError(
                                f"Cannot undo: original path already exists: {log.source_path}"
                            )
                        shutil.move(log.destination_path, log.source_path)
                        successful_actions += 1
                    else:
                        raise FileNotFoundError(
                            f"Cannot undo: file not found at: {log.destination_path}"
                        )
                
                elif log.action_type == ActionType.RENAME:
                    # Rename back to original name
                    if os.path.exists(log.destination_path):
                        if os.path.exists(log.source_path):
                            raise FileExistsError(
                                f"Cannot undo: original path already exists: {log.source_path}"
                            )
                        shutil.move(log.destination_path, log.source_path)
                        successful_actions += 1
                    else:
                        raise FileNotFoundError(
                            f"Cannot undo: file not found at: {log.destination_path}"
                        )
                
                elif log.action_type == ActionType.DELETE:
                    # Cannot automatically undo deletes
                    # File is in Trash - user must manually restore
                    failed_actions += 1
                    error_message = "Delete operations cannot be automatically undone. Files are in Trash."
                
                elif log.action_type == ActionType.CREATE_FOLDER:
                    # Optionally remove folder if empty
                    if os.path.exists(log.source_path):
                        try:
                            os.rmdir(log.source_path)  # Only removes if empty
                            successful_actions += 1
                        except OSError:
                            # Folder not empty, skip removal
                            pass
                
                # Log the undo operation
                undo_log = self.logger.log_action(
                    task_id=f"undo_{task_id}",
                    action_type=log.action_type,
                    source_path=log.destination_path if log.destination_path else log.source_path,
                    destination_path=log.source_path,
                    status="success" if successful_actions > len(execution_logs) else "failed",
                    error_message=error_message
                )
                execution_logs.append(undo_log)
                
            except Exception as e:
                failed_actions += 1
                error_message = f"Failed to undo {log.action_type.value}: {str(e)}"
                
                # Log failure
                undo_log = self.logger.log_action(
                    task_id=f"undo_{task_id}",
                    action_type=log.action_type,
                    source_path=log.destination_path if log.destination_path else log.source_path,
                    destination_path=log.source_path,
                    status="failed",
                    error_message=str(e)
                )
                execution_logs.append(undo_log)
        
        # Mark task as no longer undoable
        task_record = self.session.get(TaskRecord, task_id)
        if task_record:
            task_record.undo_available = False
            self.session.add(task_record)
            self.session.commit()
        
        return ExecutionResult(
            task_id=f"undo_{task_id}",
            total_actions=len(logs),
            successful_actions=successful_actions,
            failed_actions=failed_actions,
            execution_logs=execution_logs,
            error_message=error_message,
            rollback_performed=False
        )
    
    def can_undo_task(self, task_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a task can be undone.
        
        Args:
            task_id: Task identifier to check
            
        Returns:
            Tuple of (can_undo: bool, reason: Optional[str])
            If can_undo is False, reason explains why
            
        Example:
            >>> undo_mgr = UndoManager(session)
            >>> can_undo, reason = undo_mgr.can_undo_task("task_123")
            >>> if not can_undo:
            ...     print(f"Cannot undo: {reason}")
        """
        # Check if task exists
        task_record = self.session.get(TaskRecord, task_id)
        if not task_record:
            return False, f"Task {task_id} not found"
        
        # Check if already undone
        if not task_record.undo_available:
            return False, "Task has already been undone"
        
        # Check if there are any successful operations
        statement = select(ExecutionLogEntry).where(
            ExecutionLogEntry.task_id == task_id,
            ExecutionLogEntry.status == "success"
        )
        results = self.session.exec(statement)
        logs = list(results.all())
        
        if not logs:
            return False, "No successful operations to undo"
        
        return True, None
    
    def get_undo_operations(self, task_id: str) -> List[UndoOperation]:
        """
        Get list of operations that would be undone.
        
        Provides a preview of what undo would do before executing.
        
        Args:
            task_id: Task identifier
            
        Returns:
            List of UndoOperation objects describing what would be undone
            
        Example:
            >>> undo_mgr = UndoManager(session)
            >>> operations = undo_mgr.get_undo_operations("task_123")
            >>> for op in operations:
            ...     if op.can_undo:
            ...         print(f"Can undo: {op.action_type} on {op.original_path}")
            ...     else:
            ...         print(f"Cannot undo: {op.undo_reason}")
        """
        # Get execution logs
        statement = select(ExecutionLogEntry).where(
            ExecutionLogEntry.task_id == task_id,
            ExecutionLogEntry.status == "success"
        ).order_by(ExecutionLogEntry.timestamp.desc())
        
        results = self.session.exec(statement)
        logs = list(results.all())
        
        undo_operations: List[UndoOperation] = []
        
        for log in logs:
            # Determine if operation can be undone
            can_undo = True
            undo_reason = None
            
            if log.action_type == ActionType.DELETE:
                can_undo = False
                undo_reason = "Delete operations cannot be automatically undone. File is in Trash."
            
            elif log.action_type in (ActionType.MOVE, ActionType.RENAME):
                # Check if file still exists at destination
                if not os.path.exists(log.destination_path):
                    can_undo = False
                    undo_reason = f"File no longer exists at destination: {log.destination_path}"
                
                # Check if original path is now occupied
                elif os.path.exists(log.source_path):
                    can_undo = False
                    undo_reason = f"Original path is now occupied: {log.source_path}"
            
            undo_op = UndoOperation(
                task_id=task_id,
                action_type=log.action_type,
                original_path=log.source_path,
                new_path=log.destination_path,
                timestamp=log.timestamp,
                can_undo=can_undo,
                undo_reason=undo_reason
            )
            undo_operations.append(undo_op)
        
        return undo_operations
