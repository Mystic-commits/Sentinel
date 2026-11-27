import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from starlette.websockets import WebSocketDisconnect

from sentinel_core.api.config import settings
from sentinel_core.api.main import app

TOKEN = "a" * 64
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
PROTOCOLS = ["sentinel.events.v1", f"auth.{TOKEN}"]


def test_local_http_requires_token_and_allowed_origin(monkeypatch):
    with TestClient(app, base_url="http://localhost") as client:
        monkeypatch.setattr(settings, "access_token", None)
        assert client.get("/api/tasks", headers=HEADERS).status_code == 401
        monkeypatch.setattr(settings, "access_token", SecretStr(TOKEN))
        assert client.get("/api/tasks").status_code == 401
        assert (
            client.get("/api/tasks", headers={"Authorization": "Bearer wrong"}).status_code == 401
        )
        assert client.get("/api/tasks", headers=HEADERS).status_code == 200
        assert (
            client.get(
                "/api/tasks", headers={**HEADERS, "Origin": "https://example.org"}
            ).status_code
            == 403
        )
        assert (
            client.get("/api/tasks", headers={**HEADERS, "Host": "example.org"}).status_code == 400
        )


def test_websocket_requires_token_and_allowed_origin(monkeypatch):
    monkeypatch.setattr(settings, "access_token", SecretStr(TOKEN))
    with TestClient(app, base_url="http://localhost") as client:
        for protocols, headers in [
            (["sentinel.events.v1"], {}),
            (["sentinel.events.v1", "auth.wrong"], {}),
            (PROTOCOLS, {"Origin": "https://example.org"}),
        ]:
            with (
                pytest.raises(WebSocketDisconnect) as error,
                client.websocket_connect(
                    "ws://localhost/ws/events", subprotocols=protocols, headers=headers
                ),
            ):
                pass
            assert error.value.code == 1008

        with client.websocket_connect("ws://localhost/ws/events", subprotocols=PROTOCOLS) as socket:
            assert socket.accepted_subprotocol == "sentinel.events.v1"
            assert socket.receive_json()["event_type"] == "CONNECTION_ACK"
