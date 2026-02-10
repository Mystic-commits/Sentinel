from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, JSON
from sentinel_core.models.enums import ActionType

class Preferences(SQLModel, table=True):
    """User preferences storage."""
    __tablename__ = "preferences"
    
    key: str = Field(primary_key=True)
    value: str # JSON encoded
    
    # Typed helpers could be added as methods or separate Pydantic schemas
    # used for validation before saving here.

class PreferencesSchema(SQLModel):
    """Pydantic schema for validation (not a table)."""
    preferred_destinations: dict[str, str] = {} # "extension": "folder_name"
    rejected_categories: List[str] = []
    delete_rules_enabled: bool = False
    excluded_extensions: List[str] = []


class PreferencePattern(SQLModel, table=True):
    """
    Learned patterns from user behavior.
    
    Stores patterns extracted from approved/rejected actions to improve
    future suggestions. Each pattern has a confidence score based on
    historical approval rate.
    
    Attributes:
        id: Auto-incrementing primary key
        pattern_type: Type of pattern (file_extension_destination, folder_structure, delete_approval)
        source_pattern: Pattern to match (e.g., ".pdf", "IMG_*", "temp_*")
        destination_pattern: Where files should go (for move/rename patterns)
        confidence: Approval rate (0.0 to 1.0)
        occurrence_count: How many times this pattern was seen
        approval_count: How many times user approved this pattern
        last_seen: When pattern was last encountered
        created_at: When pattern was first learned
    """
    __tablename__ = "preference_patterns"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    pattern_type: str = Field(index=True)  # "file_extension_destination", "folder_structure", "delete_approval"
    source_pattern: str = Field(index=True)  # e.g., ".pdf", "IMG_*", "temp_*"
    destination_pattern: Optional[str] = None  # e.g., "Documents/PDFs"
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)  # How often this pattern was approved
    occurrence_count: int = Field(default=0, ge=0)  # Number of times seen
    approval_count: int = Field(default=0, ge=0)  # Number of times approved
    last_seen: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)


class UserDecision(SQLModel, table=True):
    """
    Record of individual user decisions.
    
    Tracks every user approval, rejection, or modification to learn patterns.
    Used to calculate confidence scores and identify preferences.
    
    Attributes:
        id: Auto-incrementing primary key
        task_id: Associated task ID
        timestamp: When decision was made
        action_type: Type of action (MOVE, RENAME, DELETE, etc.)
        source_path: Original file path
        destination_path: Target path (if applicable)
        decision: User's decision (approved, rejected, modified)
        original_suggestion: What was originally suggested (if user modified)
        reason_code: Why user rejected/modified (optional)
    """
    __tablename__ = "user_decisions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: str = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.now, index=True)
    action_type: ActionType
    source_path: str
    destination_path: Optional[str] = None
    decision: str = Field(index=True)  # "approved", "rejected", "modified"
    original_suggestion: Optional[str] = None  # If user modified
    reason_code: Optional[str] = None  # Why rejected/modified

