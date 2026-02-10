"""
Tests for the database management module.

Verifies database initialization, backup, and restore functionality.
"""

import pytest
import tempfile
import os
import json
from datetime import datetime
from sqlmodel import create_engine, Session, SQLModel, select

from sentinel_core.models import PreferencePattern, UserDecision, ActionType
from sentinel_core.memory.db import (
    get_engine,
    create_tables,
    backup_to_json,
    restore_from_json,
    initialize_database,
    reset_preferences
)


def test_get_engine_creates_default_path():
    """Test that get_engine creates database at default path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        engine = get_engine(db_path)
        
        assert engine is not None
        # Create tables to force file creation
        create_tables(engine)
        # Verify file was created
        assert os.path.exists(db_path)


def test_create_tables():
    """Test table creation."""
    engine = create_engine("sqlite:///:memory:")
    create_tables(engine)
    
    # Verify tables exist by trying to query them
    with Session(engine) as session:
        # These should not raise errors
        session.exec(select(PreferencePattern)).all()
        session.exec(select(UserDecision)).all()


def test_initialize_database():
    """Test database initialization helper."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "init_test.db")
        engine = initialize_database(db_path)
        
        assert engine is not None
        assert os.path.exists(db_path)
        
        # Verify tables exist
        with Session(engine) as session:
            session.exec(select(PreferencePattern)).all()


def test_backup_to_json():
    """Test exporting preferences to JSON."""
    engine = create_engine("sqlite:///:memory:")
    create_tables(engine)
    
    # Add some test data
    with Session(engine) as session:
        pattern = PreferencePattern(
            pattern_type="file_extension_destination",
            source_pattern=".pdf",
            destination_pattern="/home/Documents/PDFs",
            confidence=0.95,
            occurrence_count=20,
            approval_count=19,
            last_seen=datetime.now(),
            created_at=datetime.now()
        )
        session.add(pattern)
        session.commit()
    
    # Backup to JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        backup_path = f.name
    
    try:
        backup_to_json(engine, backup_path)
        
        # Verify JSON was created
        assert os.path.exists(backup_path)
        
        # Verify JSON content
        with open(backup_path, 'r') as f:
            data = json.load(f)
        
        assert data["version"] == "1.0"
        assert "exported_at" in data
        assert len(data["patterns"]) == 1
        assert data["patterns"][0]["source_pattern"] == ".pdf"
        assert data["patterns"][0]["confidence"] == 0.95
    
    finally:
        if os.path.exists(backup_path):
            os.remove(backup_path)


