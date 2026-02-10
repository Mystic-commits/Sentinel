"""
Log Writer Module

Handles writing execution logs to the database.
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import Session, select
from sentinel_core.models.logging import ExecutionLogEntry
from sentinel_core.models.enums import ActionType


class LogWriter:
    """
    Writes execution logs to database.
    
    Provides a clean interface for logging file operations to the SQLite database.
    Handles transaction management and error resilience.
    
    Attributes:
        session: SQLModel database session
    """
    
    def __init__(self, session: Session):
        """
        Initialize LogWriter with a database session.
        
        Args:
            session: SQLModel Session for database operations
        """
        self.session = session
    
    def log_action(
        self,
        task_id: str,
        action_type: ActionType,
        source_path: str,
        destination_path: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> ExecutionLogEntry:
        """
        Log a single action to the database.
        
        Args:
            task_id: Unique identifier for the task
            action_type: Type of action performed
            source_path: Source path of the operation
            destination_path: Destination path (if applicable)
            status: Status of operation ("success", "failed", "rolled_back")
            error_message: Error message if operation failed
            
        Returns:
            The created ExecutionLogEntry
            
        Example:
            >>> logger = LogWriter(session)
            >>> entry = logger.log_action(
            ...     task_id="task_123",
            ...     action_type=ActionType.MOVE,
            ...     source_path="/tmp/file.txt",
            ...     destination_path="/tmp/dest/file.txt",
            ...     status="success"
            ... )
        """
        try:
            log_entry = ExecutionLogEntry(
                task_id=task_id,
                timestamp=datetime.now(),
                action_type=action_type,
                source_path=source_path,
                destination_path=destination_path,
                status=status,
                error_message=error_message
            )
            
            self.session.add(log_entry)
            self.session.commit()
            self.session.refresh(log_entry)
            
            return log_entry
            
        except Exception as e:
            # Logging failure shouldn't crash execution
            # Roll back this log entry but don't raise
            self.session.rollback()
            print(f"Warning: Failed to log action: {e}")
            
            # Return a non-persisted log entry for consistency
            return ExecutionLogEntry(
                task_id=task_id,
                timestamp=datetime.now(),
                action_type=action_type,
                source_path=source_path,
                destination_path=destination_path,
                status=status,
                error_message=error_message
            )
    
    def get_task_logs(self, task_id: str) -> List[ExecutionLogEntry]:
        """
        Retrieve all logs for a specific task.
        
        Args:
            task_id: Task identifier to query
            
        Returns:
            List of ExecutionLogEntry records for the task
            
        Example:
            >>> logger = LogWriter(session)
            >>> logs = logger.get_task_logs("task_123")
            >>> print(f"Found {len(logs)} log entries")
        """
        statement = select(ExecutionLogEntry).where(
            ExecutionLogEntry.task_id == task_id
        ).order_by(ExecutionLogEntry.timestamp)
        
        results = self.session.exec(statement)
        return list(results.all())
    
    def get_logs_by_status(self, task_id: str, status: str) -> List[ExecutionLogEntry]:
        """
        Retrieve logs for a task filtered by status.
        
        Args:
            task_id: Task identifier
            status: Status to filter by ("success", "failed", "rolled_back")
            
        Returns:
            List of matching ExecutionLogEntry records
        """
        statement = select(ExecutionLogEntry).where(
            ExecutionLogEntry.task_id == task_id,
            ExecutionLogEntry.status == status
        ).order_by(ExecutionLogEntry.timestamp)
        
        results = self.session.exec(statement)
        return list(results.all())
