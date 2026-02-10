"""
Request Schemas

Pydantic models for API request validation.
"""

from pydantic import BaseModel, Field
from typing import Optional


class ScanRequest(BaseModel):
    """Request to scan a directory."""
    
    path: str = Field(..., description="Absolute path to directory to scan")
    max_depth: int = Field(default=10, ge=1, le=20, description="Maximum directory depth")
    
    class Config:
        json_schema_extra = {
            "example": {
                "path": "/Users/test/Downloads",
                "max_depth": 10
            }
        }


class PlanRequest(BaseModel):
    """Request to create an organization plan."""
    
    scan_id: Optional[str] = Field(None, description="ID from previous scan")
    path: Optional[str] = Field(None, description="Path to scan and plan")
    user_prompt: Optional[str] = Field(None, description="Custom instructions for AI")
    
    class Config:
        json_schema_extra = {
            "example": {
                "path": "/Users/test/Downloads",
                "user_prompt": "Organize by file type and date"
            }
        }


class PreviewRequest(BaseModel):
    """Request to preview a plan."""
    
    task_id: str = Field(..., description="Task ID to preview")
    format: str = Field(default="terminal", description="Preview format: terminal, json, html")


class ExecuteRequest(BaseModel):
    """Request to execute a plan."""
    
    task_id: str = Field(..., description="Task ID to execute")
    skip_safety: bool = Field(
        default=False,
        description="Skip safety validation (REJECTED - always validates)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc-123-def-456"
            }
        }


class UndoRequest(BaseModel):
    """Request to undo a task."""
    
    task_id: str = Field(..., description="Task ID to undo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc-123-def-456"
            }
        }
