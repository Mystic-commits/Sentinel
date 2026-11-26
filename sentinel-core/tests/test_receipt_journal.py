import json
from pathlib import Path

import pytest

from sentinel_core.api import receipts
from sentinel_core.api.config import settings
from sentinel_core.models.enums import ActionType
from sentinel_core.models.planner import PlanAction, PlanSchema


@pytest.fixture
def batch(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "database_url", str(tmp_path / "test.sqlite"))
    folder = tmp_path / "sample"
    folder.mkdir()
    actions = []
    for name in ("first.txt", "second.txt"):
        source = folder / name
        source.write_text(name)
        actions.append(PlanAction(
            type=ActionType.MOVE, source_path=str(source),
            destination_path=str(folder / "organized" / name), confidence=1, reason="fixture",
        ))
    return PlanSchema(task_id="test-journal", scope_path=str(folder), summary="", actions=actions)


def test_interruption_keeps_committed_progress_and_marks_uncertain_action(batch, monkeypatch):
    real_execute = receipts.execute_plan

    def interrupted(plan):
        result = real_execute(plan)
        if plan.actions[0] == batch.actions[1]:
            raise KeyboardInterrupt
        return result

    monkeypatch.setattr(receipts, "execute_plan", interrupted)
    receipts.record_start(batch)
    with pytest.raises(KeyboardInterrupt):
        receipts.run_recorded(batch, receipts.snapshot_sources(batch))

    # A history read with no writer can reconcile the abandoned receipt.
    first, second = receipts.receipt_details(batch.task_id)
    assert first["apply_state"] == "done"
    assert second["apply_state"] == "started"
    summary = receipts.history()[0]
    assert summary["state"] == "interrupted"
    assert summary["applied_count"] == summary["uncertain_count"] == 1
    assert receipts.receipt_state(batch.task_id) == "interrupted"
    with pytest.raises(ValueError, match="receipt can be undone"):
        receipts.undo_recorded(batch.task_id)
    assert all(Path(action.destination_path).exists() for action in batch.actions)


def test_partial_failure_can_restore_only_confirmed_moves(batch, monkeypatch):
    real_execute = receipts.execute_plan
    second = batch.actions[1]

    def conflict_after_first(plan):
        result = real_execute(plan)
        if plan.actions[0] == batch.actions[0]:
            Path(second.destination_path).write_text("someone else's file")
        return result

    monkeypatch.setattr(receipts, "execute_plan", conflict_after_first)
    receipts.record_start(batch)
    result = receipts.run_recorded(batch, receipts.snapshot_sources(batch))
    assert (result.successful_actions, result.failed_actions) == (1, 1)
    assert receipts.history()[0]["state"] == "partial"
    assert receipts.receipt_details(batch.task_id)[1]["apply_state"] == "pending"

    assert receipts.undo_recorded(batch.task_id).successful_actions == 1
    assert receipts.history()[0]["state"] == "undone"
    assert all(Path(action.source_path).exists() for action in batch.actions)
    assert Path(second.destination_path).read_text() == "someone else's file"


def test_active_writer_is_not_reconciled_and_second_writer_is_rejected(batch):
    receipts.record_start(batch)
    with receipts.writer():
        with receipts.database() as connection:
            connection.execute("UPDATE api_receipts SET state = 'executing'")
        assert receipts.history()[0]["state"] == "executing"
        with pytest.raises(receipts.WriterBusy):
            receipts.undo_recorded(batch.task_id)

    assert receipts.history()[0]["state"] == "interrupted"


def test_receipt_written_before_journaling_can_still_be_undone(batch):
    assert receipts.execute_plan(batch).successful_actions == 2
    legacy_identities = [receipts.identity(action.destination_path) for action in batch.actions]
    with receipts.database() as connection:
        connection.execute(
            "INSERT INTO api_receipts (task_id, state, plan, identities) VALUES (?, 'completed', ?, ?)",
            (batch.task_id, batch.model_dump_json(), json.dumps(legacy_identities)),
        )
    assert receipts.undo_recorded(batch.task_id).successful_actions == 2
    assert receipts.history()[0]["restored_count"] == 2
    assert all(Path(action.source_path).exists() for action in batch.actions)


def test_interrupted_undo_preserves_per_file_restore_evidence(batch, monkeypatch):
    receipts.record_start(batch)
    assert receipts.run_recorded(batch, receipts.snapshot_sources(batch)).successful_actions == 2
    real_execute = receipts.execute_plan

    def interrupted(plan):
        result = real_execute(plan)
        if plan.actions[0].destination_path == batch.actions[0].source_path:
            raise KeyboardInterrupt
        return result

    monkeypatch.setattr(receipts, "execute_plan", interrupted)
    with pytest.raises(KeyboardInterrupt):
        receipts.undo_recorded(batch.task_id)
    summary = receipts.history()[0]
    assert summary["state"] == "undo_interrupted"
    assert summary["restored_count"] == summary["uncertain_count"] == 1
    first, second = receipts.receipt_details(batch.task_id)
    assert (first["undo_state"], second["undo_state"]) == ("started", "done")
    assert all(Path(action.source_path).exists() for action in batch.actions)
