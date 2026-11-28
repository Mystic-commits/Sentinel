import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from sentinel_core.api.config import settings
from sentinel_core.api.main import app
from sentinel_core.api.memory import task_store
from sentinel_core.api.receipts import snapshot_sources
from sentinel_core.api.routers import plan
from sentinel_core.models.enums import ActionType, TaskState
from sentinel_core.models.planner import PlanAction, PlanSchema


@pytest.fixture(autouse=True)
def configure_access(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "database_url", str(tmp_path / "receipts.db"))
    monkeypatch.setattr(settings, "access_token", SecretStr("a" * 64))


@pytest.fixture
def inline_planner(monkeypatch):
    # Provider and pipeline doubles live in this process. The worker tests separately
    # exercise the real spawn and IPC boundary.
    async def run_here(job, *args, timeout):
        assert timeout > 0
        return await asyncio.to_thread(job, *args)

    monkeypatch.setattr(plan, "run_file_job", run_here)


def authorized_client():
    return TestClient(
        app, base_url="http://localhost", headers={"Authorization": "Bearer " + "a" * 64}
    )


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
    plan = PlanSchema(
        task_id="test-approved", scope_path=str(tmp_path), actions=actions, summary=""
    )
    monkeypatch.setitem(
        task_store,
        plan.task_id,
        {
            "plan": plan,
            "source_identities": snapshot_sources(plan),
            "state": TaskState.REVIEW,
            "authorized_root": str(tmp_path.resolve()),
        },
    )
    payload = {"task_id": plan.task_id, "approved_action_indices": [0]}
    with authorized_client() as client:
        assert client.post("/api/execute", json=payload).status_code == 200
        assert client.post("/api/execute", json=payload).status_code == 409

    assert (tmp_path / "sorted" / files[0].name).read_text() == files[0].name
    assert not files[0].exists()
    assert all(file.exists() for file in files[1:])
    assert task_store[plan.task_id]["state"] == TaskState.COMPLETED
    monkeypatch.delitem(task_store, plan.task_id)
    with authorized_client() as restarted:
        assert restarted.get("/api/history").json()[0]["state"] == "completed"
        assert (
            restarted.post("/api/undo", json={"task_id": plan.task_id}).json()["undone_operations"]
            == 1
        )
        assert restarted.post("/api/undo", json={"task_id": plan.task_id}).status_code == 409
    assert files[0].read_text() == files[0].name


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
    monkeypatch.setitem(
        task_store,
        plan.task_id,
        {
            "plan": plan,
            "source_identities": snapshot_sources(plan),
            "state": TaskState.REVIEW,
            "authorized_root": str(root.resolve()),
        },
    )
    with authorized_client() as client:
        response = client.post(
            "/api/execute", json={"task_id": plan.task_id, "approved_action_indices": [0]}
        )

    assert response.status_code == 409
    assert source.read_text() == "keep me"
    assert not destination.exists()


@pytest.mark.usefixtures("inline_planner")
def test_plan_falls_back_to_moves_inside_selected_folder(tmp_path, monkeypatch):
    from sentinel_core.planner.planner_agent import PlannerAgent

    def unavailable(*_args, **_kwargs):
        raise RuntimeError("Model unavailable in test")

    monkeypatch.setattr(PlannerAgent, "create_plan", unavailable)
    folder = tmp_path / "files"
    folder.mkdir()
    source = folder / "notes.txt"
    source.write_text("local test data")
    with authorized_client() as client:
        response = client.post("/api/plan", json={"path": str(folder)})
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


@pytest.mark.parametrize("change", ["destination", "original"])
def test_undo_preserves_changed_files(tmp_path, monkeypatch, change):
    source = tmp_path / "source.txt"
    destination = tmp_path / "destination.txt"
    source.write_text("original data")
    plan = PlanSchema(
        task_id="test-undo-conflict",
        scope_path=str(tmp_path),
        actions=[move(source, destination)],
        summary="",
    )
    monkeypatch.setitem(
        task_store,
        plan.task_id,
        {
            "plan": plan,
            "source_identities": snapshot_sources(plan),
            "state": TaskState.REVIEW,
            "authorized_root": str(tmp_path.resolve()),
        },
    )
    with authorized_client() as client:
        response = client.post(
            "/api/execute", json={"task_id": plan.task_id, "approved_action_indices": [0]}
        )
        assert response.status_code == 200
        changed = destination if change == "destination" else source
        changed.write_text("new user content")
        assert client.post("/api/undo", json={"task_id": plan.task_id}).status_code == 409
        assert changed.read_text() == "new user content"
        assert destination.exists()


def test_apply_rejects_changed_source(tmp_path, monkeypatch):
    source = tmp_path / "notes.txt"
    destination = tmp_path / "sorted.txt"
    source.write_text("before review")
    plan = PlanSchema(
        task_id="stale",
        scope_path=str(tmp_path),
        actions=[move(source, destination)],
        summary="",
    )
    monkeypatch.setitem(
        task_store,
        plan.task_id,
        {
            "plan": plan,
            "source_identities": snapshot_sources(plan),
            "authorized_root": str(tmp_path.resolve()),
            "state": TaskState.REVIEW,
        },
    )
    source.write_text("changed after review")
    with authorized_client() as client:
        response = client.post(
            "/api/execute",
            json={
                "task_id": plan.task_id,
                "approved_action_indices": [0],
            },
        )
        assert response.status_code == 409
        assert client.get("/api/history").json() == []
    assert source.read_text() == "changed after review"
    assert not destination.exists()


