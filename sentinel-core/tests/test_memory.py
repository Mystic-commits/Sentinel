"""
Tests for the preference memory module.

Verifies learning from user decisions and suggestion accuracy.
"""

import pytest
import tempfile
import os
from datetime import datetime
from sqlmodel import create_engine, Session, SQLModel

from sentinel_core.models import (
    PreferencePattern,
    UserDecision,
    ActionType,
    ExecutionResult,
    ExecutionLogEntry
)
from sentinel_core.memory import PreferenceMemory
from sentinel_core.memory.db import create_tables


@pytest.fixture
def db_session():
    """Create an in-memory database session for testing."""
    engine = create_engine("sqlite:///:memory:")
    create_tables(engine)
    with Session(engine) as session:
        yield session


def test_load_empty_preferences(db_session):
    """Test loading preferences from empty database."""
    memory = PreferenceMemory(db_session)
    prefs = memory.load_preferences()
    
    assert prefs["extension_destinations"] == {}
    assert prefs["folder_patterns"] == []
    assert prefs["delete_preferences"] == {}


def test_learn_from_move_approval(db_session):
    """Test learning destination pattern from approved move."""
    memory = PreferenceMemory(db_session)
    
    # Create approved decision
    decision = UserDecision(
        task_id="test_1",
        timestamp=datetime.now(),
        action_type=ActionType.MOVE,
        source_path="/tmp/document.pdf",
        destination_path="/home/Documents/PDFs/document.pdf",
        decision="approved"
    )
    
    # Create dummy execution result
    exec_result = ExecutionResult(
        task_id="test_1",
        total_actions=1,
        successful_actions=1,
        failed_actions=0,
        execution_logs=[]
    )
    
    # Learn from decision
    memory.update_preferences(exec_result, [decision])
    
    # Verify pattern was learned
    prefs = memory.load_preferences()
    assert ".pdf" in prefs["extension_destinations"]
    assert prefs["extension_destinations"][".pdf"]["destination"] == "/home/Documents/PDFs"
    assert prefs["extension_destinations"][".pdf"]["confidence"] > 0


def test_learn_from_delete_approval(db_session):
    """Test learning delete pattern from approved deletion."""
    memory = PreferenceMemory(db_session)
    
    decision = UserDecision(
        task_id="test_2",
        timestamp=datetime.now(),
        action_type=ActionType.DELETE,
        source_path="/tmp/cache.tmp",
        destination_path=None,
        decision="approved"
    )
    
    exec_result = ExecutionResult(
        task_id="test_2",
        total_actions=1,
        successful_actions=1,
        failed_actions=0,
        execution_logs=[]
    )
    
    memory.update_preferences(exec_result, [decision])
    
    # Verify pattern was learned
    prefs = memory.load_preferences()
    assert ".tmp" in prefs["delete_preferences"]
    assert prefs["delete_preferences"][".tmp"]["should_delete"] is True


def test_confidence_increases_with_approvals(db_session):
    """Test that confidence increases with consistent approvals."""
    memory = PreferenceMemory(db_session)
    
    # Approve PDF -> Documents/PDFs multiple times
    for i in range(5):
        decision = UserDecision(
            task_id=f"test_{i}",
            timestamp=datetime.now(),
            action_type=ActionType.MOVE,
            source_path=f"/tmp/doc{i}.pdf",
            destination_path=f"/home/Documents/PDFs/doc{i}.pdf",
            decision="approved"
        )
        
        exec_result = ExecutionResult(
            task_id=f"test_{i}",
            total_actions=1,
            successful_actions=1,
            failed_actions=0,
            execution_logs=[]
        )
        
        memory.update_preferences(exec_result, [decision])
    
    # Check confidence increased
    prefs = memory.load_preferences()
    confidence = prefs["extension_destinations"][".pdf"]["confidence"]
    assert confidence > 0.8  # Should be high after 5 approvals


def test_suggest_destination_based_on_pattern(db_session):
    """Test destination suggestion based on learned patterns."""
    memory = PreferenceMemory(db_session)
    
    # Learn pattern: .jpg -> Photos/
    decision = UserDecision(
        task_id="test",
        timestamp=datetime.now(),
        action_type=ActionType.MOVE,
        source_path="/tmp/image.jpg",
        destination_path="/home/Photos/image.jpg",
        decision="approved"
    )
    
    exec_result = ExecutionResult(
        task_id="test",
        total_actions=1,
        successful_actions=1,
        failed_actions=0,
        execution_logs=[]
    )
    
    memory.update_preferences(exec_result, [decision])
    
    # Test suggestion
    suggestion, confidence = memory.suggest_destination("another_image.jpg")
    assert suggestion == "/home/Photos"
    assert confidence > 0


def test_suggest_destination_no_pattern(db_session):
    """Test suggestion returns None when no pattern exists."""
    memory = PreferenceMemory(db_session)
    
    # No patterns learned
    result = memory.suggest_destination("unknown.xyz")
    assert result is None


def test_should_delete_based_on_pattern(db_session):
    """Test delete recommendation based on learned patterns."""
    memory = PreferenceMemory(db_session)
    
    # Approve deleting .log files multiple times
    for i in range(5):
        decision = UserDecision(
            task_id=f"test_{i}",
            timestamp=datetime.now(),
            action_type=ActionType.DELETE,
            source_path=f"/tmp/log{i}.log",
            destination_path=None,
            decision="approved"
        )
        
        exec_result = ExecutionResult(
            task_id=f"test_{i}",
            total_actions=1,
            successful_actions=1,
            failed_actions=0,
            execution_logs=[]
        )
        
        memory.update_preferences(exec_result, [decision])
    
    # Test recommendation
    should_delete, confidence = memory.should_delete("debug.log")
    assert should_delete is True
    assert confidence > 0.7


