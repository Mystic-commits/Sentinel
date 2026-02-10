"""
Preference Memory Module

Learns from user decisions and provides intelligent suggestions
based on historical patterns.
"""

import os
import fnmatch
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path
from sqlmodel import Session, select

from sentinel_core.models.preferences import PreferencePattern, UserDecision
from sentinel_core.models.executor import ExecutionResult
from sentinel_core.models.enums import ActionType
from sentinel_core.memory.db import get_engine, get_session, create_tables


class PreferenceMemory:
    """
    Manages preference learning and retrieval.
    
    Learns patterns from user decisions and provides suggestions
    for future file operations based on historical approval rates.
    
    Attributes:
        session: SQLModel database session
    """
    
    def __init__(self, session: Session):
        """
        Initialize PreferenceMemory with a database session.
        
        Args:
            session: SQLModel Session for database operations
        """
        self.session = session
    
    def load_preferences(self) -> Dict[str, Any]:
        """
        Load all learned preferences.
        
        Returns:
            Dictionary containing:
            - extension_destinations: Map of file extensions to preferred folders
            - folder_patterns: Learned folder organization patterns  
            - delete_preferences: Which file types are safe to delete
            - confidence_scores: Confidence for each pattern
            
        Example:
            >>> memory = PreferenceMemory(session)
            >>> prefs = memory.load_preferences()
            >>> print(prefs['extension_destinations'].get('.pdf'))
            {'destination': 'Documents/PDFs', 'confidence': 0.95}
        """
        # Query all high-confidence patterns
        patterns_stmt = select(PreferencePattern).where(
            PreferencePattern.confidence >= 0.5
        ).order_by(PreferencePattern.confidence.desc())
        
        patterns = self.session.exec(patterns_stmt).all()
        
        # Organize by type
        extension_destinations: Dict[str, Dict[str, Any]] = {}
        folder_patterns: List[Dict[str, Any]] = []
        delete_preferences: Dict[str, Dict[str, Any]] = {}
        
        for pattern in patterns:
            if pattern.pattern_type == "file_extension_destination":
                extension_destinations[pattern.source_pattern] = {
                    "destination": pattern.destination_pattern,
                    "confidence": pattern.confidence,
                    "count": pattern.approval_count
                }
            elif pattern.pattern_type == "delete_approval":
                delete_preferences[pattern.source_pattern] = {
                    "should_delete": True,
                    "confidence": pattern.confidence,
                    "count": pattern.approval_count
                }
            elif pattern.pattern_type == "folder_structure":
                folder_patterns.append({
                    "source_pattern": pattern.source_pattern,
                    "destination": pattern.destination_pattern,
                    "confidence": pattern.confidence
                })
        
        return {
            "extension_destinations": extension_destinations,
            "folder_patterns": folder_patterns,
            "delete_preferences": delete_preferences
        }
    
    def update_preferences(
        self,
        execution_result: ExecutionResult,
        user_decisions: List[UserDecision]
    ) -> None:
        """
        Learn from execution results and user decisions.
        
        Analyzes user decisions to:
        - Increase confidence for approved patterns
        - Decrease confidence for rejected patterns
        - Learn new patterns from modifications
        - Prune low-confidence patterns
        
        Args:
            execution_result: Result from executor
            user_decisions: List of user approval/rejection decisions
            
        Example:
            >>> memory = PreferenceMemory(session)
            >>> decisions = [UserDecision(..., decision="approved")]
            >>> memory.update_preferences(result, decisions)
        """
        for decision in user_decisions:
            # Extract pattern from decision
            if decision.action_type in (ActionType.MOVE, ActionType.RENAME):
                if decision.destination_path:
                    self._learn_destination_pattern(decision)
            
            elif decision.action_type == ActionType.DELETE:
                self._learn_delete_pattern(decision)
        
        # Prune low-confidence patterns
        self._prune_low_confidence_patterns()
        
        self.session.commit()
    
    def suggest_destination(self, file_path: str) -> Optional[Tuple[str, float]]:
        """
        Suggest destination for a file based on learned patterns.
        
        Args:
            file_path: Path to file
            
        Returns:
            (suggested_path: str, confidence: float) or None if no pattern matches
            
        Example:
            >>> memory = PreferenceMemory(session)
            >>> suggestion, confidence = memory.suggest_destination("report.pdf")
            >>> print(f"{suggestion} (confidence: {confidence})")
            Documents/PDFs (confidence: 0.95)
        """
        # Get file extension
        ext = Path(file_path).suffix.lower()
        
        if not ext:
            return None
        
        # Query patterns for this extension
        pattern_stmt = select(PreferencePattern).where(
            PreferencePattern.pattern_type == "file_extension_destination",
            PreferencePattern.source_pattern == ext,
            PreferencePattern.confidence >= 0.5
        ).order_by(PreferencePattern.confidence.desc())
        
        pattern = self.session.exec(pattern_stmt).first()
        
        if pattern and pattern.destination_pattern:
            return (pattern.destination_pattern, pattern.confidence)
        
        # Try name patterns
        filename = Path(file_path).name
        name_patterns_stmt = select(PreferencePattern).where(
            PreferencePattern.pattern_type == "folder_structure",
            PreferencePattern.confidence >= 0.5
        ).order_by(PreferencePattern.confidence.desc())
        
        name_patterns = self.session.exec(name_patterns_stmt).all()
        
        for pattern in name_patterns:
            if fnmatch.fnmatch(filename, pattern.source_pattern):
                if pattern.destination_pattern:
                    return (pattern.destination_pattern, pattern.confidence)
        
        return None
    
    def should_delete(self, file_path: str) -> Tuple[bool, float]:
        """
        Check if file type is safe to delete based on past approvals.
        
        Args:
            file_path: Path to file
            
        Returns:
            (should_delete: bool, confidence: float)
            
        Example:
            >>> memory = PreferenceMemory(session)
            >>> should_delete, confidence = memory.should_delete("temp.tmp")
            >>> if should_delete and confidence > 0.8:
            ...     print("Safe to delete")
        """
        # Get file extension
        ext = Path(file_path).suffix.lower()
        
        if not ext:
            return (False, 0.0)
        
        # Query delete patterns
        pattern_stmt = select(PreferencePattern).where(
            PreferencePattern.pattern_type == "delete_approval",
            PreferencePattern.source_pattern == ext
        )
        
        pattern = self.session.exec(pattern_stmt).first()
        
        if pattern:
            should_delete = pattern.confidence >= 0.7
            return (should_delete, pattern.confidence)
        
        return (False, 0.0)
    
    def _learn_destination_pattern(self, decision: UserDecision) -> None:
        """
        Learn from a move/rename decision.
        
        Extracts file extension and destination folder to create
        or update a pattern.
        
        Args:
            decision: UserDecision record
        """
        # Extract extension
        ext = Path(decision.source_path).suffix.lower()
        
        if not ext or not decision.destination_path:
            return
        
        # Extract destination folder (remove filename)
        dest_folder = os.path.dirname(decision.destination_path)
        
        if not dest_folder:
            return
        
        # Find or create pattern
        pattern_stmt = select(PreferencePattern).where(
            PreferencePattern.pattern_type == "file_extension_destination",
            PreferencePattern.source_pattern == ext
        )
        
        pattern = self.session.exec(pattern_stmt).first()
        
        if pattern:
            # Update existing pattern
            pattern.occurrence_count += 1
            pattern.last_seen = datetime.now()
            
            if decision.decision == "approved":
                # Check if destination matches
                if pattern.destination_pattern == dest_folder:
                    pattern.approval_count += 1
                else:
                    # User chose different destination
                    # If this is consistent, update the pattern
                    if pattern.approval_count == 0:
                        # No approvals yet, update destination
                        pattern.destination_pattern = dest_folder
                        pattern.approval_count = 1
                    # Otherwise, this might be a rejection of the pattern
            
            elif decision.decision == "rejected":
                # Decrease confidence but don't increment approval
                pass
            
            elif decision.decision == "modified":
                # User modified suggestion - learn new destination
                if decision.original_suggestion != dest_folder:
                    pattern.destination_pattern = dest_folder
                    pattern.approval_count += 1
            
            # Update confidence using Bayesian formula
            pattern.confidence = self._calculate_confidence(
                pattern.approval_count,
                pattern.occurrence_count
            )
        
        else:
            # Create new pattern if approved or modified
            if decision.decision in ("approved", "modified"):
                pattern = PreferencePattern(
                    pattern_type="file_extension_destination",
                    source_pattern=ext,
                    destination_pattern=dest_folder,
                    confidence=self._calculate_confidence(1, 1),
                    occurrence_count=1,
                    approval_count=1,
                    last_seen=datetime.now(),
                    created_at=datetime.now()
                )
                self.session.add(pattern)
    
    def _learn_delete_pattern(self, decision: UserDecision) -> None:
        """
        Learn from a delete decision.
        
        Tracks which file types user approves for deletion.
        
        Args:
            decision: UserDecision record
        """
        # Extract extension
        ext = Path(decision.source_path).suffix.lower()
        
        if not ext:
            return
        
        # Find or create pattern
        pattern_stmt = select(PreferencePattern).where(
            PreferencePattern.pattern_type == "delete_approval",
            PreferencePattern.source_pattern == ext
        )
        
        pattern = self.session.exec(pattern_stmt).first()
        
        if pattern:
            pattern.occurrence_count += 1
            pattern.last_seen = datetime.now()
            
            if decision.decision == "approved":
                pattern.approval_count += 1
            
            # Update confidence
            pattern.confidence = self._calculate_confidence(
                pattern.approval_count,
                pattern.occurrence_count
            )
        
        else:
            # Create new pattern
            if decision.decision == "approved":
                pattern = PreferencePattern(
                    pattern_type="delete_approval",
                    source_pattern=ext,
                    destination_pattern=None,
                    confidence=self._calculate_confidence(1, 1),
                    occurrence_count=1,
                    approval_count=1,
                    last_seen=datetime.now(),
                    created_at=datetime.now()
                )
                self.session.add(pattern)
    
    def _calculate_confidence(self, approvals: int, total: int) -> float:
        """
        Calculate confidence score using Bayesian updating with Laplace smoothing.
        
        Formula: (approvals + α) / (total + β)
        Where α=1, β=2 (prior smoothing to avoid extreme values)
        
        Args:
            approvals: Number of approvals
            total: Total number of occurrences
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        alpha = 1.0  # Prior approvals
        beta = 2.0   # Prior total
        
        return (approvals + alpha) / (total + beta)
    
    def _prune_low_confidence_patterns(self) -> None:
        """
        Remove patterns with low confidence and few occurrences.
        
        Removes patterns where:
        - Confidence < 0.3 AND occurrence_count < 3
        
        This prevents accumulation of unreliable patterns.
        """
        # Query low-confidence patterns
        patterns_stmt = select(PreferencePattern).where(
            PreferencePattern.confidence < 0.3,
            PreferencePattern.occurrence_count < 3
        )
        
        patterns = self.session.exec(patterns_stmt).all()
        
        for pattern in patterns:
            self.session.delete(pattern)


# Public API functions

def load_preferences(db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load user preferences from database.
    
    Args:
        db_path: Optional path to database file
        
    Returns:
        Dictionary of learned preferences
        
    Example:
        >>> prefs = load_preferences()
        >>> print(prefs['extension_destinations'].get('.pdf'))
        {'destination': 'Documents/PDFs', 'confidence': 0.95}
    """
    engine = get_engine(db_path)
    create_tables(engine)
    
    with get_session(engine) as session:
        memory = PreferenceMemory(session)
        return memory.load_preferences()


