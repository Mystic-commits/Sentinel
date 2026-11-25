"""
Tests for the Executor Module

Tests file operations, dry-run mode, and undo functionality.
"""

import pytest
from pathlib import Path

from sentinel_core.executor import Executor
from sentinel_core.models.enums import ActionType
from sentinel_core.models.planner import PlanAction, PlanSchema


class TestDryRunMode:
    """Tests for dry-run mode (no actual changes)."""
    
    @pytest.mark.asyncio
    async def test_dry_run_move(self, mock_fs):
        """Test that dry run doesn't actually move files."""
        source = mock_fs.create_file("source/file.txt", content="test content")
        dest_dir = mock_fs.create_directory("destination")
        dest_path = str(Path(dest_dir) / "file.txt")
        
        plan = PlanSchema(
            task_id="test-123",
            scope_path=str(mock_fs.root),
            actions=[
                PlanAction(confidence=1,
                    type=ActionType.MOVE,
                    source_path=source,
                    destination_path=dest_path,
                    reason="Test move"
                )
            ],
            summary="Move file"
        )
        
        executor = Executor()
        result = await executor.execute_plan(plan, dry_run=True)
        
        # Operation should succeed (in simulation)
        assert result.successful_actions == 1
        assert result.failed_actions == 0
        
        # But file should still be in original location
        assert Path(source).exists()
        assert not Path(dest_path).exists()
    
    @pytest.mark.asyncio
    async def test_dry_run_delete(self, mock_fs):
        """Test that dry run doesn't actually delete files."""
        file_path = mock_fs.create_file("file.txt", content="important data")
        
        plan = PlanSchema(
            task_id="test-123",
            scope_path=str(mock_fs.root),
            actions=[
                PlanAction(confidence=1,
                    type=ActionType.DELETE,
                    source_path=file_path,
                    reason="Test delete"
                )
            ],
            summary="Delete file"
        )
        
        executor = Executor()
        result = await executor.execute_plan(plan, dry_run=True)
        
        # Operation should succeed (in simulation)
        assert result.successful_actions == 1
        
        # But file should still exist
        assert Path(file_path).exists()


class TestMoveOperations:
    """Tests for actual move operations."""
    
    @pytest.mark.asyncio
    async def test_move_file(self, mock_fs):
        """Test moving a file to a new location."""
        content = "test content"
        source = mock_fs.create_file("source/file.txt", content=content)
        dest_dir = mock_fs.create_directory("destination")
        dest_path = str(Path(dest_dir) / "file.txt")
        
        plan = PlanSchema(
            task_id="test-123",
            scope_path=str(mock_fs.root),
            actions=[
                PlanAction(confidence=1,
                    type=ActionType.MOVE,
                    source_path=source,
                    destination_path=dest_path,
                    reason="Organize"
                )
            ],
            summary="Move file"
        )
        
        executor = Executor()
        result = await executor.execute_plan(plan, dry_run=False)
        
        assert result.successful_actions == 1
        assert result.failed_actions == 0
        
        # File should be in new location
        assert Path(dest_path).exists()
        assert Path(dest_path).read_text() == content
        
        # File should not be in old location
        assert not Path(source).exists()
    
    @pytest.mark.asyncio
    async def test_move_creates_destination_directory(self, mock_fs):
        """Test that move creates destination directory if needed."""
        source = mock_fs.create_file("file.txt", content="test")
        dest_path = mock_fs.get_path("new/nested/directory/file.txt")
        
        plan = PlanSchema(
            task_id="test-123",
            scope_path=str(mock_fs.root),
            actions=[
                PlanAction(confidence=1,
                    type=ActionType.MOVE,
                    source_path=source,
                    destination_path=dest_path,
                    reason="Move to new location"
                )
            ],
            summary="Move file"
        )
        
        executor = Executor()
        result = await executor.execute_plan(plan, dry_run=False)
        
        assert result.successful_actions == 1
        assert Path(dest_path).exists()


class TestDeleteOperations:
    """Tests for delete operations."""
    
    @pytest.mark.asyncio
    async def test_delete_to_trash(self, mock_fs):
        """Test that delete moves files to trash."""
        file_path = mock_fs.create_file("file.txt", content="to delete")
        
        plan = PlanSchema(
            task_id="test-123",
            scope_path=str(mock_fs.root),
            actions=[
                PlanAction(confidence=1,
                    type=ActionType.DELETE,
                    source_path=file_path,
                    reason="Cleanup"
                )
            ],
            summary="Delete file"
        )
        
        executor = Executor()
        result = await executor.execute_plan(plan, dry_run=False)
        
        assert result.successful_actions == 1
        
        # File should be gone from original location
        assert not Path(file_path).exists()
        
        # Note: Testing actual trash location is platform-specific
        # and may require additional implementation


class TestCopyOperations:
    """Tests for copy operations."""
    
class TestErrorHandling:
    """Tests for error handling."""
    
    @pytest.mark.asyncio
    async def test_nonexistent_source(self, mock_fs):
        """Test handling of nonexistent source files."""
        plan = PlanSchema(
            task_id="test-123",
            scope_path=str(mock_fs.root),
            actions=[
                PlanAction(confidence=1,
                    type=ActionType.MOVE,
                    source_path=mock_fs.get_path("nonexistent.txt"),
                    destination_path=mock_fs.get_path("dest.txt"),
                    reason="Should fail"
                )
            ],
            summary="Invalid operation"
        )
        
        executor = Executor()
        result = await executor.execute_plan(plan, dry_run=False)
        
        # Should report failure
        assert result.failed_actions == 1
        assert result.error_message
    
    @pytest.mark.asyncio
    async def test_partial_failure(self, mock_fs):
        """Test that execution stops after the first failure."""
        # Create two files, but only reference one correctly
        good_file = mock_fs.create_file("good.txt", content="exists")
        
        plan = PlanSchema(
            task_id="test-123",
            scope_path=str(mock_fs.root),
            actions=[
                PlanAction(confidence=1,
                    type=ActionType.DELETE,
                    source_path=mock_fs.get_path("nonexistent.txt"),
                    reason="Will fail"
                ),
                PlanAction(confidence=1,
                    type=ActionType.DELETE,
                    source_path=good_file,
                    reason="Will succeed"
                ),
            ],
            summary="Mixed operations"
        )
        
        executor = Executor()
        result = await executor.execute_plan(plan, dry_run=False)
        
        assert result.successful_actions == 0
        assert Path(good_file).exists()
        assert result.failed_actions == 1


class TestBatchOperations:
    """Tests for multiple operations."""
    
    @pytest.mark.asyncio
    async def test_multiple_moves(self, mock_fs):
        """Test moving multiple files."""
        files = []
        for i in range(5):
            files.append(mock_fs.create_file(f"source/file{i}.txt", content=f"content{i}"))
        
        dest_dir = mock_fs.create_directory("destination")
        
        operations = [
            PlanAction(confidence=1,
                type=ActionType.MOVE,
                source_path=f,
                destination_path=str(Path(dest_dir) / Path(f).name),
                reason="Batch move"
            )
            for f in files
        ]
        
        plan = PlanSchema(
            task_id="test-123",
            scope_path=str(mock_fs.root),
            actions=operations,
            summary="Move multiple files"
        )
        
        executor = Executor()
        result = await executor.execute_plan(plan, dry_run=False)
        
        assert result.successful_actions == 5
        assert result.failed_actions == 0
        
        # All files should be in destination
        for i in range(5):
            assert Path(dest_dir, f"file{i}.txt").exists()