def test_should_delete_unknown_type(db_session):
    """Test delete recommendation for unknown file type."""
    memory = PreferenceMemory(db_session)
    
    should_delete, confidence = memory.should_delete("important.doc")
    assert should_delete is False
    assert confidence == 0.0


def test_learn_from_rejection(db_session):
    """Test that rejections don't increase confidence."""
    memory = PreferenceMemory(db_session)
    
    # Approve once
    decision1 = UserDecision(
        task_id="test_1",
        timestamp=datetime.now(),
        action_type=ActionType.MOVE,
        source_path="/tmp/file.txt",
        destination_path="/home/Text/file.txt",
        decision="approved"
    )
    
    exec_result1 = ExecutionResult(
        task_id="test_1",
        total_actions=1,
        successful_actions=1,
        failed_actions=0,
        execution_logs=[]
    )
    
    memory.update_preferences(exec_result1, [decision1])
    
    # Get initial confidence
    prefs1 = memory.load_preferences()
    initial_confidence = prefs1["extension_destinations"][".txt"]["confidence"]
    
    # Reject similar action
    decision2 = UserDecision(
        task_id="test_2",
        timestamp=datetime.now(),
        action_type=ActionType.MOVE,
        source_path="/tmp/file2.txt",
        destination_path="/home/Text/file2.txt",
        decision="rejected"
    )
    
    exec_result2 = ExecutionResult(
        task_id="test_2",
        total_actions=1,
        successful_actions=0,
        failed_actions=1,
        execution_logs=[]
    )
    
    memory.update_preferences(exec_result2, [decision2])
    
    # Confidence should not increase (might decrease)
    prefs2 = memory.load_preferences()
    new_confidence = prefs2["extension_destinations"][".txt"]["confidence"]
    assert new_confidence <= initial_confidence


def test_prune_low_confidence_patterns(db_session):
    """Test that low-confidence patterns are pruned."""
    memory = PreferenceMemory(db_session)
    
    # Create a low-confidence pattern manually
    low_conf_pattern = PreferencePattern(
        pattern_type="file_extension_destination",
        source_pattern=".xyz",
        destination_pattern="/tmp",
        confidence=0.2,  # Low confidence
        occurrence_count=2,  # Few occurrences
        approval_count=0
    )
    
    db_session.add(low_conf_pattern)
    db_session.commit()
    
    # Trigger learning (which includes pruning)
    decision = UserDecision(
        task_id="test",
        timestamp=datetime.now(),
        action_type=ActionType.MOVE,
        source_path="/tmp/doc.pdf",
        destination_path="/home/PDFs/doc.pdf",
        decision="approved"
    )
    
    exec_result = ExecutionResult(
        task_id="test",
        total_actions=1,
        successful_actions=1,
        failed_actions=0,
        execution_logs=[]
    )
    
    memory.update_preferences(exec_result, [decision])
    
    # Low-confidence pattern should be removed
    prefs = memory.load_preferences()
    assert ".xyz" not in prefs["extension_destinations"]


def test_multiple_approvals_same_extension(db_session):
    """Test learning consistency with multiple files of same type."""
    memory = PreferenceMemory(db_session)
    
    # Approve multiple PDF moves to same destination
    for i in range(3):
        decision = UserDecision(
            task_id=f"test_{i}",
            timestamp=datetime.now(),
            action_type=ActionType.MOVE,
            source_path=f"/tmp/report{i}.pdf",
            destination_path=f"/home/Documents/PDFs/report{i}.pdf",
            decision="approved"
        )
        
        exec_result = ExecutionResult(
            task_id=f"test_{i}",
            total_actions=1,
            successful_actions=1,
            failed_actions=0,
            execution_logs=[]
        )
        
        memory.update_preferences(exec_result, [decision])
    
    prefs = memory.load_preferences()
    pdf_pref = prefs["extension_destinations"][".pdf"]
    
    assert pdf_pref["destination"] == "/home/Documents/PDFs"
    assert pdf_pref["count"] == 3
    assert pdf_pref["confidence"] > 0.7


def test_confidence_calculation(db_session):
    """Test Bayesian confidence calculation."""
    memory = PreferenceMemory(db_session)
    
    # Test formula: (approvals + 1) / (total + 2)
    # With 3 approvals out of 3 occurrences
    confidence = memory._calculate_confidence(3, 3)
    expected = (3 + 1) / (3 + 2)  # 4/5 = 0.8
    assert abs(confidence - expected) < 0.01


def test_learn_from_modified_decision(db_session):
    """Test learning when user modifies suggested destination."""
    memory = PreferenceMemory(db_session)
    
    decision = UserDecision(
        task_id="test",
        timestamp=datetime.now(),
        action_type=ActionType.MOVE,
        source_path="/tmp/code.py",
        destination_path="/home/Projects/code.py",
        decision="modified",
        original_suggestion="/home/Downloads/code.py"
    )
    
    exec_result = ExecutionResult(
        task_id="test",
        total_actions=1,
        successful_actions=1,
        failed_actions=0,
        execution_logs=[]
    )
    
    memory.update_preferences(exec_result, [decision])
    
    # Should learn user's preferred destination
    prefs = memory.load_preferences()
    assert ".py" in prefs["extension_destinations"]
    assert prefs["extension_destinations"][".py"]["destination"] == "/home/Projects"
