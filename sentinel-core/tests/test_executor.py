"""
Tests for the Executor Module

Tests file operations, dry-run mode, and undo functionality.
"""

import pytest
from pathlib import Path

from sentinel_core.executor.executor import Executor
from sentinel_core.models.planner import PlanSchema, OperationSchema, OperationType


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
            operations=[
                OperationSchema(
                    type=OperationType.MOVE,
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
        assert result.success_count == 1
        assert result.failure_count == 0
        
        # But file should still be in original location
        assert Path(source).exists()
        assert not Path(dest_path).exists()
    
    @pytest.mark.asyncio
    async def test_dry_run_delete(self, mock_fs):
        """Test that dry run doesn't actually delete files."""
        file_path = mock_fs.create_file("file.txt", content="important data")
        
        plan = PlanSchema(
            task_id="test-123",
            operations=[
                OperationSchema(
                    type=OperationType.DELETE,
                    source_path=file_path,
                    reason="Test delete"
                )
            ],
            summary="Delete file"
        )
        
        executor = Executor()
        result = await executor.execute_plan(plan, dry_run=True)
        
        # Operation should succeed (in simulation)
        assert result.success_count == 1
        
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
            operations=[
                OperationSchema(
                    type=OperationType.MOVE,
                    source_path=source,
                    destination_path=dest_path,
                    reason="Organize"
                )
            ],
            summary="Move file"
        )
        
        executor = Executor()
        result = await executor.execute_plan(plan, dry_run=False)
        
        assert result.success_count == 1
        assert result.failure_count == 0
        
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
            operations=[
                OperationSchema(
                    type=OperationType.MOVE,
                    source_path=source,
                    destination_path=dest_path,
                    reason="Move to new location"
                )
            ],
            summary="Move file"
        )
        
        executor = Executor()
        result = await executor.execute_plan(plan, dry_run=False)
        
        assert result.success_count == 1
        assert Path(dest_path).exists()


class TestDeleteOperations:
    """Tests for delete operations."""
    
    @pytest.mark.asyncio
    async def test_delete_to_trash(self, mock_fs):
        """Test that delete moves files to trash."""
        file_path = mock_fs.create_file("file.txt", content="to delete")
        
        plan = PlanSchema(
            task_id="test-123",
            operations=[
                OperationSchema(
                    type=OperationType.DELETE,
                    source_path=file_path,
                    reason="Cleanup"
                )
            ],
            summary="Delete file"
        )
        
        executor = Executor()
        result = await executor.execute_plan(plan, dry_run=False)
        
        assert result.success_count == 1
        
        # File should be gone from original location
        assert not Path(file_path).exists()
        
        # Note: Testing actual trash location is platform-specific
        # and may require additional implementation


class TestCopyOperations:
    """Tests for copy operations."""
    
    @pytest.mark.asyncio
    async def test_copy_file(self, mock_fs):
        """Test copying a file."""
        content = "original content"
        source = mock_fs.create_file("source.txt", content=content)
        dest = mock_fs.get_path("copy.txt")
        
        plan = PlanSchema(
            task_id="test-123",
            operations=[
                OperationSchema(
                    type=OperationType.COPY,
                    source_path=source,
                    destination_path=dest,
                    reason="Backup"
                )
            ],
            summary="Copy file"
        )
        
        executor = Executor()
        result = await executor.execute_plan(plan, dry_run=False)
        
        assert result.success_count == 1
        
        # Both files should exist
        assert Path(source).exists()
        assert Path(dest).exists()
        
        # Content should be identical
        assert Path(dest).read_text() == content


class TestErrorHandling:
    """Tests for error handling."""
    
    @pytest.mark.asyncio
    async def test_nonexistent_source(self, mock_fs):
        """Test handling of nonexistent source files."""
        plan = PlanSchema(
            task_id="test-123",
            operations=[
                OperationSchema(
                    type=OperationType.MOVE,
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
        assert result.failure_count == 1
        assert len(result.errors) > 0
    
    @pytest.mark.asyncio
    async def test_partial_failure(self, mock_fs):
        """Test that execution continues after failures."""
        # Create two files, but only reference one correctly
        good_file = mock_fs.create_file("good.txt", content="exists")
        
        plan = PlanSchema(
            task_id="test-123",
            operations=[
                OperationSchema(
                    type=OperationType.DELETE,
                    source_path=mock_fs.get_path("nonexistent.txt"),
                    reason="Will fail"
                ),
                OperationSchema(
                    type=OperationType.DELETE,
                    source_path=good_file,
                    reason="Will succeed"
                ),
            ],
            summary="Mixed operations"
        )
        
        executor = Executor()
        result = await executor.execute_plan(plan, dry_run=False)
        
        # Should have both success and failure
        assert result.success_count == 1
        assert result.failure_count == 1


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
            OperationSchema(
                type=OperationType.MOVE,
                source_path=f,
                destination_path=str(Path(dest_dir) / Path(f).name),
                reason="Batch move"
            )
            for f in files
        ]
        
        plan = PlanSchema(
            task_id="test-123",
            operations=operations,
            summary="Move multiple files"
        )
        
        executor = Executor()
        result = await executor.execute_plan(plan, dry_run=False)
        
        assert result.success_count == 5
        assert result.failure_count == 0
        
        # All files should be in destination
        for i in range(5):
            assert Path(dest_dir, f"file{i}.txt").exists()


class TestUndoFunctionality:
    """Tests for undo functionality."""
    
    @pytest.mark.asyncio
    async def test_undo_move_operation(self, mock_fs):
        """Test undoing a move operation."""
        # This is a placeholder - actual undo implementation needed
        # The test demonstrates what undo should do
        
        original_path = mock_fs.create_file("original/file.txt", content="data")
        new_path = mock_fs.get_path("new/file.txt")
        
        # TODO: Implement undo functionality in executor
        # For now, this test is skipped
        pytest.skip("Undo functionality not yet implemented")