def update_preferences(
    execution_result: ExecutionResult,
    user_decisions: List[UserDecision],
    db_path: Optional[str] = None
) -> None:
    """
    Update preferences based on user decisions.
    
    Args:
        execution_result: Result from executor
        user_decisions: List of user approval/rejection decisions
        db_path: Optional path to database file
        
    Example:
        >>> decisions = [
        ...     UserDecision(
        ...         task_id="task_123",
        ...         action_type=ActionType.MOVE,
        ...         source_path="/tmp/file.pdf",
        ...         destination_path="/tmp/PDFs/file.pdf",
        ...         decision="approved"
        ...     )
        ... ]
        >>> update_preferences(result, decisions)
    """
    engine = get_engine(db_path)
    create_tables(engine)
    
    with get_session(engine) as session:
        memory = PreferenceMemory(session)
        memory.update_preferences(execution_result, user_decisions)


def reset_preferences(db_path: Optional[str] = None) -> None:
    """
    Reset all learned preferences.
    
    WARNING: This deletes all learned patterns.
    
    Args:
        db_path: Optional path to database file
    """
    from sentinel_core.memory.db import reset_preferences as db_reset_preferences
    
    engine = get_engine(db_path)
    db_reset_preferences(engine)


def export_preferences(export_path: str, db_path: Optional[str] = None) -> None:
    """
    Export preferences to JSON file.
    
    Args:
        export_path: Path to export file
        db_path: Optional path to database file
    """
    from sentinel_core.memory.db import backup_to_json
    
    engine = get_engine(db_path)
    backup_to_json(engine, export_path)


def import_preferences(import_path: str, db_path: Optional[str] = None) -> None:
    """
    Import preferences from JSON file.
    
    Args:
        import_path: Path to import file
        db_path: Optional path to database file
    """
    from sentinel_core.memory.db import restore_from_json
    
    engine = get_engine(db_path)
    restore_from_json(engine, import_path)
