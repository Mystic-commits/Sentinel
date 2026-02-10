"""
Clean My PC API Router

FastAPI endpoints for the Clean My PC pipeline.
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from sentinel_core.cleanpc.pipeline import CleanPCPipeline
from sentinel_core.planner.planner_agent import PlannerAgent
from sentinel_core.planner.ollama_client import OllamaClient
from sentinel_core.safety.safety import SafetyValidator
from sentinel_core.executor.executor import Executor
from sentinel_core.models.preferences import PreferencesSchema
from sentinel_core.models.planner import PlanSchema

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clean-pc", tags=["clean-pc"])


# Request/Response Models

class CleanPCRequest(BaseModel):
    """Request to scan and plan cleanup."""
    task_id: str = Field(..., description="Unique task identifier")
    target_dirs: Optional[List[str]] = Field(None, description="Directories to scan")
    max_depth: int = Field(3, description="Maximum directory depth")
    preferences: Optional[dict] = Field(None, description="User preferences")


class CleanPCResponse(BaseModel):
    """Response with scan results and plan."""
    task_id: str
    plan: dict
    summary: dict
    validation: dict


class ExecutePlanRequest(BaseModel):
    """Request to execute a plan."""
    task_id: str
    plan: dict
    dry_run: bool = True


# Initialize pipeline components
# Note: In production, these should be dependency-injected
ollama_client = OllamaClient()
planner = PlannerAgent(ollama_client)
safety = SafetyValidator()
executor = Executor()
pipeline = CleanPCPipeline(planner=planner, safety=safety, executor=executor)


@router.post("/scan", response_model=CleanPCResponse)
async def scan_and_plan(request: CleanPCRequest):
    """
    Scan directories and generate a cleanup plan.
    
    This endpoint:
    1. Scans the specified directories (or defaults)
    2. Classifies files
    3. Generates an organization plan
    4. Validates for safety
    5. Returns the plan for user approval
    
    The plan is NOT executed by this endpoint.
    """
    try:
        logger.info(f"Received Clean PC scan request for task {request.task_id}")
        
        # Convert preferences dict to schema if provided
        preferences = None
        if request.preferences:
            preferences = PreferencesSchema(**request.preferences)
        
        result = await pipeline.scan_and_plan(
            task_id=request.task_id,
            target_dirs=request.target_dirs,
            preferences=preferences,
            max_depth=request.max_depth
        )
        
        return CleanPCResponse(
            task_id=result["task_id"],
            plan=result["plan"].model_dump(),
            summary=result["summary"],
            validation=result["validation"]
        )
    
    except Exception as e:
        logger.error(f"Clean PC scan failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute")
async def execute_plan(request: ExecutePlanRequest):
    """
    Execute an approved cleanup plan.
    
    Args:
        request: Execution request with task_id, plan, and dry_run flag
        
    Returns:
        Execution results
    """
    try:
        logger.info(f"Executing plan for task {request.task_id} (dry_run={request.dry_run})")
        
        # Convert plan dict to schema
        plan = PlanSchema(**request.plan)
        
        result = await pipeline.execute_plan(
            task_id=request.task_id,
            plan=plan,
            dry_run=request.dry_run
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Plan execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "clean-pc"}
