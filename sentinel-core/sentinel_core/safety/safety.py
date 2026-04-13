from pathlib import Path
from typing import List, Optional
from sentinel_core.models.planner import PlanSchema, PlanAction
from sentinel_core.models.enums import ActionType
from sentinel_core.safety.constants import PROTECTED_PATHS

_LARGE_DELETE_THRESHOLD = 100  # Warn if plan contains this many deletes


class SafetyValidationResult:
    def __init__(self, is_safe: bool, issues: List[str]):
        self.issues = issues
        self.errors = [issue for issue in issues if issue.startswith("[ERROR]")]
        self.warnings = [issue for issue in issues if issue.startswith("[WARN]")]
        # is_safe based on errors only — warnings are non-blocking
        self.is_safe = len(self.errors) == 0

    def __repr__(self):
        return f"SafetyValidationResult(is_safe={self.is_safe}, errors={self.errors}, warnings={self.warnings})"


class SafetyValidator:
    def validate_plan(self, plan: PlanSchema) -> SafetyValidationResult:
        """
        Validates the compliance of a plan with safety rules.

        Issues are prefixed:
          [ERROR] — plan is rejected if any errors exist
          [WARN]  — plan is safe, but user should review
        """
        issues: List[str] = []

        # --- Scope validation (only when scope_path is provided) ---
        use_scope = bool(plan.scope_path)
        scope_root = Path(plan.scope_path).resolve() if use_scope else None

        if use_scope and scope_root and not scope_root.exists():
            issues.append(f"[ERROR] Scope root does not exist: {scope_root}")

        # --- Folder creation validation ---
        for folder in plan.folders_to_create:
            f_path = Path(folder).resolve()
            if use_scope and scope_root and not self._is_subpath(f_path, scope_root):
                issues.append(f"[ERROR] Folder creation outside scope: {f_path}")
            if self._is_protected(f_path):
                issues.append(f"[ERROR] Cannot create folder in protected path: {f_path}")

        # --- Action validation ---
        delete_count = sum(1 for a in plan.actions if a.type == ActionType.DELETE)
        if delete_count >= _LARGE_DELETE_THRESHOLD:
            issues.append(
                f"[WARN] Plan contains {delete_count} delete operations — please review carefully."
            )

        for action in plan.actions:
            action_issues = self._validate_action(action, scope_root if use_scope else None)
            issues.extend(action_issues)

        return SafetyValidationResult(is_safe=len(issues) == 0, issues=issues)

    def _validate_action(self, action: PlanAction, scope_root: Optional[Path]) -> List[str]:
        issues: List[str] = []
        source_path = Path(action.source_path).resolve() if action.source_path else None
        dest_path = Path(action.destination_path).resolve() if action.destination_path else None

        # MOVE / COPY / RENAME must have a destination
        if action.type in (ActionType.MOVE, ActionType.RENAME, ActionType.COPY) and not dest_path:
            issues.append(
                f"[ERROR] Cannot execute {action.type.value} without a destination path."
            )

        # Check Source
        if source_path:
            if scope_root and not self._is_subpath(source_path, scope_root):
                issues.append(f"[ERROR] Action source outside scope: {source_path}")
            if self._is_protected(source_path):
                issues.append(f"[ERROR] Cannot touch protected source: {source_path}")

        # Check Destination
        if dest_path:
            if scope_root and not self._is_subpath(dest_path, scope_root):
                issues.append(f"[ERROR] Action destination outside scope: {dest_path}")
            if self._is_protected(dest_path):
                issues.append(f"[ERROR] Cannot write to protected destination: {dest_path}")

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
            try:
                if path == protected or protected in path.parents:
                    return True
            except Exception:
                continue
        return False
