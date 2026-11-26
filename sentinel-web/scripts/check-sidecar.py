"""Exercise the frozen native backend from a directory outside the checkout."""

import json
import os
from pathlib import Path
import secrets
import subprocess
from tempfile import TemporaryDirectory
from time import monotonic, sleep
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from websockets.sync.client import connect


def check_backend(binary: Path, data: Path) -> None:
    token = secrets.token_hex(32)
    env = {
        **os.environ,
        "SENTINEL_ACCESS_TOKEN": token,
        "SENTINEL_DATABASE_URL": str(data / "sentinel.db"),
        "PATH": "",
    }
    env.pop("SENTINEL_ALLOWED_ORIGINS", None)
    env.pop("SENTINEL_API_PREFIX", None)
    with (data / "startup.log").open("w+") as output:
        child = subprocess.Popen(
            [str(binary)], stdin=subprocess.PIPE, stdout=output, env=env, cwd=data,
        )
        try:
            deadline = monotonic() + 30
            while monotonic() < deadline and child.poll() is None:
                output.seek(0)
                ready = next((line for line in output.read().splitlines()
                              if line.startswith("SENTINEL_READY ")), None)
                if ready:
                    break
                sleep(0.1)
            else:
                raise RuntimeError("Sidecar did not report readiness")
            port = int(ready.split()[1])
            base = f"http://127.0.0.1:{port}/api"
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

            def request(endpoint, payload=None):
                body = json.dumps(payload).encode() if payload is not None else None
                with urlopen(Request(base + endpoint, data=body, headers=headers), timeout=10) as response:
                    return json.load(response)

            try:
                urlopen(base + "/tasks", timeout=5).close()
            except HTTPError as error:
                assert error.code == 401
            else:
                raise AssertionError("Sidecar accepted an unauthenticated request")

            sample = data / "sample"
            sample.mkdir()
            for index in range(250):
                (sample / f"placeholder-{index}.unknown").touch()
            source = sample / "invoice.txt"
            source.write_text("sentinel smoke fixture", encoding="utf-8")
            with connect(f"ws://127.0.0.1:{port}/ws/events", origin="tauri://localhost",
                         subprotocols=["sentinel.events.v1", f"auth.{token}"], open_timeout=5) as socket:
                assert json.loads(socket.recv(timeout=5))["event_type"] == "CONNECTION_ACK"
                task = request("/plan", {"path": str(sample)})
                while True:
                    event = json.loads(socket.recv(timeout=10))
                    if event["event_type"] == "PLAN_READY":
                        break
                    if event["event_type"] == "ERROR":
                        raise AssertionError(event["message"])
                assert len(event["data"]["plan"]["actions"]) == 1

            request("/execute", {"task_id": task["task_id"], "approved_action_indices": [0]})
            destination = sample / "document" / source.name
            deadline = monotonic() + 10
            while monotonic() < deadline:
                state = request("/history")[0]["state"]
                if state == "completed":
                    break
                assert state == "executing", state
                sleep(0.1)
            assert destination.is_file() and not source.exists()
            assert request("/undo", {"task_id": task["task_id"]})["undone_operations"] == 1
            assert source.read_text(encoding="utf-8") == "sentinel smoke fixture"
            child.stdin.close()
            assert child.wait(timeout=10) == 0
        finally:
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=10)


if __name__ == "__main__":
    binaries = Path(__file__).resolve().parents[1] / "src-tauri" / "binaries"
    binary, = binaries.glob("sentinel-backend-*")
    with TemporaryDirectory(prefix="sentinel-sidecar-") as folder:
        check_backend(binary, Path(folder).resolve())
    print("Frozen backend startup, authentication, plan, apply, undo, and shutdown passed.")
