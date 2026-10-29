"""Transactional local task storage. No filesystem work occurs before execution is claimed."""

import json
import sqlite3
from contextlib import contextmanager
from collections.abc import MutableMapping
from datetime import datetime, timezone
from pathlib import Path

from fastapi.encoders import jsonable_encoder
from sentinel_core.models.planner import PlanSchema
from .config import settings


def now():
    return datetime.now(timezone.utc).isoformat()


class TaskStore(MutableMapping):
    def __init__(self, path=None):
        self.path = path

    @contextmanager
    def connect(self):
        path = Path(self.path or settings.task_database_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(path, timeout=10)
        try:
            db.execute("PRAGMA synchronous=FULL")
            db.execute(
                "CREATE TABLE IF NOT EXISTS api_tasks (id TEXT PRIMARY KEY, data TEXT NOT NULL)"
            )
            with db:
                yield db
        finally:
            db.close()

    def decode(self, raw):
        data = json.loads(raw)
        if data.get("plan"):
            data["plan"] = PlanSchema.model_validate(data["plan"])
        return data

    def __getitem__(self, key):
        with self.connect() as db:
            row = db.execute("SELECT data FROM api_tasks WHERE id=?", (key,)).fetchone()
        if row is None:
            raise KeyError(key)
        return self.decode(row[0])

    def __setitem__(self, key, value):
        with self.connect() as db:
            db.execute(
                "INSERT OR REPLACE INTO api_tasks VALUES (?, ?)",
                (key, json.dumps(jsonable_encoder(value))),
            )

    def __delitem__(self, key):
        with self.connect() as db:
            cursor = db.execute("DELETE FROM api_tasks WHERE id=?", (key,))
            if not cursor.rowcount:
                raise KeyError(key)

    def __iter__(self):
        with self.connect() as db:
            rows = db.execute("SELECT id FROM api_tasks").fetchall()
        return iter(row[0] for row in rows)

    def __len__(self):
        with self.connect() as db:
            return db.execute("SELECT COUNT(*) FROM api_tasks").fetchone()[0]

    def update_task(self, key, updates, expected_state=None):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT data FROM api_tasks WHERE id=?", (key,)).fetchone()
            data = self.decode(row[0]) if row else {"created_at": now()}
            if expected_state is not None and data.get("state") != expected_state:
                return False
            data.update(updates)
            data["updated_at"] = now()
            db.execute(
                "INSERT OR REPLACE INTO api_tasks VALUES (?, ?)",
                (key, json.dumps(jsonable_encoder(data))),
            )
        return True

    def append_receipt(self, key, action, event):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT data FROM api_tasks WHERE id=?", (key,)).fetchone()
            if not row:
                raise KeyError(key)
            data = json.loads(row[0])
            data.setdefault("receipts", []).append(
                {"timestamp": now(), "event": event, "action": jsonable_encoder(action)}
            )
            db.execute("UPDATE api_tasks SET data=? WHERE id=?", (json.dumps(data), key))

    def recover_interrupted(self):
        # Single local API process only. Never automatically replay uncertain mutations.
        for key in list(self):
            data = self[key]
            if data.get("state") in {"executing", "planning", "scanning"}:
                self.update_task(
                    key,
                    {
                        "state": "failed",
                        "recovery_required": True,
                        "error": "Agent stopped before task completion. Review receipts and files before creating a new plan.",
                    },
                )


task_store = TaskStore()


def save_task(task_id, data):
    task_store.update_task(task_id, data)


def get_task(task_id):
    return task_store.get(task_id)
