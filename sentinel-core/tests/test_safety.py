
import pytest

from sentinel_core.models.enums import ActionType
from sentinel_core.models.planner import PlanAction, PlanSchema
from sentinel_core.safety.safety import SafetyValidator


@pytest.mark.parametrize("kind", [ActionType.MOVE, ActionType.RENAME, ActionType.DELETE])
def test_accepts_existing_scoped_source(tmp_path, kind):
    source = tmp_path / "source.txt"
    source.touch()
    action = PlanAction(
        type=kind, source_path=str(source),
        destination_path=None if kind == ActionType.DELETE else str(tmp_path / "dest.txt"),
        confidence=1, reason="Test",
    )
    plan = PlanSchema(task_id="safe", scope_path=str(tmp_path), actions=[action], summary="")
    assert SafetyValidator().validate_plan(plan).is_safe


@pytest.mark.parametrize("violation", ["folder", "source", "destination", "missing", "protected"])
def test_rejects_unsafe_plan(tmp_path, monkeypatch, violation):
    root = tmp_path / "granted"
    root.mkdir()
    source = root / "source.txt"
    destination = root / "destination.txt"
    folders: list[str] = []
    if violation == "folder":
        folders = [str(tmp_path / "outside")]
    elif violation == "source":
        source = tmp_path / "outside.txt"
    elif violation == "destination":
        destination = tmp_path / "outside.txt"
    elif violation == "protected":
        monkeypatch.setattr("sentinel_core.safety.safety.PROTECTED_PATHS", {root.resolve()})
    if violation != "missing":
        source.touch()

    plan = PlanSchema(
        task_id="unsafe",
        scope_path=str(root),
        actions=[PlanAction(
            type=ActionType.MOVE,
            source_path=str(source),
            destination_path=str(destination),
            reason="Test",
            confidence=1,
        )],
        folders_to_create=folders,
        summary="",
    )
    result = SafetyValidator().validate_plan(plan)
    assert not result.is_safe
    assert result.errors
