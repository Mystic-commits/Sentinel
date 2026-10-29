"""Prompt-first terminal client for the same local API used by the dashboard."""

import argparse
import shlex
from pathlib import Path

import httpx
from rich.console import Console
from rich.table import Table

HELP = """Describe what you want to organize to create a preview.
/folder PATH        Choose a folder (required before planning)
/mode ai|rules      Choose local AI or predictable file-type rules
/status             Refresh the current task
/review             Show numbered proposed changes
/apply 1,3          Review and confirm selected changes
/help               Show commands
/exit               Leave the session
No file changes happen until you confirm /apply."""


class Shell:
    def __init__(self, client, console=None, path=None, confirm=input):
        self.client = client
        self.console = console or Console()
        self.path = str(Path(path).expanduser().resolve()) if path else None
        self.task_id = None
        self.strategy = "local_ai"
        self.confirm = confirm

    def request(self, method, endpoint, **kwargs):
        response = self.client.request(method, endpoint, **kwargs)
        if response.is_error:
            detail = response.json().get("detail", response.reason_phrase)
            raise ValueError(str(detail))
        return response.json()

    def task(self):
        if not self.task_id:
            raise ValueError("Create a plan first by describing what you want.")
        return self.request("GET", f"/api/tasks/{self.task_id}")

    def review(self, task):
        plan = task.get("plan")
        if not plan:
            self.console.print(f"Task is {task['state']}. Use /status in a moment.", markup=False)
            return
        table = Table("Number", "Change", "From", "To", "Why")
        for i, action in enumerate(plan["actions"], 1):
            table.add_row(
                str(i),
                action["type"],
                action.get("source_path") or "",
                action.get("destination_path") or "System Trash",
                action["reason"],
            )
        self.console.print(table)

    def handle(self, text):
        text = text.strip()
        if not text:
            return True
        if text == "/exit":
            return False
        if text == "/help":
            self.console.print(HELP, markup=False)
        elif text.startswith("/folder "):
            args = shlex.split(text)
            if len(args) != 2:
                raise ValueError('Use /folder "path with spaces"')
            path = Path(args[1]).expanduser().resolve()
            if not path.is_dir():
                raise ValueError("Choose an existing folder.")
            self.path = str(path)
            self.task_id = None
            self.console.print(f"Folder: {self.path}", markup=False)
        elif text.startswith("/mode "):
            mode = text[6:].strip()
            if mode not in {"ai", "rules"}:
                raise ValueError("Use /mode ai or /mode rules")
            self.strategy = "local_ai" if mode == "ai" else "file_types"
            self.console.print("Local AI selected." if mode == "ai" else "File-type rules selected. No model needed; custom text instructions are not interpreted.")
        elif text == "/status":
            task = self.task()
            self.console.print(f"{task['state']}: {task['summary']}", markup=False)
            if task.get("recovery_required"):
                self.console.print(
                    "Interrupted task: inspect files and receipts before creating a new plan."
                )
        elif text == "/review":
            self.review(self.task())
        elif text.startswith("/apply "):
            task = self.task()
            if task["state"] != "review" or not task.get("plan"):
                raise ValueError("Only a plan awaiting review can be applied.")
            indices = [int(value.strip()) - 1 for value in text[7:].split(",")]
            actions = task["plan"]["actions"]
            if (
                not indices
                or len(set(indices)) != len(indices)
                or any(i < 0 or i >= len(actions) for i in indices)
            ):
                raise ValueError("Choose unique action numbers from /review.")
            self.review({"plan": {"actions": [actions[i] for i in indices]}})
            self.console.print(
                f"Apply {len(indices)} selected changes to task {self.task_id}?", markup=False
            )
            if self.confirm("Type APPLY to confirm: ") != "APPLY":
                self.console.print("Cancelled. No changes requested.")
                return True
            self.request(
                "POST", "/api/execute", json={"task_id": self.task_id, "approved_actions": indices}
            )
            self.console.print("Changes requested. Use /status for the result.")
        elif text.startswith("/"):
            raise ValueError("Unknown command. Use /help.")
        else:
            if not self.path:
                raise ValueError("Choose a folder first with /folder PATH.")
            response = self.request(
                "POST", "/api/plan", json={"path": self.path, "user_prompt": text, "strategy": self.strategy}
            )
            self.task_id = response["task_id"]
            self.console.print(
                f"Preview requested: {self.task_id}. Use /status, then /review.", markup=False
            )
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Sentinel: describe, review, approve. Local files stay local."
    )
    parser.add_argument("--path", help="Initial folder to organize")
    args = parser.parse_args()
    console = Console()
    console.print("[bold]Sentinel[/bold] · Your local workspace assistant")
    console.print("Describe a goal, or use /help. Changes always require review and confirmation.")
    # Fixed loopback endpoint: terminal prompts never go to a remote server.
    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=30, trust_env=False) as client:
        shell = Shell(client, console, args.path)
        while True:
            try:
                if not shell.handle(console.input("[bold cyan]sentinel › [/bold cyan]")):
                    break
            except (EOFError, KeyboardInterrupt):
                console.print("\nSession closed. Submitted tasks remain in local history.")
                break
            except (ValueError, httpx.HTTPError) as error:
                console.print(f"Could not continue: {error}", markup=False)


if __name__ == "__main__":
    main()
