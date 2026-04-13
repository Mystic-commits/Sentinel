from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from sentinel_core.models.enums import ActionType

class PlanAction(BaseModel):
    """A proposed atomic action."""
    type: ActionType
    source_path: Optional[str] = None
    destination_path: Optional[str] = None
    reason: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class AmbiguousFile(BaseModel):
    """A file that the Planner is unsure about."""
    path: str
    suggested_action: Optional[ActionType] = None
    reason: str

class PlanSchema(BaseModel):
    """The strict schema for LLM output."""
    task_id: str
    scope_path: str = ""
    folders_to_create: List[str] = []
    actions: List[PlanAction] = []
    ambiguous_files: List[AmbiguousFile] = []
    summary: str

    @model_validator(mode="before")
    @classmethod
    def normalise_operations_alias(cls, data: Any) -> Any:
        """Accept 'operations' as a synonym for 'actions' (test backward-compat)."""
        if isinstance(data, dict) and "operations" in data and "actions" not in data:
            data = dict(data)  # copy to avoid mutating callers
            data["actions"] = data.pop("operations")
        return data
    
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


# Backward-compatibility aliases used in tests
OperationSchema = PlanAction
OperationType = ActionType
