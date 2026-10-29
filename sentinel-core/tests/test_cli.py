"""Exercise public commands against the real API and disposable files."""

import importlib
from types import SimpleNamespace
import httpx
from contextlib import nullcontext

import pytest
from fastapi.testclient import TestClient
from sentinel_core.api.main import app as api_app
from sentinel_core.api.memory import task_store
from sentinel_core.cli.main import app


@pytest.fixture
def agent(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "sentinel_core.api.config.settings.task_database_path", str(tmp_path / "tasks.sqlite3")
    )
    with TestClient(api_app, base_url="http://127.0.0.1") as client:
        monkeypatch.setattr(
            "sentinel_core.cli.main.httpx",
            SimpleNamespace(Client=lambda **kwargs: nullcontext(client), HTTPError=httpx.HTTPError),
        )
        yield client


def test_public_cli_plan_review_cancel_then_apply(agent, tmp_path, monkeypatch):
    folder = tmp_path / "Inbox"
    folder.mkdir()
    (folder / "note.txt").write_text("Important content")
    app(["plan", str(folder), "--strategy", "file_types"])
    task_id = agent.get("/api/tasks").json()["tasks"][0]["task_id"]
    app(["history"])
    app(["review", task_id])
    module = importlib.import_module("sentinel_core.cli.main")
    original = module.Shell
    monkeypatch.setattr(module, "Shell", lambda *args: original(*args, confirm=lambda _: "CANCEL"))
    app(["apply", task_id, "--actions", "1"])
    assert (folder / "note.txt").exists()
    monkeypatch.setattr(module, "Shell", lambda *args: original(*args, confirm=lambda _: "APPLY"))
    app(["apply", task_id, "--actions", "1"])
    app(["status", task_id])
    assert (folder / "Documents" / "note.txt").read_text() == "Important content"
    assert agent.get(f"/api/tasks/{task_id}").json()["state"] == "completed"
    with pytest.raises(SystemExit) as error:
        app(["apply", task_id, "--actions", "1"])
    assert error.value.code == 1


def test_plan_prompt_cannot_dispatch_shell_commands(agent, tmp_path):
    with pytest.raises(SystemExit):
        app(["plan", str(tmp_path), "--prompt", "/apply 1"])
    assert len(task_store) == 0


def test_unsupported_commands_fail_instead_of_reporting_success():
    with pytest.raises(SystemExit) as error:
        app(["undo", "any-task"])
    assert error.value.code == 2
