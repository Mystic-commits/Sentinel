import shutil
import os
from pathlib import Path
from sentinel_core.safety.safety import SafetyValidator, SafetyValidationResult
from sentinel_core.models.planner import PlanSchema, PlanAction
from sentinel_core.models.enums import ActionType

def setup_safe_env():
    base = Path("/tmp/sentinel_test_safety")
    if base.exists():
        shutil.rmtree(base)
    base.mkdir()
    (base / "file.txt").touch()
    return base

def test_safety():
    print("Setting up env...", end="")
    scope = setup_safe_env()
    print("OK")
    
    validator = SafetyValidator()
    
    # 1. Safe Plan
    print("Testing Safe Plan...", end="")
    safe_plan = PlanSchema(
        task_id="safe",
        scope_path=str(scope),
        folders_to_create=[str(scope / "NewFolder")],
        actions=[
            PlanAction(
                type=ActionType.MOVE,
                source_path=str(scope / "file.txt"),
                destination_path=str(scope / "NewFolder" / "file.txt"),
                reason="Organization",
                confidence=1.0
            )
        ],
        ambiguous_files=[],
        summary="Safe move"
    )
    res = validator.validate_plan(safe_plan)
    if not res.is_safe:
        print(f"FAILED: Safe plan marked unsafe: {res.issues}")
        exit(1)
    print("OK")
    
    # 2. Unsafe Source (System Path)
    print("Testing System Path Protection...", end="")
    unsafe_system = PlanSchema(
        task_id="system",
        scope_path=str(scope),
        folders_to_create=[],
        actions=[
            PlanAction(
                type=ActionType.DELETE,
                source_path="/System/Library/CoreServices/Finder.app", # Should trigger protected check
                destination_path=None,
                reason="Malicious",
                confidence=1.0
            )
        ],
        ambiguous_files=[],
        summary="Bad delete"
    )
    res = validator.validate_plan(unsafe_system)
    if res.is_safe:
        print("FAILED: System path delete was allowed!")
        exit(1)
    if not any("protected" in i for i in res.issues):
        print(f"FAILED: Issue message mismatch: {res.issues}")
        exit(1)
    print("OK")
    
    # 3. Scope Escape (Traversals resolved by Path)
    print("Testing Scope Escape...", end="")
    unsafe_scope = PlanSchema(
        task_id="escape",
        scope_path=str(scope),
        folders_to_create=[],
        actions=[
            PlanAction(
                type=ActionType.MOVE,
                source_path=str(scope / "file.txt"),
                destination_path="/tmp/outside_scope.txt",
                reason="Exfiltration",
                confidence=1.0
            )
        ],
        ambiguous_files=[],
        summary="Bad move"
    )
    res = validator.validate_plan(unsafe_scope)
    if res.is_safe:
        print("FAILED: Scope escape allowed!")
        exit(1)
    if not any("outside scope" in i for i in res.issues):
        print(f"FAILED: Issue message mismatch: {res.issues}")
        exit(1)
    print("OK")

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    test_safety()
