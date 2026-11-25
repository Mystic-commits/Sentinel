import asyncio
from collections import deque

import pytest
from fastapi import BackgroundTasks, HTTPException

from sentinel_core.api import limits
from sentinel_core.scanner.scanner import Scanner


def test_rate_limit_expires(monkeypatch):
    monkeypatch.setattr(limits, "_recent_mutations", deque())
    monkeypatch.setattr(limits, "MUTATIONS_PER_MINUTE", 1)
    monkeypatch.setattr(limits, "monotonic", lambda: 100)
    limits.rate_limit_mutation()
    with pytest.raises(HTTPException) as rejected:
        limits.rate_limit_mutation()
    assert rejected.value.status_code == 429
    assert int(rejected.value.headers["Retry-After"]) > 0

    monkeypatch.setattr(limits, "monotonic", lambda: 160)
    limits.rate_limit_mutation()


def test_scan_slot_releases_after_worker_failure():
    async def fail():
        raise RuntimeError("worker failed")

    async def success():
        return None

    first = BackgroundTasks()
    limits.schedule_scan_job(first, fail)
    second = BackgroundTasks()
    with pytest.raises(HTTPException) as rejected:
        limits.schedule_scan_job(second, success)
    assert rejected.value.status_code == 429
    with pytest.raises(RuntimeError, match="worker failed"):
        asyncio.run(first())
    limits.schedule_scan_job(second, success)
    asyncio.run(second())


@pytest.mark.parametrize("budget", [{"max_entries": 2}, {"max_seconds": 0}])
def test_scan_reports_partial_inventory(tmp_path, budget):
    for i in range(3):
        (tmp_path / f"{i}.txt").touch()

    result = Scanner(str(tmp_path), include_previews=False, **budget).scan()

    assert result.truncated
    assert len(result.files) == (2 if "max_entries" in budget else 0)
    assert result.errors
