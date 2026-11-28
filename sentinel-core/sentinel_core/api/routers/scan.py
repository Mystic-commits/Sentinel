"""
Scan Router

Endpoint for scanning directories.
"""

import logging
import uuid

from fastapi import APIRouter, BackgroundTasks

from sentinel_core.models.enums import TaskState

from ..file_jobs import run_file_job, scan_folder
from ..limits import schedule_scan_job
from ..memory import save_task
from ..models.requests import ScanRequest
from ..models.responses import ScanResponse
from ..websocket.manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter()


async def perform_scan(scan_id: str, path: str, max_depth: int):
    """
    Background task to perform directory scan.

    Args:
        scan_id: Unique scan identifier
        path: Directory path to scan
        max_depth: Maximum directory depth
    """

    from ..models.events import EventType, WebSocketEvent

    try:
        # Broadcast scanning started

        await ws_manager.broadcast(
            WebSocketEvent(
                event_type=EventType.SCANNING,
                task_id=scan_id,
                message=f"Scanning {path}",
                data={"path": path, "max_depth": max_depth},
            )
        )

        result = await run_file_job(scan_folder, path, max_depth)
        total_files = result["total_files"]
        status = "Partial scan" if result["truncated"] else "Scan complete"
        message = f"{status}: {total_files} files found"
        save_task(scan_id, {"state": TaskState.COMPLETED, "summary": message})
        await ws_manager.broadcast(
            WebSocketEvent(
                event_type=EventType.SCAN_COMPLETE,
                task_id=scan_id,
                message=message,
                data=result,
            )
        )

        logger.info(f"Scan complete: {scan_id} - {total_files} files")

    except Exception as e:
        save_task(scan_id, {"state": TaskState.FAILED, "summary": str(e)})
        logger.error(f"Scan failed: {scan_id} - {e}")
        await ws_manager.broadcast(
            WebSocketEvent(
                event_type=EventType.ERROR,
                task_id=scan_id,
                message=f"Scan failed: {e!s}",
                data={"error_type": type(e).__name__},
            )
        )


@router.post("/scan", response_model=ScanResponse)
async def scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """
    Scan a directory and return file statistics.

    Starts a background scan job and immediately returns. Listen to WebSocket
    for SCAN_COMPLETE event.

    Args:
        request: Scan request with path and max_depth
        background_tasks: FastAPI background tasks

    Returns:
        ScanResponse with scan_id and initial state

    Example:
        POST /api/scan
        {
            "path": "/Users/test/Downloads",
            "max_depth": 10
        }
    """
    scan_id = f"scan-{uuid.uuid4()}"

    schedule_scan_job(background_tasks, perform_scan, scan_id, request.path, request.max_depth)
    save_task(scan_id, {"state": TaskState.SCANNING})

    logger.info(f"Scan initiated: {scan_id}")

    return ScanResponse(
        scan_id=scan_id,
        root_path=request.path,
        total_files=0,
        total_size_bytes=0,
        state=TaskState.SCANNING,
    )