@pytest.mark.parametrize("mode", ["rules", "ai", "unsafe_ai"])
@pytest.mark.usefixtures("inline_planner")
def test_planning_mode_reports_actual_source_and_preserves_scope(tmp_path, monkeypatch, mode):
    from sentinel_core.planner.planner_agent import PlannerAgent

    folder = tmp_path / "sample"
    folder.mkdir()
    source = folder / "notes.txt"
    source.write_text("fixture")
    outside = tmp_path / "outside.txt"
    model_requests = []

    def fake_plan(self, task_id, scan_result, **_options):
        model_requests.append(self.user_prompt)
        assert scan_result.files[0].preview_text is None
        destination = outside if mode == "unsafe_ai" else folder / "notes" / source.name
        return PlanSchema(
            task_id=task_id,
            scope_path=str(tmp_path),
            actions=[move(source, destination)],
            summary="Fixture model result",
        )

    monkeypatch.setattr(PlannerAgent, "create_plan", fake_plan)
    payload = {"path": str(folder), "use_ai": mode != "rules"}
    if mode != "rules":
        payload["user_prompt"] = "Group the notes"
    with authorized_client() as client:
        response = client.post("/api/plan", json=payload)
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        try:
            task = task_store[task_id]
            expected_source = "ai" if mode == "ai" else "rules"
            assert task["summary"]["planning_source"] == expected_source
            detail = client.get(f"/api/tasks/{task_id}")
            assert detail.status_code == 200
            assert detail.json()["planning_source"] == expected_source
            assert detail.json()["total_actions"] == 1
            assert model_requests == (["Group the notes"] if mode != "rules" else [])
            assert task["plan"].scope_path == str(folder.resolve())
            assert len(task["plan"].actions) == 1
            assert Path(task["plan"].actions[0].destination_path).is_relative_to(folder)
            assert source.is_file() and not outside.exists()
        finally:
            task_store.pop(task_id, None)


@pytest.mark.parametrize("route", ["/api/scan", "/api/plan"])
@pytest.mark.parametrize("folder", [".", "", "../files", "/tmp/bad\x00folder"])
def test_folder_jobs_require_explicit_absolute_path(route, folder):
    with authorized_client() as client:
        response = client.post(route, json={"path": folder})
    assert response.status_code == 422


@pytest.mark.usefixtures("inline_planner")
def test_failed_planning_remains_queryable(tmp_path, monkeypatch):
    from sentinel_core.cleanpc.pipeline import CleanPCPipeline

    async def fail(*_args, **_kwargs):
        raise ValueError("Fixture planning error")

    monkeypatch.setattr(CleanPCPipeline, "scan_and_plan", fail)
    with authorized_client() as client:
        response = client.post("/api/plan", json={"path": str(tmp_path), "use_ai": False})
        task_id = response.json()["task_id"]
        try:
            detail = client.get(f"/api/tasks/{task_id}").json()
            assert detail["state"] == "failed"
            assert detail["summary"] == "Fixture planning error"
            latest = client.get("/api/tasks?limit=1").json()["tasks"][0]
            assert latest["task_id"] == task_id
            assert latest["created_at"] == detail["created_at"]
        finally:
            task_store.pop(task_id, None)


@pytest.mark.usefixtures("inline_planner")
def test_folder_plan_classifies_without_reading_file_contents(tmp_path, monkeypatch):
    from sentinel_core.cleanpc.classifiers import FileClassifier

    def forbid_hashing(*_args):
        pytest.fail("Folder-scoped planning must not hash file contents")

    monkeypatch.setattr(FileClassifier, "_compute_hash", forbid_hashing)
    (tmp_path / "invoice.pdf").write_bytes(b"invoice")
    with authorized_client() as client:
        response = client.post("/api/plan", json={"path": str(tmp_path), "use_ai": False})
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        try:
            assert client.get(f"/api/tasks/{task_id}").json()["state"] == "review"
        finally:
            task_store.pop(task_id, None)


@pytest.mark.parametrize("proposal", ["Invoices", "../outside", "C:/outside"])
@pytest.mark.usefixtures("inline_planner")
def test_scoped_model_proposal_uses_inventory_ids(tmp_path, monkeypatch, proposal):
    from sentinel_core.planner.ollama_client import OllamaClient

    def generate(_self, prompt, model):
        assert model == "llama2"
        assert str(tmp_path) not in prompt
        return {"moves": [{"file_id": "F1", "folder": proposal}]}

    monkeypatch.setattr(OllamaClient, "generate_json", generate)
    (tmp_path / "invoice.pdf").write_bytes(b"fixture")
    with authorized_client() as client:
        response = client.post("/api/plan", json={"path": str(tmp_path), "use_ai": True})
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        try:
            detail = client.get(f"/api/tasks/{task_id}").json()
            ai_plan = proposal == "Invoices"
            assert detail["planning_source"] == ("ai" if ai_plan else "rules")
            destination = "Invoices/invoice.pdf" if ai_plan else "document/invoice.pdf"
            assert Path(detail["plan"]["actions"][0]["destination_path"]) == tmp_path / destination
        finally:
            task_store.pop(task_id, None)


@pytest.mark.parametrize(
    ("route", "id_field"), [("/api/scan", "scan_id"), ("/api/plan", "task_id")]
)
def test_unavailable_folder_is_reported_in_background_job(tmp_path, route, id_field):
    with authorized_client() as client:
        response = client.post(route, json={"path": str(tmp_path / "missing")})
        assert response.status_code == 200
        task_id = response.json()[id_field]
        try:
            detail = client.get(f"/api/tasks/{task_id}").json()
            assert detail["state"] == "failed"
            assert detail["summary"] == "The selected folder is unavailable"
        finally:
            task_store.pop(task_id, None)
