"""
Preview Router

Endpoint for previewing organization plans.
"""

import logging

from fastapi import APIRouter, HTTPException

from ..models.requests import PreviewRequest
from ..models.responses import PreviewResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/preview", response_model=PreviewResponse)
async def preview(request: PreviewRequest):
    """
    Preview an organization plan before execution.

    Shows what changes will be made without executing them.

    Args:
        request: Preview request with task_id

    Returns:
        PreviewResponse with formatted preview

    Example:
        POST /api/preview
        {
            "task_id": "task-abc-123",
            "format": "terminal"
        }
    """
    import json

    from sentinel_core.preview import generate_terminal_preview, generate_web_preview

    from ..memory import get_task

    task = get_task(request.task_id)
    if not task or "plan" not in task:
        raise HTTPException(status_code=404, detail="Plan not found")
    if request.format == "terminal":
        preview_text = generate_terminal_preview(task["plan"])
    elif request.format == "json":
        preview_text = json.dumps(generate_web_preview(task["plan"]))
    else:
        raise HTTPException(status_code=422, detail="Use terminal or json preview")

    return PreviewResponse(
        task_id=request.task_id, preview_text=preview_text, format=request.format
    )
