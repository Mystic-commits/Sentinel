import pytest
from datetime import datetime
from sentinel_core.models import (
    FileMetadata, FileType, PlanSchema, PlanAction, ActionType
)

def test_file_metadata_valid():
    """Test valid file metadata creation."""
    fm = FileMetadata(
        path="/tmp/test.txt",
        name="test.txt",
        extension="txt",
        size_bytes=1024,
        created_at=datetime.now(),
        modified_at=datetime.now(),
        file_type=FileType.DOCUMENT
    )
    assert fm.name == "test.txt"
    assert fm.file_type == FileType.DOCUMENT

def test_plan_schema_validation():
    """Test strict validation of PlanSchema."""
    # Valid Plan
    plan = PlanSchema(
        task_id="123",
        scope_path="/tmp",
        actions=[
            PlanAction(
                type=ActionType.MOVE,
                source_path="/tmp/a",
                destination_path="/tmp/b",
                reason="test",
                confidence=0.9
            )
        ],
        summary="Moving items"
    )
    assert len(plan.actions) == 1

def test_plan_action_invalid_destination():
    """Test that MOVE requires a destination."""
    with pytest.raises(ValueError):
        PlanAction(
            type=ActionType.MOVE,
            source_path="/tmp/a",
            destination_path=None, # Should fail
            reason="test",
            confidence=1.0
        )
