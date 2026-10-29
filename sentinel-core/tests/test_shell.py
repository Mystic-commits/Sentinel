import io
import httpx
import pytest
from rich.console import Console
from sentinel_core.cli.shell import Shell


def session(confirm="CANCEL"):
    calls = []

    def handle(request):
        calls.append(request)
        if request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "state": "review",
                    "summary": "Preview",
                    "plan": {
                        "actions": [
                            {
                                "type": "move",
                                "source_path": "/example/a",
                                "destination_path": "/example/b",
                                "reason": "group",
                            }
                        ]
                    },
                },
            )
        return httpx.Response(200, json={"task_id": "task-one"})

    shell = Shell(
        httpx.Client(base_url="http://127.0.0.1:8000", transport=httpx.MockTransport(handle)),
        console=Console(file=io.StringIO()),
        confirm=lambda _: confirm,
    )
    return shell, calls


def test_prompt_requires_folder_and_never_executes(tmp_path):
    shell, calls = session()
    with pytest.raises(ValueError, match="folder"):
        shell.handle("Organize PDFs")
    assert calls == []
    shell.handle("/folder " + str(tmp_path))
    shell.handle("Organize PDFs")
    assert shell.task_id == "task-one"
    assert calls[0].url.path == "/api/plan"
    assert b"Organize PDFs" in calls[0].content


def test_cancel_does_not_execute():
    shell, calls = session()
    shell.task_id = "task-one"
    shell.handle("/apply 1")
    assert all(call.method == "GET" for call in calls)


def test_apply_sends_only_confirmed_selection():
    shell, calls = session("APPLY")
    shell.task_id = "task-one"
    shell.handle("/apply 1")
    import json

    assert json.loads(calls[-1].content)["approved_actions"] == [0]


@pytest.mark.parametrize("command", ["/apply 0", "/apply 2", "/apply 1,1", "/apply all"])
def test_invalid_selection_never_executes(command):
    shell, calls = session("APPLY")
    shell.task_id = "task-one"
    with pytest.raises(ValueError):
        shell.handle(command)
    assert all(call.method == "GET" for call in calls)


def test_rules_mode_is_explicit_and_shared_with_api(tmp_path):
    import json

    shell, calls = session()
    shell.handle("/folder " + str(tmp_path))
    shell.handle("/mode rules")
    shell.handle("Create a preview")
    assert json.loads(calls[-1].content)["strategy"] == "file_types"


def test_resume_reopens_saved_plan():
    shell, calls = session()
    shell.handle("/resume saved-task")
    assert shell.task_id == "saved-task"
    assert calls[-1].url.path == "/api/tasks/saved-task"
    assert all(call.method == "GET" for call in calls)


def test_review_displays_fallback_and_failure():
    shell, _ = session()
    shell.review(
        {
            "state": "failed",
            "error": "Folder is unavailable",
            "planning_warning": "Custom instructions were not used",
        }
    )
    output = shell.console.file.getvalue()
    assert "Folder is unavailable" in output
    assert "Custom instructions were not used" in output


def test_non_json_api_error_is_readable():
    client = httpx.Client(
        base_url="http://127.0.0.1:8000",
        transport=httpx.MockTransport(lambda _: httpx.Response(503, text="unavailable")),
    )
    shell = Shell(client)
    with pytest.raises(ValueError, match="Service Unavailable"):
        shell.handle("/history")
