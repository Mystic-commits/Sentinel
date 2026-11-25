from pathlib import Path

import pytest
from pydantic import SecretStr

from sentinel_core.api.config import settings
from fastapi.testclient import TestClient

from sentinel_core.api.main import app
from sentinel_core.api.memory import task_store
from sentinel_core.models.enums import ActionType, TaskState
from sentinel_core.models.planner import PlanAction, PlanSchema


@pytest.fixture(autouse=True)
def configure_access(monkeypatch):
    monkeypatch.setattr(settings, "access_token", SecretStr("a" * 64))


def authorized_client():
    return TestClient(app, base_url="http://localhost", headers={"Authorization": "Bearer " + "a" * 64})


def move(source: Path, destination: Path) -> PlanAction:
    return PlanAction(
        type=ActionType.MOVE,
        source_path=str(source),
        destination_path=str(destination),
        reason="Regression fixture",
        confidence=1,
    )


def test_execution_changes_only_approved_files_and_rejects_replay(tmp_path, monkeypatch):
    files = [tmp_path / name for name in ("approved.txt", "rejected.txt", "pending.txt")]
    for file in files:
        file.write_text(file.name)
    actions = [move(file, tmp_path / "sorted" / file.name) for file in files]
    plan = PlanSchema(task_id="test-approved", scope_path=str(tmp_path), actions=actions, summary="")
    monkeypatch.setitem(task_store, plan.task_id, {
        "plan": plan,
        "state": TaskState.REVIEW,
        "authorized_root": str(tmp_path.resolve()),
    })
    payload = {"task_id": plan.task_id, "approved_action_indices": [0]}
    with authorized_client() as client:
        assert client.post("/api/execute", json=payload).status_code == 200
        assert client.post("/api/execute", json=payload).status_code == 409

    assert (tmp_path / "sorted" / files[0].name).read_text() == files[0].name
    assert not files[0].exists()
    assert all(file.exists() for file in files[1:])
    assert task_store[plan.task_id]["state"] == TaskState.COMPLETED


def test_execution_rejects_out_of_scope_destination(tmp_path, monkeypatch):
    root = tmp_path / "selected"
    root.mkdir()
    source = root / "file.txt"
    source.write_text("keep me")
    destination = tmp_path / "outside.txt"
    plan = PlanSchema(
        task_id="test-scope",
        scope_path=str(root),
        actions=[move(source, destination)],
        summary="",
    )
    monkeypatch.setitem(task_store, plan.task_id, {
        "plan": plan,
        "state": TaskState.REVIEW,
        "authorized_root": str(root.resolve()),
    })
    with authorized_client() as client:
        response = client.post(
            "/api/execute", json={"task_id": plan.task_id, "approved_action_indices": [0]}
        )

    assert response.status_code == 409
    assert source.read_text() == "keep me"
    assert not destination.exists()


def test_plan_falls_back_to_moves_inside_selected_folder(tmp_path, monkeypatch):
    from sentinel_core.planner.planner_agent import PlannerAgent

    def unavailable(*args, **kwargs):
        raise RuntimeError("Model unavailable in test")

    monkeypatch.setattr(PlannerAgent, "create_plan", unavailable)
    source = tmp_path / "notes.txt"
    source.write_text("local test data")
    with authorized_client() as client:
        response = client.post("/api/plan", json={"path": str(tmp_path)})
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        try:
            plan = task_store[task_id]["plan"]
            assert task_store[task_id]["state"] == TaskState.REVIEW
            assert len(plan.actions) == 1
            assert Path(plan.actions[0].source_path) == source
            assert Path(plan.actions[0].destination_path).is_relative_to(tmp_path)
            assert source.exists()
        finally:
            task_store.pop(task_id, None)
