"""Authentication for the single-user local API."""

from secrets import compare_digest

from fastapi import HTTPException, Request

from .config import settings
from .limits import rate_limit_mutation

EVENT_PROTOCOL = "sentinel.events.v1"


def authorized(token: str) -> bool:
    expected = settings.access_token
    return bool(
        expected
        and compare_digest(token.encode(), expected.get_secret_value().encode())
    )


async def require_access(request: Request) -> None:
    origin = request.headers.get("origin")
    if origin is not None and origin not in settings.allowed_origins:
        raise HTTPException(status_code=403, detail="Origin is not allowed")

    scheme, _, token = request.headers.get("authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not authorized(token):
        raise HTTPException(
            status_code=401,
            detail="A valid Sentinel access token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        rate_limit_mutation()
