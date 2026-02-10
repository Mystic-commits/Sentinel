"""
WebSocket Event Examples

This file demonstrates how to emit WebSocket events from the backend.
"""

import asyncio
from sentinel_core.api.websocket.manager import ws_manager
from sentinel_core.api.models.events import EventType

# Example usage in a task handler

async def example_task_flow(task_id: str, path: str):
    """
    Example of emitting WebSocket events during a task lifecycle.
    
    This demonstrates the complete event flow from task start to completion.
    """
    
    # 1. Task Started
    await ws_manager.broadcast_task_event(
        EventType.TASK_STARTED,
        task_id,
        f"Starting cleanup of {path}",
        {
            "description": f"Clean {path}",
            "mode": "file_organization",
            "path": path
        }
    )
    
    # 2. Scanning Progress (multiple updates)
    total_files = 100
    for i in range(0, total_files, 10):
        await ws_manager.broadcast_task_event(
            EventType.SCAN_PROGRESS,
            task_id,
            f"Scanning... ({i}/{total_files} files)",
            {
                "current_file": f"/path/to/file_{i}.txt",
                "files_scanned": i,
                "total_size": i * 1024,
                "progress": int((i / total_files) * 100)
            }
        )
        await asyncio.sleep(0.1)  # Simulate work
    
    # 3. Plan Ready
    plan = {
        "id": "plan-xyz-789",
        "operations": [
            {
                "id": "op-1",
                "type": "move",
                "source": "/Downloads/photo.jpg",
                "destination": "/Pictures/2024/photo.jpg",
                "reason": "Photo from 2024 based on EXIF data",
                "status": "pending",
                "size": 2048000
            },
            {
                "id": "op-2",
                "type": "delete",
                "source": "/Downloads/temp.txt",
                "reason": "Temporary file older than 30 days",
                "status": "pending",
                "size": 1024
            }
        ],
        "total_files": 127,
        "estimated_time": "2 minutes"
    }
    
    await ws_manager.broadcast_task_event(
        EventType.PLAN_READY,
        task_id,
        f"Plan ready with {len(plan['operations'])} operations",
        {"plan": plan}
   )
    
    # 4. Waiting for Approval
    await ws_manager.broadcast_task_event(
        EventType.WAITING_FOR_APPROVAL,
        task_id,
        "Review the plan and approve to continue",
        {
            "operations_count": len(plan['operations']),
            "requires_confirmation": True
        }
    )
    
    # Simulate waiting for approval
    await asyncio.sleep(2)
    
    # 5. Execution Progress (multiple updates)
    total_operations = len(plan['operations'])
    for i, op in enumerate(plan['operations']):
        progress = int(((i + 1) / total_operations) * 100)
        
        await ws_manager.broadcast_task_event(
            EventType.EXECUTION_PROGRESS,
            task_id,
            f"Processing: {op['source']}",
            {
                "progress": progress,
                "current_operation": op['id'],
                "files_processed": i + 1,
                "total_files": total_operations,
                "current_file": op['source']
            }
        )
        
        await asyncio.sleep(0.5)  # Simulate work
    
    # 6. Task Completed
    await ws_manager.broadcast_task_event(
        EventType.TASK_COMPLETED,
        task_id,
        "Task completed successfully",
        {
            "result": {
                "success": True,
                "files_processed": total_operations,
                "errors": [],
                "duration": "2 minutes 15 seconds",
                "completed_at": "2026-02-09T11:35:00Z"
            }
        }
    )


async def example_task_failure(task_id: str):
    """Example of handling task failure."""
    
    await ws_manager.broadcast_task_event(
        EventType.TASK_STARTED,
        task_id,
        "Starting task...",
        {}
    )
    
    # Simulate some work
    await asyncio.sleep(1)
    
    # Task fails
    await ws_manager.broadcast_task_event(
        EventType.TASK_FAILED,
        task_id,
        "Task failed: Permission denied",
        {
            "error": "Permission denied: /System/Protected/file.txt",
            "error_code": "PERMISSION_DENIED",
            "files_processed": 23,
            "failed_at": "2026-02-09T11:32:30Z"
        }
    )


# Example: How to use in a FastAPI endpoint

"""
from fastapi import APIRouter
from sentinel_core.api.websocket.manager import ws_manager
from sentinel_core.api.models.events import EventType

router = APIRouter()

@router.post("/tasks/scan")
async def scan_directory(path: str):
    task_id = str(uuid.uuid4())
    
    # Start task in background
    asyncio.create_task(perform_scan(task_id, path))
    
    return {"task_id": task_id}

async def perform_scan(task_id: str, path: str):
    # Emit TASK_STARTED event
    await ws_manager.broadcast_task_event(
        EventType.TASK_STARTED,
        task_id,
        f"Scanning {path}",
        {"path": path}
    )
    
    # ... do actual scanning ...
    
    # Emit SCAN_PROGRESS events
    for file in files:
        await ws_manager.broadcast_task_event(
            EventType.SCAN_PROGRESS,
            task_id,
            f"Scanning: {file.name}",
            {"current_file": str(file)}
        )
    
    # ... generate plan ...
    
    # Emit PLAN_READY event
    await ws_manager.broadcast_task_event(
        EventType.PLAN_READY,
        task_id,
        "Plan ready for review",
        {"plan": plan}
    )
"""
