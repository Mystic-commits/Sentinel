"""
Undo Router

Endpoint for undoing executed tasks.
"""

from fastapi import APIRouter, HTTPException
from ..models.requests import UndoRequest
from ..models.responses import UndoResponse
from ..websocket.manager import ws_manager
from sentinel_core.models.enums import TaskState
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/undo", response_model=UndoResponse)
async def undo(request: UndoRequest):
    """
    Undo a previously executed task.
    
    Reverses file operations from a completed task.
    Note: Some operations (like permanent deletes) cannot be undone.
    
    Args:
        request: Undo request with task_id
        
    Returns:
        UndoResponse with undo status
        
    Raises:
        HTTPException 404: If task not found
        HTTPException 400: If task cannot be undone
        
    Example:
        POST /api/undo
        {
            "task_id": "task-abc-123"
        }
    """
    # TODO: Integrate with UndoManager
    # from sentinel_core.executor import UndoManager
    # from sentinel_core.memory.db import get_engine, get_session
    
    # engine = get_engine()
    # with get_session(engine) as session:
    #     undo_mgr = UndoManager(session)
    #     can_undo, reason = undo_mgr.can_undo_task(request.task_id)
    #
    #     if not can_undo:
    #         raise HTTPException(status_code=400, detail=reason)
    #
    #     result = undo_mgr.undo_task(request.task_id)
    
    logger.info(f"Undo requested (pending integration): {request.task_id}")
    
    await ws_manager.broadcast({
        "event_type": "EXECUTING",
        "task_id": request.task_id,
        "message": "Undo in progress",
        "data": {}
    })
    
    return UndoResponse(
        task_id=request.task_id,
        state=TaskState.COMPLETED,
        undone_operations=0,
        failed_operations=0,
        message="Undo pending (undo manager integration needed)"
    )
