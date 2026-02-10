"""
Tests for the plan preview module.

Verifies both terminal and web preview output for various plan scenarios.
"""

import pytest
from sentinel_core.models import PlanSchema, PlanAction, ActionType, AmbiguousFile
from sentinel_core.preview import generate_terminal_preview, generate_web_preview


@pytest.fixture
def sample_plan_full():
    """Create a comprehensive plan with all action types."""
    return PlanSchema(
        task_id="test_full_plan",
        scope_path="/Users/test/Downloads",
        folders_to_create=[
            "/Users/test/Downloads/PDFs",
            "/Users/test/Downloads/Images"
        ],
        actions=[
            PlanAction(
                type=ActionType.MOVE,
                source_path="/Users/test/Downloads/document.pdf",
                destination_path="/Users/test/Downloads/PDFs/document.pdf",
                reason="PDF file should be in PDFs folder",
                confidence=0.95
            ),
            PlanAction(
                type=ActionType.RENAME,
                source_path="/Users/test/Downloads/img_001.jpg",
                destination_path="/Users/test/Downloads/vacation_photo.jpg",
                reason="Rename to descriptive name",
                confidence=0.85
            ),
            PlanAction(
                type=ActionType.DELETE,
                source_path="/Users/test/Downloads/temp_file.tmp",
                destination_path=None,
                reason="Temporary file no longer needed",
                confidence=0.9
            ),
            PlanAction(
                type=ActionType.SKIP,
                source_path="/Users/test/Downloads/important.txt",
                destination_path=None,
                reason="User marked as important",
                confidence=1.0
            ),
        ],
        ambiguous_files=[
            AmbiguousFile(
                path="/Users/test/Downloads/unknown.dat",
                reason="Unknown file format",
                suggested_action=ActionType.SKIP
            )
        ],
        summary="Organizing Downloads folder with mixed operations"
    )


@pytest.fixture
def sample_plan_empty():
    """Create an empty plan with no actions."""
    return PlanSchema(
        task_id="test_empty",
        scope_path="/Users/test/Downloads",
        actions=[],
        summary="No actions needed"
    )


@pytest.fixture
def sample_plan_deletes_only():
    """Create a plan with only delete operations."""
    return PlanSchema(
        task_id="test_deletes",
        scope_path="/Users/test/Downloads",
        actions=[
            PlanAction(
                type=ActionType.DELETE,
                source_path="/Users/test/Downloads/file1.tmp",
                destination_path=None,
                reason="Temporary file",
                confidence=0.8
            ),
            PlanAction(
                type=ActionType.DELETE,
                source_path="/Users/test/Downloads/file2.tmp",
                destination_path=None,
                reason="Temporary file",
                confidence=0.85
            ),
        ],
        summary="Cleaning up temporary files"
    )


def test_terminal_preview_full_plan(sample_plan_full):
    """Test terminal preview with all action types."""
    preview = generate_terminal_preview(sample_plan_full)
    
    # Verify basic structure
    assert isinstance(preview, str)
    assert len(preview) > 0
    
    # Verify key sections appear
    assert "Plan Preview" in preview
    assert "test_full_plan" in preview
    assert "/Users/test/Downloads" in preview
    assert "Organizing Downloads folder" in preview
    
    # Verify section headers
    assert "Folders to Create" in preview
    assert "Move Operations" in preview
    assert "Rename Operations" in preview
    assert "Delete Operations" in preview
    assert "Skipped Files" in preview
    assert "Ambiguous Files" in preview
    
    # Verify specific items
    assert "PDFs" in preview
    assert "Images" in preview
    assert "document.pdf" in preview
    assert "vacation_photo.jpg" in preview
    assert "temp_file.tmp" in preview
    assert "important.txt" in preview
    assert "unknown.dat" in preview
    
    # Verify summary section
    assert "Summary" in preview
    assert "Total Actions:" in preview


def test_terminal_preview_empty_plan(sample_plan_empty):
    """Test terminal preview with no actions."""
    preview = generate_terminal_preview(sample_plan_empty)
    
    assert isinstance(preview, str)
    assert "test_empty" in preview
    assert "No actions needed" in preview
    # Should still have header and summary
    assert "Plan Preview" in preview
    assert "Summary" in preview


def test_terminal_preview_deletes_only(sample_plan_deletes_only):
    """Test terminal preview with only delete operations (high-risk scenario)."""
    preview = generate_terminal_preview(sample_plan_deletes_only)
    
    assert isinstance(preview, str)
    assert "Delete Operations" in preview
    assert "file1.tmp" in preview
    assert "file2.tmp" in preview
    assert "Cleaning up temporary files" in preview


