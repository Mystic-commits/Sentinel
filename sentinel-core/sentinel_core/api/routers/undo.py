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
    raise HTTPException(
        status_code=501,
        detail="API undo is not integrated. Restore trashed files using your system Trash.",
    )
