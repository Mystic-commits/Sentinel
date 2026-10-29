from concurrent.futures import ThreadPoolExecutor
from sentinel_core.api.memory import TaskStore
from sentinel_core.models.planner import PlanSchema


def test_reopen_preserves_plan_and_timestamp(tmp_path):
    path = tmp_path / "tasks.db"
    store = TaskStore(path)
    store.update_task(
        "one",
        {
            "state": "review",
            "plan": PlanSchema(
                task_id="one", scope_path=str(tmp_path), summary="persisted", actions=[]
            ),
        },
    )
    original = store["one"]["created_at"]
    restored = TaskStore(path)["one"]
    assert restored["plan"].summary == "persisted"
    assert restored["created_at"] == original


def test_concurrent_claim_has_one_winner(tmp_path):
    store = TaskStore(tmp_path / "tasks.db")
    store.update_task("one", {"state": "review"})

    def claim(_):
        return store.update_task("one", {"state": "executing"}, expected_state="review")

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(claim, range(8))) == 1


def test_recovery_preserves_receipts_without_replay(tmp_path):
    path = tmp_path / "tasks.db"
    store = TaskStore(path)
    store.update_task("one", {"state": "executing", "approved_actions": [0]})
    store.append_receipt("one", {"source_path": "synthetic"}, "started")
    reopened = TaskStore(path)
    reopened.recover_interrupted()
    assert reopened["one"]["state"] == "failed"
    assert reopened["one"]["recovery_required"]
    assert reopened["one"]["receipts"][0]["event"] == "started"
    assert reopened["one"]["approved_actions"] == [0]
