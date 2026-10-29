from pathlib import Path
from typing import List, Optional
from sentinel_core.models.planner import PlanSchema, PlanAction
from sentinel_core.models.enums import ActionType
from sentinel_core.safety.constants import PROTECTED_PATHS


class SafetyValidationResult:
    def __init__(self, is_safe: bool, issues: List[str]):
        self.issues = issues
        self.errors = list(issues)
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

        roots = [Path(p).resolve() for p in plan.authorized_roots] or [scope_root]
        if any(not p.is_dir() for p in roots):
            issues.append("Authorized roots must be existing directories")

        # 1. Scope Root Validation
        if not scope_root.is_dir():
            issues.append(f"Scope root does not exist: {scope_root}")

        # 2. Check Folders Creation
        for folder in plan.folders_to_create:
            f_path = Path(folder).resolve()
            # Must be within scope
            if not any(self._is_subpath(f_path, root) for root in roots):
                issues.append(f"Folder creation outside scope: {f_path}")
            # Must not be system path
            if self._is_protected(f_path):
                issues.append(f"Cannot create folder in protected path: {f_path}")

        # 3. Check Actions
        for action in plan.actions:
            action_issues = self._validate_action(action, scope_root, roots)
            issues.extend(action_issues)

        return SafetyValidationResult(is_safe=len(issues) == 0, issues=issues)

    def _validate_action(self, action: PlanAction, scope_root: Path, roots=None) -> List[str]:
        issues = []
        roots = roots or [scope_root]
        source_path = Path(action.source_path).resolve() if action.source_path else None
        dest_path = Path(action.destination_path).resolve() if action.destination_path else None

        # Check Source
        if (
            action.type in (ActionType.MOVE, ActionType.RENAME, ActionType.DELETE)
            and not source_path
        ):
            issues.append("Source path is required")
        if (
            action.type in (ActionType.MOVE, ActionType.RENAME, ActionType.CREATE_FOLDER)
            and not dest_path
        ):
            issues.append("Destination path is required")
        if source_path:
            if source_path == scope_root or not source_path.is_file():
                issues.append(f"Source must be a regular file below scope: {source_path}")
            if not any(self._is_subpath(source_path, root) for root in roots):
                issues.append(f"Action source outside scope: {source_path}")
            if self._is_protected(source_path):
                issues.append(f"Cannot touch protected source: {source_path}")
            if not source_path.exists():
                issues.append(f"Source file does not exist: {source_path}")

        # Check Destination
        if dest_path:
            if action.type in (ActionType.MOVE, ActionType.RENAME) and dest_path.exists():
                issues.append(f"Destination already exists: {dest_path}")
            if not any(self._is_subpath(dest_path, root) for root in roots):
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
