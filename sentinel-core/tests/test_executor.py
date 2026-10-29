import pytest
from sentinel_core.executor import Executor
from sentinel_core.executor.executor import execute_plan
from sentinel_core.models.planner import PlanSchema, PlanAction


def make_plan(tmp_path):
    source = tmp_path / "source"
    source.write_text("important")
    return PlanSchema(
        task_id="test",
        scope_path=str(tmp_path),
        summary="move",
        actions=[
            PlanAction(
                type="move",
                source_path=str(source),
                destination_path=str(tmp_path / "new" / "file"),
                reason="test",
                confidence=1,
            )
        ],
    )


@pytest.mark.asyncio
async def test_dry_run(tmp_path):
    result = await Executor().execute_plan(make_plan(tmp_path))
    assert result.successful_actions == 1
    assert (tmp_path / "source").read_text() == "important"
    assert not (tmp_path / "new").exists()


def test_move(tmp_path):
    result = execute_plan(make_plan(tmp_path))
    assert result.successful_actions == 1
    assert not (tmp_path / "source").exists()
    assert (tmp_path / "new" / "file").read_text() == "important"


def test_scope_cannot_be_bypassed(tmp_path):
    plan = make_plan(tmp_path)
    plan.scope_path = str(tmp_path / "new")
    assert execute_plan(plan).error_message
    assert (tmp_path / "source").exists()


def test_collision(tmp_path):
    plan = make_plan(tmp_path)
    dest = tmp_path / "new" / "file"
    dest.parent.mkdir()
    dest.write_text("existing")
    assert execute_plan(plan).error_message
    assert dest.read_text() == "existing"
    assert (tmp_path / "source").read_text() == "important"


def test_trash(tmp_path, monkeypatch):
    plan = make_plan(tmp_path)
    plan.actions[0].type = "delete"
    plan.actions[0].destination_path = None
    calls = []
    monkeypatch.setattr("sentinel_core.executor.executor.send2trash", calls.append)
    assert execute_plan(plan).successful_actions == 1
    assert calls == [str(tmp_path / "source")]


def test_empty_selection(tmp_path):
    assert execute_plan(make_plan(tmp_path), approved_actions=[]).successful_actions == 0
    assert (tmp_path / "source").exists()
