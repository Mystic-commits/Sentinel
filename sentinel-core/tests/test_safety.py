import pytest
from sentinel_core.models.planner import PlanSchema, PlanAction
from sentinel_core.safety import SafetyValidator


def make_plan(root, source, dest=None, kind="move", folders=None):
    return PlanSchema(
        task_id="test",
        scope_path=str(root),
        summary="test",
        folders_to_create=folders or [],
        actions=[
            PlanAction(
                type=kind,
                source_path=str(source),
                destination_path=str(dest) if dest else None,
                reason="test",
                confidence=1,
            )
        ],
    )


def test_safe_move(tmp_path):
    source = tmp_path / "file"
    source.write_text("keep")
    assert (
        SafetyValidator()
        .validate_plan(make_plan(tmp_path, source, tmp_path / "new" / "file"))
        .is_safe
    )


@pytest.mark.parametrize("escape", ["source", "destination", "folder"])
def test_scope_escape(tmp_path, escape):
    root = tmp_path / "scope"
    root.mkdir()
    source = root / "file"
    source.write_text("keep")
    outside = tmp_path / "private"
    outside.write_text("private")
    plan = make_plan(
        root,
        outside if escape == "source" else source,
        outside if escape == "destination" else root / "new",
        folders=[str(tmp_path / "elsewhere")] if escape == "folder" else [],
    )
    result = SafetyValidator().validate_plan(plan)
    assert not result.is_safe
    assert any("outside scope" in e for e in result.errors)


def test_symlink_escape(tmp_path):
    root = tmp_path / "scope"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    source = root / "file"
    source.write_text("keep")
    try:
        (root / "link").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Symlinks unavailable")
    assert (
        not SafetyValidator().validate_plan(make_plan(root, source, root / "link" / "file")).is_safe
    )


def test_directory_delete(tmp_path):
    assert not SafetyValidator().validate_plan(make_plan(tmp_path, tmp_path, kind="delete")).is_safe


def test_missing_paths(tmp_path):
    plan = PlanSchema(
        task_id="test",
        scope_path=str(tmp_path),
        summary="test",
        actions=[PlanAction(type="move", reason="invalid", confidence=1)],
    )
    assert not SafetyValidator().validate_plan(plan).is_safe


def test_protected(tmp_path, monkeypatch):
    source = tmp_path / "protected"
    source.write_text("keep")
    monkeypatch.setattr("sentinel_core.safety.safety.PROTECTED_PATHS", {source})
    assert not SafetyValidator().validate_plan(make_plan(tmp_path, source, kind="delete")).is_safe
