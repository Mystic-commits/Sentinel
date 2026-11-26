import asyncio

from sentinel_core.planner.evaluate import evaluate
from sentinel_core.planner.ollama_client import OllamaClient


def test_evaluation_scores_rules_without_calling_ollama(monkeypatch):
    calls = []
    monkeypatch.setattr(OllamaClient, "generate_json", lambda *args, **kwargs: calls.append(args))
    reports = {report["case"]: report for report in asyncio.run(evaluate("rules", "fixture-model"))}

    assert not calls
    assert all(
        report["actual"] == "rules" and not report["outside_scope"] and not report["duplicates"]
        for report in reports.values()
    )
    assert reports["group_by_type"]["matched"] == 2
    assert reports["already_organized"]["moves"] == []
    assert reports["custom_destination"]["matched"] == 0
