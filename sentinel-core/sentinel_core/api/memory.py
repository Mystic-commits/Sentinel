"""
In-Memory Task Store

Temporary storage for tasks and plans until database integration is complete.
"""

from typing import Dict, Any

# Global dictionary to store task data
# Key: task_id, Value: dict containing 'plan', 'status', etc.
task_store: Dict[str, Any] = {}

def save_task(task_id: str, data: Dict[str, Any]):
    """Save or update task data."""
    if task_id not in task_store:
        task_store[task_id] = {}
    
    task_store[task_id].update(data)

def get_task(task_id: str) -> Dict[str, Any]:
    """Get task data."""
    return task_store.get(task_id)
