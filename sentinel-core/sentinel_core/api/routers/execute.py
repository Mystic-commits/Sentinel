"""
Execute Router

Endpoint for executing organization plans.

CRITICAL: This router enforces safety validation - execution cannot proceed without it.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..models.requests import ExecuteRequest
from ..models.responses import ExecuteResponse
from ..websocket.manager import ws_manager
from sentinel_core.models.enums import TaskState
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest, background_tasks: BackgroundTasks):
    """
    Execute an organization plan.
    
    SAFETY GUARANTEE: This endpoint ALWAYS validates plans through SafetyValidator.
    The skip_safety parameter is rejected - it exists only to document that
    safety cannot be bypassed.
    
    Args:
        request: Execute request with task_id
        background_tasks: FastAPI background tasks
        
    Returns:
        ExecuteResponse with execution status
        
    Raises:
        HTTPException 403: If skip_safety is True
        HTTPException 400: If plan fails safety validation
        HTTPException 404: If task not found
        
    Example:
        POST /api/execute
        {
            "task_id": "task-abc-123"
        }
    """
    # CRITICAL SAFETY CHECK: NEVER allow skipping validation
    if request.skip_safety:
        logger.warning(f"Execution rejected: attempt to skip safety for {request.task_id}")
        raise HTTPException(
            status_code=403,
            detail="Safety validation cannot be skipped. This is a non-negotiable system invariant."
        )
    
    # Load plan from memory store
    from ..memory import get_task, save_task
    task_data = get_task(request.task_id)
    
    if not task_data or "plan" not in task_data:
        raise HTTPException(status_code=404, detail=f"Task not found or no plan available: {request.task_id}")
    
    plan = task_data["plan"]
    
    # CRITICAL: Safety validation
    from sentinel_core.safety import SafetyValidator
    validator = SafetyValidator()
    validation_result = validator.validate_plan(plan)
    
    import asyncio
    from ..models.events import WebSocketEvent, EventType
    
    if not validation_result.is_safe:
        logger.error(f"Safety validation failed for {request.task_id}: {validation_result.errors}")
        await ws_manager.broadcast(WebSocketEvent(
            event_type=EventType.TASK_FAILED,
            task_id=request.task_id,
            message="Plan failed safety validation",
            data={"errors": validation_result.errors}
        ))
        raise HTTPException(
            status_code=400,
            detail=f"Plan failed safety validation: {validation_result.errors}"
        )
    
    # Broadcast safety passed
    await ws_manager.broadcast(WebSocketEvent(
        event_type=EventType.WAITING_FOR_APPROVAL, # Or generic info
        task_id=request.task_id,
        message="Safety validation passed. Starting execution...",
        data={}
    ))
    
    async def perform_execution(task_id: str, plan):
        try:
            from sentinel_core.executor.executor import execute_plan as do_execute
            
            logger.warning(f"[EXEC] Starting execution for {task_id}")
            logger.warning(f"[EXEC] Plan type: {type(plan).__name__}")
            logger.warning(f"[EXEC] Plan has {len(plan.actions)} actions, {len(plan.folders_to_create)} folders")
            
            if plan.actions:
                first = plan.actions[0]
                logger.warning(f"[EXEC] First action: type={first.type}, source={first.source_path}, dest={first.destination_path}")
            
            # Broadcast start
            await ws_manager.broadcast(WebSocketEvent(
                event_type=EventType.EXECUTION_PROGRESS,
                task_id=task_id,
                message="Starting execution...",
                data={"progress": 0}
            ))
            
            # Call the REAL executor directly — no pipeline, no class wrapper
            result = do_execute(plan=plan)
            
            logger.warning(f"[EXEC] Result: succeeded={result.successful_actions}, failed={result.failed_actions}, error={result.error_message}")
            
            # Broadcast complete
            await ws_manager.broadcast(WebSocketEvent(
                event_type=EventType.TASK_COMPLETED,
                task_id=task_id,
                message=f"Execution completed: {result.successful_actions} succeeded, {result.failed_actions} failed",
                data={"result": {"success": result.successful_actions, "failed": result.failed_actions, "error": result.error_message}, "progress": 100}
            ))
            
            # Update store
            save_task(task_id, {"state": TaskState.COMPLETED, "result": {"success": result.successful_actions, "failed": result.failed_actions}})
            
        except Exception as e:
            import traceback
            logger.error(f"[EXEC] Execution FAILED: {e}")
            logger.error(f"[EXEC] Traceback: {traceback.format_exc()}")
            await ws_manager.broadcast(WebSocketEvent(
                event_type=EventType.TASK_FAILED,
                task_id=task_id,
                message=f"Execution failed: {str(e)}",
                data={"error": str(e)}
            ))
            save_task(task_id, {"state": TaskState.FAILED, "error": str(e)})

    # Start execution in background
    background_tasks.add_task(perform_execution, request.task_id, plan)
    
    logger.info(f"Execution initiated: {request.task_id}")
    
    return ExecuteResponse(
        task_id=request.task_id,
        state=TaskState.EXECUTING,
        successful_actions=0,
        failed_actions=0,
        message="Execution initiated"
    )
