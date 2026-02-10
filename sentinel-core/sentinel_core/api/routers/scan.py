"""
Scan Router

Endpoint for scanning directories.
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from ..models.requests import ScanRequest
from ..models.responses import ScanResponse
from ..websocket.manager import ws_manager
from sentinel_core.scanner import scan_directory
from sentinel_core.models.enums import TaskState
import uuid
from datetime import datetime
import logging

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
    with open("/Users/Mystic/Desktop/trial and error/Sentinel/backend_debug.log", "a") as f:
        f.write(f"DEBUG: perform_scan started for {scan_id} at {path}\n")
    
    import asyncio
    from ..models.events import WebSocketEvent, EventType
    
    try:
        # Broadcast scanning started
        with open("/Users/Mystic/Desktop/trial and error/Sentinel/backend_debug.log", "a") as f:
            f.write(f"DEBUG: Broadcasting SCANNING event for {scan_id}\n")
            
        await ws_manager.broadcast(WebSocketEvent(
            event_type=EventType.SCANNING,
            task_id=scan_id,
            message=f"Scanning {path}",
            data={"path": path, "max_depth": max_depth}
        ))
        
        # Perform scan in thread pool to prevent blocking
        with open("/Users/Mystic/Desktop/trial and error/Sentinel/backend_debug.log", "a") as f:
            f.write(f"DEBUG: Starting scan_directory in thread for {scan_id}\n")
            
        result = await asyncio.to_thread(scan_directory, path)
        
        with open("/Users/Mystic/Desktop/trial and error/Sentinel/backend_debug.log", "a") as f:
            f.write(f"DEBUG: scan_directory completed for {scan_id}. Found {len(result.files)} files.\n")
        
        total_files = len(result.files)
        total_size = sum(f.size_bytes for f in result.files)
        
        # Broadcast complete
        with open("/Users/Mystic/Desktop/trial and error/Sentinel/backend_debug.log", "a") as f:
            f.write(f"DEBUG: Broadcasting SCAN_COMPLETE event for {scan_id}\n")
            
        await ws_manager.broadcast(WebSocketEvent(
            event_type=EventType.SCAN_COMPLETE,
            task_id=scan_id,
            message=f"Scan complete: {total_files} files found",
            data={
                "total_files": total_files,
                "total_size_bytes": total_size,
                "errors": len(result.errors) if result.errors else 0
            }
        ))
        
        logger.info(f"Scan complete: {scan_id} - {total_files} files")
        
    except Exception as e:
        with open("/Users/Mystic/Desktop/trial and error/Sentinel/backend_debug.log", "a") as f:
            f.write(f"DEBUG: ERROR in perform_scan: {e}\n")
            import traceback
            traceback.print_exc(file=f)
            
        logger.error(f"Scan failed: {scan_id} - {e}")
        await ws_manager.broadcast(WebSocketEvent(
            event_type=EventType.ERROR,
            task_id=scan_id,
            message=f"Scan failed: {str(e)}",
            data={"error_type": type(e).__name__}
        ))


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
    
    # Validate path exists
    from pathlib import Path
    if not Path(request.path).exists():
        raise HTTPException(status_code=404, detail=f"Path not found: {request.path}")
    
    # Start scan in background
    background_tasks.add_task(perform_scan, scan_id, request.path, request.max_depth)
    
    logger.info(f"Scan initiated: {scan_id}")
    
    return ScanResponse(
        scan_id=scan_id,
        root_path=request.path,
        total_files=0,
        total_size_bytes=0,
        state=TaskState.SCANNING
    )
