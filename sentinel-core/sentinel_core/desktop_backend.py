"""Launch the bundled local backend on an OS-assigned loopback port."""

import socket
import sys
from multiprocessing import freeze_support
from threading import Thread

import uvicorn

from sentinel_core.api.config import settings
from sentinel_core.api.main import app


def main() -> None:
    if settings.access_token is None:
        raise SystemExit("Desktop backend requires a session token")

    class DesktopServer(uvicorn.Server):
        async def startup(self, sockets=None):
            await super().startup(sockets=sockets)
            if self.started:
                print(f"SENTINEL_READY {listener.getsockname()[1]}", flush=True)

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        server = DesktopServer(
            uvicorn.Config(app, log_level="warning", access_log=False, ws_max_size=64 * 1024)
        )

        def stop_on_parent_exit() -> None:
            sys.stdin.buffer.read()
            server.should_exit = True

        Thread(target=stop_on_parent_exit, daemon=True).start()
        server.run(sockets=[listener])


if __name__ == "__main__":
    freeze_support()
    main()
