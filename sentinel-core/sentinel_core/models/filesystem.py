from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from sentinel_core.models.enums import FileType

class FileMetadata(BaseModel):
    """Represents metadata for a single file on the filesystem."""
    path: str
    name: str
    extension: str
    size_bytes: int
    created_at: datetime
    modified_at: datetime
    file_type: FileType
    is_hidden: bool = False
    preview_text: Optional[str] = Field(default=None, max_length=150, description="Short preview of text content")
    hash: Optional[str] = Field(default=None, description="SHA-256 hash if computed")

    class Config:
        from_attributes = True

class ScanResult(BaseModel):
    """Result of a directory scan."""
    root_path: str
    files: List[FileMetadata]
    ignored_count: int = 0
    errors: List[str] = []
    scanned_at: datetime = Field(default_factory=datetime.now)
