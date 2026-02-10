"""
Organization Rules

Deterministic rules for file organization based on classifications.
"""

from typing import List, Callable
from dataclasses import dataclass

from sentinel_core.cleanpc.classifiers import FileClassification
from sentinel_core.rules.models import RuleMatchResult


@dataclass
class OrganizationRule:
    """
    A rule for organizing files.
    
    Attributes:
        name: Human-readable rule name
        priority: Rule priority (lower = higher priority)
        condition: Function to check if rule applies
        category: Category for matched files
        confidence: Confidence score (0.0-1.0)
    """
    name: str
    priority: int
    condition: Callable[[FileClassification], bool]
    category: str
    confidence: float = 1.0


class OrganizationRules:
    """
    Applies organization rules to classified files.
    """
    
    def __init__(self):
        """Initialize with predefined rules."""
        self.rules = self._define_rules()
    
    def _define_rules(self) -> List[OrganizationRule]:
        """
        Define the organization rules.
        
        Rules are ordered by priority. First matching rule wins.
        
        Returns:
            List of organization rules
        """
        return [
            OrganizationRule(
                name="Screenshots to Pictures",
                priority=1,
                condition=lambda c: c.is_screenshot,
                category="screenshot",
                confidence=0.95
            ),
            OrganizationRule(
                name="Large Videos to Videos Folder",
                priority=2,
                condition=lambda c: c.is_large_video,
                category="video",
                confidence=0.90
            ),
            OrganizationRule(
                name="Remove Old Installers",
                priority=3,
                condition=lambda c: c.is_installer,
                category="installer",
                confidence=0.85
            ),
            OrganizationRule(
                name="Archive Old Archives",
                priority=4,
                condition=lambda c: c.is_archive,
                category="archive",
                confidence=0.90
            ),
            OrganizationRule(
                name="Remove Duplicate Files",
                priority=5,
                condition=lambda c: c.is_duplicate,
                category="duplicate",
                confidence=0.95
            ),
        ]
    
    def apply_rules(
        self, 
        classifications: List[FileClassification]
    ) -> List[RuleMatchResult]:
        """
        Apply all rules to classifications.
        
        For each classification, find the first matching rule and create
        a RuleMatchResult.
        
        Args:
            classifications: List of file classifications
            
        Returns:
            List of rule match results
        """
        matches = []
        
        for classification in classifications:
            # Try each rule in priority order
            for rule in sorted(self.rules, key=lambda r: r.priority):
                if rule.condition(classification):
                    # Generate reason based on classification
                    reason = self._generate_reason(classification, rule)
                    
                    match = RuleMatchResult(
                        file_path=classification.file.path,
                        matched_rule=rule.name,
                        suggested_category=rule.category,
                        confidence=rule.confidence,
                        reason=reason
                    )
                    matches.append(match)
                    break  # First match wins
        
        return matches
    
    def _generate_reason(
        self, 
        classification: FileClassification, 
        rule: OrganizationRule
    ) -> str:
        """
        Generate a human-readable reason for the match.
        
        Args:
            classification: File classification
            rule: Matched rule
            
        Returns:
            Human-readable reason string
        """
        if classification.is_installer:
            return (
                f"Old installer ({classification.age_days} days old) "
                f"from Downloads/Desktop - safe to remove"
            )
        
        if classification.is_archive:
            if classification.suggested_action == "delete":
                return (
                    f"Archive file ({classification.age_days} days old) "
                    f"in Downloads - likely no longer needed"
                )
            return (
                f"Archive file should be moved to Archives/{classification.file.modified_at.year}/"
            )
        
        if classification.is_large_video:
            return (
                f"Large video file ({classification.video_size_mb}MB) "
                f"should be organized in Videos folder"
            )
        
        if classification.is_screenshot:
            return (
                f"Screenshot detected - organize in Pictures/Screenshots/{classification.file.created_at.year}/"
            )
        
        if classification.is_duplicate:
            return (
                f"Duplicate file (same as {Path(classification.duplicate_of).name}) "
                f"- keeping newest copy"
            )
        
        return f"Matched rule: {rule.name}"


# Import Path for reason generation
from pathlib import Path
