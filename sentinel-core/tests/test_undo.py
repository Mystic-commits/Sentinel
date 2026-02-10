"""
Tests for the undo module.

Verifies operation reversal and undo management.
"""

import pytest
import tempfile
import os
import shutil
from pathlib import Path
from sqlmodel import create_engine, Session, SQLModel

from sentinel_core.models import (
    PlanSchema, PlanAction, ActionType,
    ExecutionLogEntry, TaskRecord
)
from sentinel_core.executor import execute_plan, UndoManager


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    # Cleanup
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)


@pytest.fixture
def db_session():
    """Create an in-memory database session for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_undo_move_operation(temp_dir, db_session):
    """Test undoing a move operation."""
    # Setup
    source = os.path.join(temp_dir, "file.txt")
    dest = os.path.join(temp_dir, "moved", "file.txt")
    
    with open(source, "w") as f:
        f.write("content")
    
    # Create task record
    task = TaskRecord(
        task_id="test_undo_move",
        user_prompt="Test",
        undo_available=True
    )
    db_session.add(task)
    db_session.commit()
    
    # Execute move
    plan = PlanSchema(
        task_id="test_undo_move",
        scope_path=temp_dir,
        actions=[
            PlanAction(
                type=ActionType.MOVE,
                source_path=source,
                destination_path=dest,
                reason="Test",
                confidence=1.0
            )
        ],
        summary="Test"
    )
    
    exec_result = execute_plan(plan, db_session=db_session)
    assert exec_result.successful_actions == 1
    assert os.path.exists(dest)
    assert not os.path.exists(source)
    
    # Undo
    undo_mgr = UndoManager(db_session)
    undo_result = undo_mgr.undo_task("test_undo_move")
    
    assert undo_result.successful_actions == 1
    assert undo_result.failed_actions == 0
    # File should be back at original location
    assert os.path.exists(source)
    assert not os.path.exists(dest)


def test_undo_rename_operation(temp_dir, db_session):
    """Test undoing a rename operation."""
    source = os.path.join(temp_dir, "old.txt")
    dest = os.path.join(temp_dir, "new.txt")
    
    with open(source, "w") as f:
        f.write("content")
    
    task = TaskRecord(
        task_id="test_undo_rename",
        user_prompt="Test",
        undo_available=True
    )
    db_session.add(task)
    db_session.commit()
    
    plan = PlanSchema(
        task_id="test_undo_rename",
        scope_path=temp_dir,
        actions=[
            PlanAction(
                type=ActionType.RENAME,
                source_path=source,
                destination_path=dest,
                reason="Test",
                confidence=1.0
            )
        ],
        summary="Test"
    )
    
    execute_plan(plan, db_session=db_session)
    assert os.path.exists(dest)
    
    undo_mgr = UndoManager(db_session)
    undo_result = undo_mgr.undo_task("test_undo_rename")
    
    assert undo_result.successful_actions == 1
    assert os.path.exists(source)
    assert not os.path.exists(dest)


def test_undo_mixed_operations(temp_dir, db_session):
    """Test undoing multiple different operations."""
    file1 = os.path.join(temp_dir, "file1.txt")
    file2 = os.path.join(temp_dir, "file2.txt")
    
    for f in [file1, file2]:
        with open(f, "w") as file:
            file.write("content")
    
    task = TaskRecord(
        task_id="test_undo_mixed",
        user_prompt="Test",
        undo_available=True
    )
    db_session.add(task)
    db_session.commit()
    
    folder = os.path.join(temp_dir, "folder")
    
    plan = PlanSchema(
        task_id="test_undo_mixed",
        scope_path=temp_dir,
        folders_to_create=[folder],
        actions=[
            PlanAction(
                type=ActionType.MOVE,
                source_path=file1,
                destination_path=os.path.join(folder, "file1.txt"),
                reason="Move",
                confidence=1.0
            ),
            PlanAction(
                type=ActionType.RENAME,
                source_path=file2,
                destination_path=os.path.join(temp_dir, "renamed.txt"),
                reason="Rename",
                confidence=1.0
            ),
        ],
        summary="Test"
    )
    
    execute_plan(plan, db_session=db_session)
    
    undo_mgr = UndoManager(db_session)
    undo_result = undo_mgr.undo_task("test_undo_mixed")
    
    # Both file operations should be undone
    assert os.path.exists(file1)
    assert os.path.exists(file2)


def test_undo_delete_not_possible(temp_dir, db_session):
    """Test that delete operations cannot be automatically undone."""
    file_path = os.path.join(temp_dir, "delete.txt")
    with open(file_path, "w") as f:
        f.write("content")
    
    task = TaskRecord(
        task_id="test_undo_delete",
        user_prompt="Test",
        undo_available=True
    )
    db_session.add(task)
    db_session.commit()
    
    plan = PlanSchema(
        task_id="test_undo_delete",
        scope_path=temp_dir,
        actions=[
            PlanAction(
                type=ActionType.DELETE,
                source_path=file_path,
                destination_path=None,
                reason="Delete",
                confidence=1.0
            )
        ],
        summary="Test"
    )
    
    execute_plan(plan, db_session=db_session)
    
    undo_mgr = UndoManager(db_session)
    undo_result = undo_mgr.undo_task("test_undo_delete")
    
    # Delete should report as failed undo
    assert undo_result.failed_actions > 0
    assert "cannot be automatically undone" in undo_result.error_message.lower()


def test_undo_task_twice_fails(temp_dir, db_session):
    """Test that a task cannot be undone twice."""
    source = os.path.join(temp_dir, "file.txt")
    dest = os.path.join(temp_dir, "dest.txt")
    
    with open(source, "w") as f:
        f.write("content")
    
    task = TaskRecord(
        task_id="test_double_undo",
        user_prompt="Test",
        undo_available=True
    )
    db_session.add(task)
    db_session.commit()
    
    plan = PlanSchema(
        task_id="test_double_undo",
        scope_path=temp_dir,
        actions=[
            PlanAction(
                type=ActionType.MOVE,
                source_path=source,
                destination_path=dest,
                reason="Test",
                confidence=1.0
            )
        ],
        summary="Test"
    )
    
    execute_plan(plan, db_session=db_session)
    
    undo_mgr = UndoManager(db_session)
    
    # First undo should succeed
    undo_result1 = undo_mgr.undo_task("test_double_undo")
    assert undo_result1.successful_actions == 1
    
    # Second undo should fail
    with pytest.raises(ValueError, match="already been undone"):
        undo_mgr.undo_task("test_double_undo")


def test_can_undo_task_validation(temp_dir, db_session):
    """Test undo feasibility check."""
    source = os.path.join(temp_dir, "file.txt")
    dest = os.path.join(temp_dir, "dest.txt")
    
    with open(source, "w") as f:
        f.write("content")
    
    task = TaskRecord(
        task_id="test_can_undo",
        user_prompt="Test",
        undo_available=True
    )
    db_session.add(task)
    db_session.commit()
    
    plan = PlanSchema(
        task_id="test_can_undo",
        scope_path=temp_dir,
        actions=[
            PlanAction(
                type=ActionType.MOVE,
                source_path=source,
                destination_path=dest,
                reason="Test",
                confidence=1.0
            )
        ],
        summary="Test"
    )
    
    undo_mgr = UndoManager(db_session)
    
    # Before execution - no operations to undo
    can_undo, reason = undo_mgr.can_undo_task("test_can_undo")
    assert not can_undo
    assert "No successful operations" in reason
    
    # After execution - should be able to undo
    execute_plan(plan, db_session=db_session)
    can_undo, reason = undo_mgr.can_undo_task("test_can_undo")
    assert can_undo
    assert reason is None
    
    # After undo - cannot undo again
    undo_mgr.undo_task("test_can_undo")
    can_undo, reason = undo_mgr.can_undo_task("test_can_undo")
    assert not can_undo
    assert "already been undone" in reason


def test_get_undo_operations(temp_dir, db_session):
    """Test undo preview functionality."""
    file1 = os.path.join(temp_dir, "file1.txt")
    file2 = os.path.join(temp_dir, "file2.txt")
    file3 = os.path.join(temp_dir, "file3.txt")
    
    for f in [file1, file2, file3]:
        with open(f, "w") as file:
            file.write("content")
    
    task = TaskRecord(
        task_id="test_undo_preview",
        user_prompt="Test",
        undo_available=True
    )
    db_session.add(task)
    db_session.commit()
    
    plan = PlanSchema(
        task_id="test_undo_preview",
        scope_path=temp_dir,
        actions=[
            PlanAction(
                type=ActionType.MOVE,
                source_path=file1,
                destination_path=os.path.join(temp_dir, "moved.txt"),
                reason="Move",
                confidence=1.0
            ),
            PlanAction(
                type=ActionType.RENAME,
                source_path=file2,
                destination_path=os.path.join(temp_dir, "renamed.txt"),
                reason="Rename",
                confidence=1.0
            ),
            PlanAction(
                type=ActionType.DELETE,
                source_path=file3,
                destination_path=None,
                reason="Delete",
                confidence=1.0
            ),
        ],
        summary="Test"
    )
    
    execute_plan(plan, db_session=db_session)
    
    undo_mgr = UndoManager(db_session)
    undo_ops = undo_mgr.get_undo_operations("test_undo_preview")
    
    assert len(undo_ops) == 3
    
    # Check that move and rename can be undone
    move_op = next(op for op in undo_ops if op.action_type == ActionType.MOVE)
    assert move_op.can_undo is True
    
    rename_op = next(op for op in undo_ops if op.action_type == ActionType.RENAME)
    assert rename_op.can_undo is True
    
    # Check that delete cannot be undone
    delete_op = next(op for op in undo_ops if op.action_type == ActionType.DELETE)
    assert delete_op.can_undo is False
    assert "cannot be automatically undone" in delete_op.undo_reason.lower()


def test_undo_fails_if_file_moved_again(temp_dir, db_session):
    """Test undo validation when file has been moved again."""
    source = os.path.join(temp_dir, "file.txt")
    dest = os.path.join(temp_dir, "dest.txt")
    other = os.path.join(temp_dir, "other.txt")
    
    with open(source, "w") as f:
        f.write("content")
    
    task = TaskRecord(
        task_id="test_undo_moved_file",
        user_prompt="Test",
        undo_available=True
    )
    db_session.add(task)
    db_session.commit()
    
    plan = PlanSchema(
        task_id="test_undo_moved_file",
        scope_path=temp_dir,
        actions=[
            PlanAction(
                type=ActionType.MOVE,
                source_path=source,
                destination_path=dest,
                reason="Test",
                confidence=1.0
            )
        ],
        summary="Test"
    )
    
    execute_plan(plan, db_session=db_session)
    
    # Move the file again manually
    shutil.move(dest, other)
    
    # Undo should detect that file is not at expected location
    undo_mgr = UndoManager(db_session)
    undo_ops = undo_mgr.get_undo_operations("test_undo_moved_file")
    
    assert undo_ops[0].can_undo is False
    assert "no longer exists" in undo_ops[0].undo_reason.lower()
