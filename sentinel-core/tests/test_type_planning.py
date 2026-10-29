from unittest.mock import Mock
import pytest
from sentinel_core.cleanpc.pipeline import CleanPCPipeline
from sentinel_core.safety import SafetyValidator
from sentinel_core.executor import Executor


@pytest.mark.asyncio
async def test_type_rules_do_not_call_model_or_change_files(tmp_path):
    (tmp_path / "notes.txt").write_text("synthetic")
    nested = tmp_path / "Already organized"
    nested.mkdir()
    (nested / "nested.txt").write_text("leave alone")
    (tmp_path / "script.py").write_text("pass")
    planner = Mock()
    result = await CleanPCPipeline(planner, SafetyValidator(), Executor()).scan_and_plan(
        "test", [str(tmp_path)], planning_strategy="file_types"
    )
    planner.create_plan.assert_not_called()
    assert (tmp_path / "notes.txt").read_text() == "synthetic"
    assert all("Already organized" not in action.source_path for action in result["plan"].actions)
    assert all(not action.source_path.endswith("script.py") for action in result["plan"].actions)
    assert all(action.type == "move" for action in result["plan"].actions)
    assert any(
        action.destination_path == str(tmp_path / "Documents" / "notes.txt")
        for action in result["plan"].actions
    )
    assert not result["summary"]["planning_warning"]


@pytest.mark.asyncio
async def test_type_rules_leave_collisions_unchanged(tmp_path):
    (tmp_path / "notes.txt").write_text("new")
    (tmp_path / "Documents").mkdir()
    (tmp_path / "Documents" / "notes.txt").write_text("existing")
    result = await CleanPCPipeline(Mock(), SafetyValidator(), Executor()).scan_and_plan(
        "test", [str(tmp_path)], planning_strategy="file_types"
    )
    assert result["plan"].actions == []
    assert len(result["plan"].ambiguous_files) == 1
    assert (tmp_path / "Documents" / "notes.txt").read_text() == "existing"
