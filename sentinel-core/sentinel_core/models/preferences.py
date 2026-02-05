from typing import List, Optional
from sqlmodel import SQLModel, Field, JSON

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