def test_restore_from_json():
    """Test importing preferences from JSON."""
    engine = create_engine("sqlite:///:memory:")
    create_tables(engine)
    
    # Create backup JSON
    backup_data = {
        "version": "1.0",
        "exported_at": datetime.now().isoformat(),
        "patterns": [
            {
                "pattern_type": "file_extension_destination",
                "source_pattern": ".jpg",
                "destination_pattern": "/home/Photos",
                "confidence": 0.85,
                "occurrence_count": 10,
                "approval_count": 8,
                "last_seen": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat()
            }
        ],
        "preferences": {},
        "recent_decisions": []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(backup_data, f)
        backup_path = f.name
    
    try:
        # Restore from JSON
        restore_from_json(engine, backup_path)
        
        # Verify data was imported
        with Session(engine) as session:
            patterns = session.exec(select(PreferencePattern)).all()
            assert len(patterns) == 1
            assert patterns[0].source_pattern == ".jpg"
            assert patterns[0].confidence == 0.85
    
    finally:
        if os.path.exists(backup_path):
            os.remove(backup_path)


def test_restore_from_json_file_not_found():
    """Test restore raises error for missing file."""
    engine = create_engine("sqlite:///:memory:")
    
    with pytest.raises(FileNotFoundError):
        restore_from_json(engine, "/nonexistent/file.json")


def test_restore_from_json_invalid_version():
    """Test restore raises error for invalid version."""
    engine = create_engine("sqlite:///:memory:")
    create_tables(engine)
    
    # Create backup with invalid version
    backup_data = {
        "version": "99.0",
        "patterns": []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(backup_data, f)
        backup_path = f.name
    
    try:
        with pytest.raises(ValueError, match="Unsupported backup version"):
            restore_from_json(engine, backup_path)
    
    finally:
        if os.path.exists(backup_path):
            os.remove(backup_path)


def test_backup_and_restore_roundtrip():
    """Test that backup and restore preserves data."""
    engine = create_engine("sqlite:///:memory:")
    create_tables(engine)
    
    # Add test data
    with Session(engine) as session:
        pattern1 = PreferencePattern(
            pattern_type="file_extension_destination",
            source_pattern=".pdf",
            destination_pattern="/home/PDFs",
            confidence=0.9,
            occurrence_count=15,
            approval_count=14
        )
        
        pattern2 = PreferencePattern(
            pattern_type="delete_approval",
            source_pattern=".tmp",
            destination_pattern=None,
            confidence=0.95,
            occurrence_count=20,
            approval_count=19
        )
        
        session.add(pattern1)
        session.add(pattern2)
        session.commit()
    
    # Backup
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        backup_path = f.name
    
    try:
        backup_to_json(engine, backup_path)
        
        # Create new database
        engine2 = create_engine("sqlite:///:memory:")
        create_tables(engine2)
        
        # Restore to new database
        restore_from_json(engine2, backup_path)
        
        # Verify data matches
        with Session(engine2) as session:
            patterns = session.exec(select(PreferencePattern)).all()
            assert len(patterns) == 2
            
            pdf_pattern = next(p for p in patterns if p.source_pattern == ".pdf")
            assert pdf_pattern.destination_pattern == "/home/PDFs"
            assert pdf_pattern.confidence == 0.9
            assert pdf_pattern.approval_count == 14
            
            tmp_pattern = next(p for p in patterns if p.source_pattern == ".tmp")
            assert tmp_pattern.destination_pattern is None
            assert tmp_pattern.confidence == 0.95
    
    finally:
        if os.path.exists(backup_path):
            os.remove(backup_path)


def test_reset_preferences():
    """Test resetting all preferences."""
    engine = create_engine("sqlite:///:memory:")
    create_tables(engine)
    
    # Add test data
    with Session(engine) as session:
        pattern = PreferencePattern(
            pattern_type="file_extension_destination",
            source_pattern=".pdf",
            destination_pattern="/home/PDFs",
            confidence=0.9,
            occurrence_count=10,
            approval_count=9
        )
        
        decision = UserDecision(
            task_id="test",
            timestamp=datetime.now(),
            action_type=ActionType.MOVE,
            source_path="/tmp/file.pdf",
            destination_path="/home/PDFs/file.pdf",
            decision="approved"
        )
        
        session.add(pattern)
        session.add(decision)
        session.commit()
    
    # Verify data exists
    with Session(engine) as session:
        assert len(session.exec(select(PreferencePattern)).all()) == 1
        assert len(session.exec(select(UserDecision)).all()) == 1
    
    # Reset
    reset_preferences(engine)
    
    # Verify data was deleted
    with Session(engine) as session:
        assert len(session.exec(select(PreferencePattern)).all()) == 0
        assert len(session.exec(select(UserDecision)).all()) == 0


def test_restore_updates_existing_pattern():
    """Test that restore updates existing patterns instead of duplicating."""
    engine = create_engine("sqlite:///:memory:")
    create_tables(engine)
    
    # Add original pattern
    with Session(engine) as session:
        pattern = PreferencePattern(
            pattern_type="file_extension_destination",
            source_pattern=".pdf",
            destination_pattern="/home/Downloads",
            confidence=0.5,
            occurrence_count=5,
            approval_count=2
        )
        session.add(pattern)
        session.commit()
    
    # Create backup with updated confidence
    backup_data = {
        "version": "1.0",
        "exported_at": datetime.now().isoformat(),
        "patterns": [
            {
                "pattern_type": "file_extension_destination",
                "source_pattern": ".pdf",
                "destination_pattern": "/home/Documents/PDFs",
                "confidence": 0.95,
                "occurrence_count": 20,
                "approval_count": 19,
                "last_seen": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat()
            }
        ],
        "preferences": {},
        "recent_decisions": []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(backup_data, f)
        backup_path = f.name
    
    try:
        restore_from_json(engine, backup_path)
        
        # Should have only one pattern (updated, not duplicated)
        with Session(engine) as session:
            patterns = session.exec(select(PreferencePattern)).all()
            assert len(patterns) == 1
            assert patterns[0].destination_pattern == "/home/Documents/PDFs"
            assert patterns[0].confidence == 0.95
    
    finally:
        if os.path.exists(backup_path):
            os.remove(backup_path)
