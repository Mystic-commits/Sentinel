"""
Request Schemas

Pydantic models for API request validation.
"""

from pathlib import Path
from typing import Annotated, ClassVar

from pydantic import AfterValidator, BaseModel, Field


def validate_folder_path(value: str) -> str:
    if "\x00" in value or not Path(value).is_absolute():
        raise ValueError("Enter an absolute folder path")
    return value


FolderPath = Annotated[str, Field(max_length=32767), AfterValidator(validate_folder_path)]


class ScanRequest(BaseModel):
    """Request to scan a directory."""

    path: FolderPath = Field(..., description="Absolute path to directory to scan")
    max_depth: int = Field(default=10, ge=1, le=20, description="Maximum directory depth")

    class Config:
        json_schema_extra: ClassVar = {
            "example": {"path": "/Users/test/Downloads", "max_depth": 10}
        }


class PlanRequest(BaseModel):
    """Request to create an organization plan."""

    path: FolderPath = Field(description="Absolute path to scan and plan")
    user_prompt: str | None = Field(
        None, max_length=1000, description="Custom instructions for local AI"
    )
    use_ai: bool = True

    class Config:
        json_schema_extra: ClassVar = {
            "example": {
                "path": "/Users/test/Downloads",
                "user_prompt": "Organize by file type and date",
            }
        }


class PreviewRequest(BaseModel):
    """Request to preview a plan."""

    task_id: str = Field(..., description="Task ID to preview")
    format: str = Field(default="terminal", description="Preview format: terminal, json, html")


class ExecuteRequest(BaseModel):
    """Request to execute a plan."""

    task_id: str = Field(..., description="Task ID to execute")
    approved_action_indices: list[int] = Field(min_length=1, max_length=10000)
    skip_safety: bool = Field(
        default=False, description="Skip safety validation (REJECTED - always validates)"
    )

    class Config:
        json_schema_extra: ClassVar = {"example": {"task_id": "abc-123-def-456"}}


class UndoRequest(BaseModel):
    """Request to undo a task."""

    task_id: str = Field(..., description="Task ID to undo")

    class Config:
        json_schema_extra: ClassVar = {"example": {"task_id": "abc-123-def-456"}}
