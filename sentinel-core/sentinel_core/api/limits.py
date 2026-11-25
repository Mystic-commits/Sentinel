"""Process-local capacity limits for the single-user backend."""

from collections import deque
from threading import Lock
from time import monotonic
from typing import Awaitable, Callable

from fastapi import BackgroundTasks, HTTPException

MAX_SCAN_ENTRIES = 10_000
MAX_SCAN_SECONDS = 15
MAX_MODEL_FILES = 250
MUTATIONS_PER_MINUTE = 30

_scan_slot = Lock()
_recent_mutations: deque[float] = deque()
_rate_lock = Lock()


def rate_limit_mutation() -> None:
    with _rate_lock:
        now = monotonic()
        while _recent_mutations and now - _recent_mutations[0] >= 60:
            _recent_mutations.popleft()
        if len(_recent_mutations) >= MUTATIONS_PER_MINUTE:
            remaining = 60 - (now - _recent_mutations[0])
            raise HTTPException(429, "Too many requests", headers={"Retry-After": str(int(remaining) + 1)})
        _recent_mutations.append(now)


def schedule_scan_job(
    background: BackgroundTasks,
    job: Callable[..., Awaitable[None]],
    *args,
) -> None:
    if not _scan_slot.acquire(blocking=False):
        raise HTTPException(429, "A scan or plan is already running", headers={"Retry-After": "2"})

    async def run() -> None:
        try:
            await job(*args)
        finally:
            _scan_slot.release()

    background.add_task(run)