def test_web_preview_structure(sample_plan_full):
    """Test web preview returns correct JSON structure."""
    preview = generate_web_preview(sample_plan_full)
    
    # Verify top-level structure
    assert isinstance(preview, dict)
    assert "task_id" in preview
    assert "scope_path" in preview
    assert "summary" in preview
    assert "operations" in preview
    assert "ambiguous_files" in preview
    assert "stats" in preview
    
    # Verify operations structure
    ops = preview["operations"]
    assert "folders_to_create" in ops
    assert "moves" in ops
    assert "renames" in ops
    assert "deletes" in ops
    assert "skips" in ops
    
    # Verify data correctness
    assert preview["task_id"] == "test_full_plan"
    assert len(ops["folders_to_create"]) == 2
    assert len(ops["moves"]) == 1
    assert len(ops["renames"]) == 1
    assert len(ops["deletes"]) == 1
    assert len(ops["skips"]) == 1
    assert len(preview["ambiguous_files"]) == 1


def test_web_preview_move_structure(sample_plan_full):
    """Test move operation structure in web preview."""
    preview = generate_web_preview(sample_plan_full)
    
    move = preview["operations"]["moves"][0]
    assert "from" in move
    assert "to" in move
    assert "reason" in move
    assert "confidence" in move
    
    assert move["from"] == "/Users/test/Downloads/document.pdf"
    assert move["to"] == "/Users/test/Downloads/PDFs/document.pdf"
    assert move["confidence"] == 0.95


def test_web_preview_delete_structure(sample_plan_full):
    """Test delete operation structure in web preview."""
    preview = generate_web_preview(sample_plan_full)
    
    delete = preview["operations"]["deletes"][0]
    assert "path" in delete
    assert "reason" in delete
    assert "confidence" in delete
    
    assert delete["path"] == "/Users/test/Downloads/temp_file.tmp"
    assert delete["confidence"] == 0.9


def test_web_preview_statistics(sample_plan_full):
    """Test statistics calculation in web preview."""
    preview = generate_web_preview(sample_plan_full)
    
    stats = preview["stats"]
    assert stats["total_actions"] == 4
    assert stats["folders"] == 2
    assert stats["moves"] == 1
    assert stats["renames"] == 1
    assert stats["deletes"] == 1
    assert stats["skips"] == 1
    assert stats["ambiguous"] == 1
    
    # Average confidence: (0.95 + 0.85 + 0.9 + 1.0) / 4 = 0.925
    assert stats["avg_confidence"] == pytest.approx(0.925, rel=0.01)


def test_web_preview_empty_plan(sample_plan_empty):
    """Test web preview with empty plan."""
    preview = generate_web_preview(sample_plan_empty)
    
    stats = preview["stats"]
    assert stats["total_actions"] == 0
    assert stats["folders"] == 0
    assert stats["moves"] == 0
    assert stats["avg_confidence"] == 0.0


def test_ambiguous_files_display(sample_plan_full):
    """Test ambiguous files are properly displayed."""
    # Terminal preview
    terminal = generate_terminal_preview(sample_plan_full)
    assert "Ambiguous Files" in terminal
    assert "unknown.dat" in terminal
    assert "Unknown file format" in terminal
    
    # Web preview
    web = generate_web_preview(sample_plan_full)
    ambiguous = web["ambiguous_files"][0]
    assert ambiguous["path"] == "/Users/test/Downloads/unknown.dat"
    assert ambiguous["reason"] == "Unknown file format"
    assert ambiguous["suggested_action"] == "skip"


def test_path_shortening():
    """Test that paths are properly shortened in terminal preview."""
    plan = PlanSchema(
        task_id="test_paths",
        scope_path="/Users/test/Downloads",
        actions=[
            PlanAction(
                type=ActionType.MOVE,
                source_path="/Users/test/Downloads/subfolder/file.txt",
                destination_path="/Users/test/Downloads/organized/file.txt",
                reason="Test",
                confidence=0.9
            )
        ],
        summary="Test path shortening"
    )
    
    preview = generate_terminal_preview(plan)
    # Paths should be shortened to relative format
    assert "./subfolder/file.txt" in preview or "subfolder/file.txt" in preview
    assert "./organized/file.txt" in preview or "organized/file.txt" in preview


def test_confidence_levels():
    """Test different confidence levels are handled correctly."""
    plan = PlanSchema(
        task_id="test_confidence",
        scope_path="/tmp",
        actions=[
            PlanAction(
                type=ActionType.MOVE,
                source_path="/tmp/high.txt",
                destination_path="/tmp/dest/high.txt",
                reason="High confidence",
                confidence=0.95
            ),
            PlanAction(
                type=ActionType.MOVE,
                source_path="/tmp/medium.txt",
                destination_path="/tmp/dest/medium.txt",
                reason="Medium confidence",
                confidence=0.75
            ),
            PlanAction(
                type=ActionType.MOVE,
                source_path="/tmp/low.txt",
                destination_path="/tmp/dest/low.txt",
                reason="Low confidence",
                confidence=0.5
            ),
        ],
        summary="Testing confidence levels"
    )
    
    # Should not crash with different confidence levels
    terminal = generate_terminal_preview(plan)
    assert "95%" in terminal
    assert "75%" in terminal
    assert "50%" in terminal
    
    web = generate_web_preview(plan)
    assert web["stats"]["avg_confidence"] == pytest.approx(0.733, rel=0.01)
