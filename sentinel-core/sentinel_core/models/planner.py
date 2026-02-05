from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from sentinel_core.models.enums import ActionType

class PlanAction(BaseModel):
    """A proposed atomic action."""
    type: ActionType
    source_path: Optional[str] = None
    destination_path: Optional[str] = None
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)
    
    @field_validator("destination_path")
    @classmethod
    def validate_destination(cls, v: Optional[str], info: Any) -> Optional[str]:
        # Validate that move/rename/create_folder require destination
        values = info.data
        action_type = values.get("type")
        if action_type in (ActionType.MOVE, ActionType.RENAME, ActionType.CREATE_FOLDER) and not v:
            raise ValueError(f"Destination path is required for {action_type}")
        return v

class AmbiguousFile(BaseModel):
    """A file that the Planner is unsure about."""
    path: str
    suggested_action: Optional[ActionType] = None
    reason: str

class PlanSchema(BaseModel):
    """The strict schema for LLM output."""
    task_id: str
    scope_path: str
    folders_to_create: List[str] = []
    actions: List[PlanAction]
    ambiguous_files: List[AmbiguousFile] = []
    summary: str
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "task_id": "task_123",
                    "scope_path": "/Users/user/Downloads",
                    "folders_to_create": ["/Users/user/Downloads/PDFs"],
                    "actions": [
                        {
                             "type": "move",
                             "source_path": "/Users/user/Downloads/doc.pdf",
                             "destination_path": "/Users/user/Downloads/PDFs/doc.pdf",
                             "reason": "It is a PDF",
                             "confidence": 0.9
                        }
                    ],
                    "ambiguous_files": [],
                    "summary": "Moving 1 file."
                }
            ]
        }
    }
