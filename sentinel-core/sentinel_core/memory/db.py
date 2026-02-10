"""
Database Management Module

Handles database connection, table creation, and JSON backup/restore
for the preference memory system.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlmodel import create_engine, Session, SQLModel, select

from sentinel_core.models.preferences import (
    Preferences,
    PreferencePattern,
    UserDecision
)


# Default database path
DEFAULT_DB_PATH = os.path.expanduser("~/.sentinel/sentinel.db")
DEFAULT_BACKUP_PATH = os.path.expanduser("~/.sentinel/preferences_backup.json")


def get_engine(db_path: Optional[str] = None):
    """
    Get or create database engine.
    
    Creates the database directory if it doesn't exist.
    
    Args:
        db_path: Path to database file. If None, uses default (~/.sentinel/sentinel.db)
        
    Returns:
        SQLModel Engine instance
        
    Example:
        >>> engine = get_engine()
        >>> # Or custom path:
        >>> engine = get_engine("/custom/path/sentinel.db")
    """
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    
    # Expand user home directory
    db_path = os.path.expanduser(db_path)
    
    # Create directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    
    # Create engine with connection string
    connection_string = f"sqlite:///{db_path}"
    engine = create_engine(connection_string, echo=False)
    
    return engine


def create_tables(engine) -> None:
    """
    Create all tables if they don't exist.
    
    Creates tables for:
    - Preferences
    - PreferencePattern
    - UserDecision
    - ExecutionLogEntry
    - TaskRecord
    
    Args:
        engine: SQLModel Engine instance
        
    Example:
        >>> engine = get_engine()
        >>> create_tables(engine)
    """
    # Import all models to ensure they're registered
    from sentinel_core.models import (
        ExecutionLogEntry,
        TaskRecord,
        Preferences,
        PreferencePattern,
        UserDecision
    )
    
    # Create all tables
    SQLModel.metadata.create_all(engine)


def backup_to_json(engine, backup_path: Optional[str] = None) -> None:
    """
    Export preferences to JSON file.
    
    Creates a human-readable backup of all preference patterns
    and user preferences. This backup can be manually edited and
    imported on another machine.
    
    Args:
        engine: SQLModel Engine instance
        backup_path: Path to backup file. If None, uses default
        
    Example:
        >>> engine = get_engine()
        >>> backup_to_json(engine, "/backups/preferences.json")
    """
    if backup_path is None:
        backup_path = DEFAULT_BACKUP_PATH
    
    backup_path = os.path.expanduser(backup_path)
    
    # Create backup directory if needed
    backup_dir = os.path.dirname(backup_path)
    if backup_dir:
        os.makedirs(backup_dir, exist_ok=True)
    
    with Session(engine) as session:
        # Export preference patterns
        patterns_stmt = select(PreferencePattern)
        patterns = session.exec(patterns_stmt).all()
        
        patterns_data = [
            {
                "pattern_type": p.pattern_type,
                "source_pattern": p.source_pattern,
                "destination_pattern": p.destination_pattern,
                "confidence": p.confidence,
                "occurrence_count": p.occurrence_count,
                "approval_count": p.approval_count,
                "last_seen": p.last_seen.isoformat(),
                "created_at": p.created_at.isoformat()
            }
            for p in patterns
        ]
        
        # Export general preferences
        prefs_stmt = select(Preferences)
        prefs = session.exec(prefs_stmt).all()
        
        prefs_data = {
            p.key: json.loads(p.value) if p.value.startswith('{') or p.value.startswith('[') else p.value
            for p in prefs
        }
        
        # Export user decisions (last 1000 for reference)
        decisions_stmt = select(UserDecision).order_by(
            UserDecision.timestamp.desc()
        ).limit(1000)
        decisions = session.exec(decisions_stmt).all()
        
        decisions_data = [
            {
                "task_id": d.task_id,
                "timestamp": d.timestamp.isoformat(),
                "action_type": d.action_type.value,
                "source_path": d.source_path,
                "destination_path": d.destination_path,
                "decision": d.decision,
                "original_suggestion": d.original_suggestion,
                "reason_code": d.reason_code
            }
            for d in decisions
        ]
        
        # Create backup structure
        backup_data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "patterns": patterns_data,
            "preferences": prefs_data,
            "recent_decisions": decisions_data
        }
        
        # Write to file
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)


def restore_from_json(engine, backup_path: Optional[str] = None) -> None:
    """
    Import preferences from JSON file.
    
    Restores preference patterns and preferences from a backup file.
    This does NOT restore user decisions to avoid duplication.
    
    Args:
        engine: SQLModel Engine instance
        backup_path: Path to backup file. If None, uses default
        
    Raises:
        FileNotFoundError: If backup file doesn't exist
        ValueError: If backup format is invalid
        
    Example:
        >>> engine = get_engine()
        >>> restore_from_json(engine, "/backups/preferences.json")
    """
    if backup_path is None:
        backup_path = DEFAULT_BACKUP_PATH
    
    backup_path = os.path.expanduser(backup_path)
    
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup file not found: {backup_path}")
    
    # Load backup data
    with open(backup_path, 'r') as f:
        backup_data = json.load(f)
    
    # Validate version
    if backup_data.get("version") != "1.0":
        raise ValueError(f"Unsupported backup version: {backup_data.get('version')}")
    
    with Session(engine) as session:
        # Restore preference patterns
        for pattern_data in backup_data.get("patterns", []):
            # Check if pattern already exists
            existing_stmt = select(PreferencePattern).where(
                PreferencePattern.pattern_type == pattern_data["pattern_type"],
                PreferencePattern.source_pattern == pattern_data["source_pattern"]
            )
            existing = session.exec(existing_stmt).first()
            
            if existing:
                # Update existing pattern
                existing.destination_pattern = pattern_data.get("destination_pattern")
                existing.confidence = pattern_data["confidence"]
                existing.occurrence_count = pattern_data["occurrence_count"]
                existing.approval_count = pattern_data["approval_count"]
                existing.last_seen = datetime.fromisoformat(pattern_data["last_seen"])
            else:
                # Create new pattern
                pattern = PreferencePattern(
                    pattern_type=pattern_data["pattern_type"],
                    source_pattern=pattern_data["source_pattern"],
                    destination_pattern=pattern_data.get("destination_pattern"),
                    confidence=pattern_data["confidence"],
                    occurrence_count=pattern_data["occurrence_count"],
                    approval_count=pattern_data["approval_count"],
                    last_seen=datetime.fromisoformat(pattern_data["last_seen"]),
                    created_at=datetime.fromisoformat(pattern_data["created_at"])
                )
                session.add(pattern)
        
        # Restore general preferences
        for key, value in backup_data.get("preferences", {}).items():
            # Check if preference exists
            existing_pref = session.get(Preferences, key)
            
            value_str = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            
            if existing_pref:
                existing_pref.value = value_str
            else:
                pref = Preferences(key=key, value=value_str)
                session.add(pref)
        
        session.commit()


def get_session(engine):
    """
    Get a database session.
    
    Use as a context manager for automatic cleanup.
    
    Args:
        engine: SQLModel Engine instance
        
    Returns:
        SQLModel Session instance
        
    Example:
        >>> engine = get_engine()
        >>> with get_session(engine) as session:
        ...     # Perform database operations
        ...     patterns = session.exec(select(PreferencePattern)).all()
    """
    return Session(engine)


def initialize_database(db_path: Optional[str] = None):
    """
    Initialize database with all tables.
    
    Convenience function that creates engine and tables in one call.
    
    Args:
        db_path: Optional path to database file
        
    Returns:
        Engine instance
        
    Example:
        >>> engine = initialize_database()
        >>> # Database is ready to use
    """
    engine = get_engine(db_path)
    create_tables(engine)
    return engine


def reset_preferences(engine) -> None:
    """
    Reset all preference patterns and user decisions.
    
    WARNING: This deletes all learned preferences. This action cannot be undone
    unless you have a backup.
    
    Args:
        engine: SQLModel Engine instance
        
    Example:
        >>> engine = get_engine()
        >>> # Create backup first
        >>> backup_to_json(engine, "/safe/backup.json")
        >>> # Then reset
        >>> reset_preferences(engine)
    """
    with Session(engine) as session:
        # Delete all preference patterns
        patterns = session.exec(select(PreferencePattern)).all()
        for pattern in patterns:
            session.delete(pattern)
        
        # Delete all user decisions
        decisions = session.exec(select(UserDecision)).all()
        for decision in decisions:
            session.delete(decision)
        
        session.commit()
