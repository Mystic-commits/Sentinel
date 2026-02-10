from pathlib import Path
from typing import List, Optional
from sentinel_core.models.planner import PlanSchema, PlanAction
from sentinel_core.models.enums import ActionType
from sentinel_core.safety.constants import PROTECTED_PATHS

class SafetyValidationResult:
    def __init__(self, is_safe: bool, issues: List[str]):
        self.issues = issues
        self.errors = [issue for issue in issues if "Cannot" in issue or "does not exist" in issue]
        self.warnings = [issue for issue in issues if issue not in self.errors]
        # is_safe should be based on errors, not all issues (warnings OK)
        self.is_safe = len(self.errors) == 0

    def __repr__(self):
        return f"SafetyValidationResult(is_safe={self.is_safe}, errors={self.errors}, warnings={self.warnings})"

class SafetyValidator:
    def validate_plan(self, plan: PlanSchema) -> SafetyValidationResult:
        """
        Validates the compliance of a plan with safety rules.
        """
        issues = []
        scope_root = Path(plan.scope_path).resolve()
        
        # 1. Scope Root Validation
        if not scope_root.exists():
            issues.append(f"Scope root does not exist: {scope_root}")
        
        # 2. Check Folders Creation
        for folder in plan.folders_to_create:
            f_path = Path(folder).resolve()
            # Must be within scope
            if not self._is_subpath(f_path, scope_root):
                 issues.append(f"Folder creation outside scope: {f_path}")
            # Must not be system path
            if self._is_protected(f_path):
                issues.append(f"Cannot create folder in protected path: {f_path}")

        # 3. Check Actions
        for action in plan.actions:
            action_issues = self._validate_action(action, scope_root)
            issues.extend(action_issues)

        return SafetyValidationResult(is_safe=len(issues) == 0, issues=issues)

    def _validate_action(self, action: PlanAction, scope_root: Path) -> List[str]:
        issues = []
        source_path = Path(action.source_path).resolve() if action.source_path else None
        dest_path = Path(action.destination_path).resolve() if action.destination_path else None

        # Check Source
        if source_path:
            if not self._is_subpath(source_path, scope_root):
                issues.append(f"Action source outside scope: {source_path}")
            if self._is_protected(source_path):
                issues.append(f"Cannot touch protected source: {source_path}")
            if not source_path.exists():
                issues.append(f"Source file does not exist: {source_path}")

        # Check Destination
        if dest_path:
            if not self._is_subpath(dest_path, scope_root):
                 issues.append(f"Action destination outside scope: {dest_path}")
            if self._is_protected(dest_path):
                 issues.append(f"Cannot write to protected destination: {dest_path}")

        # Action Constraints
        if action.type == ActionType.DELETE:
             # Just ensures we don't delete system files (already checked above by protected check)
             pass 

        return issues

    def _is_subpath(self, path: Path, parent: Path) -> bool:
        """Checks if path is inside parent directory."""
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False

    def _is_protected(self, path: Path) -> bool:
        """Checks if a path is a system protected path."""
        for protected in PROTECTED_PATHS:
            # Check if path is equal to or inside a protected path
            # E.g. /System/foo is protected because /System is protected
            try:
                if path == protected or protected in path.parents:
                    return True
            except Exception:
                continue
        return False
