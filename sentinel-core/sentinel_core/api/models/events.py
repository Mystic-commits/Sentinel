"""
WebSocket Event Schemas

Pydantic models for WebSocket events with comprehensive task lifecycle support.
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class EventType(str, Enum):
    """WebSocket event types for task lifecycle."""
    
    # Connection events
    CONNECTION_ACK = "CONNECTION_ACK"
    HEARTBEAT = "HEARTBEAT"
    
    # Task lifecycle events
    TASK_STARTED = "TASK_STARTED"
    SCAN_PROGRESS = "SCAN_PROGRESS"
    PLAN_READY = "PLAN_READY"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    EXECUTION_PROGRESS = "EXECUTION_PROGRESS"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    
    # Legacy events (kept for compatibility)
    SCANNING = "SCANNING"
    SCAN_COMPLETE = "SCAN_COMPLETE"
    PLANNING = "PLANNING"
    SAFETY_CHECK = "SAFETY_CHECK"
    SAFETY_FAILED = "SAFETY_FAILED"
    EXECUTING = "EXECUTING"
    PROGRESS = "PROGRESS"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    ERROR = "ERROR"


class WebSocketEvent(BaseModel):
    """
    Base WebSocket event model.
    
    All WebSocket events follow this structure for consistency.
    """
    
    event_type: EventType = Field(..., description="Type of event")
    task_id: Optional[str] = Field(None, description="Task ID this event relates to")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp (UTC)")
    message: Optional[str] = Field(None, description="Human-readable message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional event data")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            EventType: lambda v: v.value
        }
        json_schema_extra = {
            "example": {
                "event_type": "TASK_STARTED",
                "task_id": "task-abc-123",
                "timestamp": "2026-02-09T11:30:00Z",
                "message": "Task started: Clean Downloads folder",
                "data": {
                    "description": "Clean Downloads folder",
                    "mode": "file_organization",
                    "path": "/Users/user/Downloads"
                }
            }
        }


class ConnectionEvent(WebSocketEvent):
    """Connection acknowledgment event."""
    
    event_type: EventType = EventType.CONNECTION_ACK


class HeartbeatEvent(WebSocketEvent):
    """Heartbeat keep-alive event."""
    
    event_type: EventType = EventType.HEARTBEAT


class TaskStartedEvent(WebSocketEvent):
    """Task started event."""
    
    event_type: EventType = EventType.TASK_STARTED


class ScanProgressEvent(WebSocketEvent):
    """Scan progress update event."""
    
    event_type: EventType = EventType.SCAN_PROGRESS


class PlanReadyEvent(WebSocketEvent):
    """Plan ready for review event."""
    
    event_type: EventType = EventType.PLAN_READY


class WaitingForApprovalEvent(WebSocketEvent):
    """Waiting for user approval event."""
    
    event_type: EventType = EventType.WAITING_FOR_APPROVAL


class ExecutionProgressEvent(WebSocketEvent):
    """Execution progress update event."""
    
    event_type: EventType = EventType.EXECUTION_PROGRESS


class TaskCompletedEvent(WebSocketEvent):
    """Task completed successfully event."""
    
    event_type: EventType = EventType.TASK_COMPLETED


class TaskFailedEvent(WebSocketEvent):
    """Task failed event."""
    
    event_type: EventType = EventType.TASK_FAILED


# Legacy compatibility (deprecated but maintained)
class TaskEvent(WebSocketEvent):
    """Legacy task event - use WebSocketEvent instead."""
    pass

