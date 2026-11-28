"""
In-Memory Task Store

Temporary storage for tasks and plans until database integration is complete.
"""

from datetime import UTC, datetime
from typing import Any

# Global dictionary to store task data
# Key: task_id, Value: dict containing 'plan', 'status', etc.
task_store: dict[str, Any] = {}


def save_task(task_id: str, data: dict[str, Any]):
    """Save or update task data."""
    if task_id not in task_store:
        task_store[task_id] = {"created_at": datetime.now(UTC)}

    task_store[task_id].update(data)


def get_task(task_id: str) -> dict[str, Any]:
    """Get task data."""
    return task_store.get(task_id)
