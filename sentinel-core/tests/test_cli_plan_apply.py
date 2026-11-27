import re

import pytest
from typer.testing import CliRunner

from sentinel_core.api.config import settings
from sentinel_core.cli.main import app

runner = CliRunner()


@pytest.fixture
def sample(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "database_url", str(tmp_path / "sentinel.db"))
    folder = tmp_path / "sample"
    folder.mkdir()
    (folder / "invoice.txt").write_text("invoice")
    (folder / "holiday.jpg").write_text("image")
    return folder


def create_plan(folder):
    result = runner.invoke(app, ["plan", str(folder), "--rules-only"])
    assert result.exit_code == 0, result.output
    return re.search(r"Task (task-[0-9a-f-]+)", result.output)[1]


def test_cli_preview_apply_subset_and_undo(sample):
    task_id = create_plan(sample)
    preview = runner.invoke(app, ["apply", task_id, "--dry-run", "--action", "1"])
    assert preview.exit_code == 0, preview.output
    assert "Dry run. No files moved." in preview.output
    assert len(list(sample.iterdir())) == 2
    cancelled = runner.invoke(app, ["apply", task_id, "--action", "1"], input="n\n")
    assert cancelled.exit_code == 0 and "Cancelled" in cancelled.output
    applied = runner.invoke(app, ["apply", task_id, "--action", "1", "--yes"])
    assert applied.exit_code == 0, applied.output
    assert len([file for file in sample.iterdir() if file.is_file()]) == 1
    assert runner.invoke(app, ["apply", task_id, "--yes"]).exit_code != 0
    undone = runner.invoke(app, ["undo", task_id, "--yes"])
    assert undone.exit_code == 0, undone.output
    assert (sample / "invoice.txt").read_text() == "invoice"
    assert (sample / "holiday.jpg").read_text() == "image"


def test_cli_blocks_stale_plan(sample):
    task_id = create_plan(sample)
    (sample / "invoice.txt").write_text("edited after review")
    result = runner.invoke(app, ["apply", task_id, "--yes"])
    assert result.exit_code != 0
    assert "changed after the plan was prepared" in result.output
    assert len(list(sample.iterdir())) == 2


def test_cli_no_save_does_not_write_plan(sample):
    result = runner.invoke(app, ["plan", str(sample), "--rules-only", "--no-save"])
    assert result.exit_code == 0, result.output
    assert "Preview saved plan" not in result.output
    assert not (sample.parent / "sentinel.db").exists()


def test_clean_command_reviews_then_applies_only_after_confirmation(sample):
    args = ["clean-pc", "--location", str(sample)]
    preview = runner.invoke(app, args)
    assert preview.exit_code == 0 and "Preview saved plan" in preview.output
    cancelled = runner.invoke(app, [*args, "--execute"], input="n\n")
    assert cancelled.exit_code == 0 and "Cancelled" in cancelled.output
    assert (sample / "invoice.txt").is_file()
    applied = runner.invoke(app, [*args, "--execute"], input="y\n")
    assert applied.exit_code == 0 and "Applied 2 changes" in applied.output
    assert not (sample / "invoice.txt").exists()


def test_verbose_scan_lists_real_files(sample):
    result = runner.invoke(app, ["scan", str(sample), "--verbose"])
    assert result.exit_code == 0
    assert "holiday.jpg" in result.output and "invoice.txt" in result.output


def test_ask_uses_local_provider(sample, monkeypatch):
    from sentinel_core.planner.ollama_client import OllamaClient

    def generate(_self, prompt, model):
        assert str(sample) in prompt and "Where" in prompt
        assert model == "llama2"
        return "Provider response"

    monkeypatch.setattr(OllamaClient, "generate", generate)
    result = runner.invoke(app, ["ask", "Where should invoices go?", "--path", str(sample)])
    assert result.exit_code == 0 and "Provider response" in result.output
