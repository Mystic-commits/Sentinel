"""
test_planner_adapter.py

Tests for the Adapter Pattern implementation in the Planner module.

Covers:
    1. LLMProvider interface contract - any implementor must behave correctly.
    2. OllamaClient as a concrete Adapter - honours the interface, errors
       map correctly, health_check works.
    3. PlannerAgent decoupling - it works with ANY LLMProvider, not just
       OllamaClient. Uses a FakeLLMProvider (test double) to prove this.
    4. Backward compatibility - existing call sites that pass OllamaClient
       to PlannerAgent still work without modification.
    5. Error propagation - LLMProviderError family is raised uniformly.
"""

import json
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from sentinel_core.models.enums import FileType
from sentinel_core.models.filesystem import FileMetadata, ScanResult
from sentinel_core.models.preferences import PreferencesSchema
from sentinel_core.planner.ollama_client import (
    OllamaClient,
    OllamaClientError,
    OllamaConnectionError,
    OllamaGenerationError,
)
from sentinel_core.planner.planner_agent import PlannerAgent
from sentinel_core.planner.provider import (
    LLMConnectionError,
    LLMGenerationError,
    LLMProvider,
    LLMProviderError,
)
from sentinel_core.rules.models import RuleMatchResult

# ---------------------------------------------------------------------------
# Helpers / test doubles
# ---------------------------------------------------------------------------


class FakeLLMProvider(LLMProvider):
    """
    Minimal in-memory LLM provider for testing.
    Does NOT talk to any network. Returns canned responses.
    """

    def __init__(self, json_response: dict[str, Any] | None = None):
        self._json_response = json_response or {}
        self._generate_called_with: list[tuple] = []
        self._generate_json_called_with: list[tuple] = []

    def generate(self, prompt: str, model: str, **kwargs: Any) -> str:
        self._generate_called_with.append((prompt, model, kwargs))
        return "fake response"

    def generate_json(self, prompt: str, model: str, **kwargs: Any) -> dict[str, Any]:
        self._generate_json_called_with.append((prompt, model, kwargs))
        if self._json_response is None:
            raise LLMGenerationError("Forced failure")
        return self._json_response

    def health_check(self) -> bool:
        return True


class ErrorLLMProvider(LLMProvider):
    """A provider that always fails - for error propagation tests."""

    def generate(self, *_args: Any, **_kwargs: Any) -> str:
        raise LLMConnectionError("Cannot reach LLM service")

    def generate_json(self, *_args: Any, **_kwargs: Any) -> dict[str, Any]:
        raise LLMConnectionError("Cannot reach LLM service")

    def health_check(self) -> bool:
        return False


def _make_scan_result(root: str = "/tmp/test") -> ScanResult:
    """Build a minimal ScanResult for planner tests."""
    now = datetime.now()
    file = FileMetadata(
        path=f"{root}/report.pdf",
        name="report.pdf",
        extension=".pdf",
        size_bytes=1024,
        created_at=now,
        modified_at=now,
        file_type=FileType.DOCUMENT,
    )
    return ScanResult(root_path=root, files=[file], errors=[])


def _make_valid_plan_dict(task_id: str = "task_001", root: str = "/tmp/test") -> dict[str, Any]:
    """Return a dict that validates against PlanSchema."""
    return {
        "task_id": task_id,
        "scope_path": root,
        "folders_to_create": [f"{root}/PDFs"],
        "actions": [
            {
                "type": "move",
                "source_path": f"{root}/report.pdf",
                "destination_path": f"{root}/PDFs/report.pdf",
                "reason": "It is a PDF",
                "confidence": 0.9,
            }
        ],
        "ambiguous_files": [],
        "summary": "Moving 1 PDF to the PDFs folder.",
    }


# ---------------------------------------------------------------------------
# 1. LLMProvider interface
# ---------------------------------------------------------------------------


class TestLLMProviderInterface:
    """
    Validate that the abstract interface works as intended and that
    concrete implementations are structurally correct.
    """

    def test_llm_provider_is_abstract(self):
        """LLMProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            LLMProvider()  # type: ignore[abstract]

    def test_fake_provider_implements_interface(self):
        """FakeLLMProvider satisfies the interface without error."""
        provider: LLMProvider = FakeLLMProvider()
        assert isinstance(provider, LLMProvider)

    def test_generate_returns_string(self):
        provider = FakeLLMProvider()
        result = provider.generate("hello", "llama2")
        assert isinstance(result, str)

    def test_generate_json_returns_dict(self):
        provider = FakeLLMProvider(json_response={"key": "value"})
        result = provider.generate_json("hello", "llama2")
        assert isinstance(result, dict)
        assert result["key"] == "value"

    def test_default_health_check_returns_true(self):
        """The default health_check implementation returns True."""
        provider = FakeLLMProvider()
        assert provider.health_check() is True

    def test_error_health_check_returns_false(self):
        """An error provider correctly reports unhealthy."""
        provider = ErrorLLMProvider()
        assert provider.health_check() is False


# ---------------------------------------------------------------------------
# 2. LLMProvider error hierarchy
# ---------------------------------------------------------------------------


class TestLLMProviderErrors:
    """
    The error class hierarchy must be consistent so callers can catch
    either the base class or a specific subclass.
    """

    def test_ollama_client_error_is_llm_provider_error(self):
        err = OllamaClientError("test")
        assert isinstance(err, LLMProviderError)

    def test_ollama_connection_error_is_llm_connection_error(self):
        err = OllamaConnectionError("test")
        assert isinstance(err, LLMConnectionError)
        assert isinstance(err, LLMProviderError)
        assert isinstance(err, OllamaClientError)

    def test_ollama_generation_error_is_llm_generation_error(self):
        err = OllamaGenerationError("test")
        assert isinstance(err, LLMGenerationError)
        assert isinstance(err, LLMProviderError)
        assert isinstance(err, OllamaClientError)

    def test_catch_base_class_catches_subclass(self):
        """Callers can use a single except LLMProviderError clause."""
        with pytest.raises(LLMProviderError):
            raise OllamaConnectionError("something went wrong")

    def test_llm_generation_error_is_provider_error(self):
        with pytest.raises(LLMProviderError):
            raise LLMGenerationError("gen failed")


# ---------------------------------------------------------------------------
# 3. OllamaClient implements LLMProvider
# ---------------------------------------------------------------------------


class TestOllamaClientImplementsProvider:
    """OllamaClient must satisfy the LLMProvider interface."""

    def test_ollama_client_is_llm_provider(self):
        client = OllamaClient()
        assert isinstance(client, LLMProvider)

    def test_ollama_client_has_generate_method(self):
        client = OllamaClient()
        assert callable(getattr(client, "generate", None))

    def test_ollama_client_has_generate_json_method(self):
        client = OllamaClient()
        assert callable(getattr(client, "generate_json", None))

    def test_ollama_client_has_health_check_method(self):
        client = OllamaClient()
        assert callable(getattr(client, "health_check", None))

    def test_health_check_returns_false_when_unreachable(self):
        """health_check should return False if Ollama is not running (no network call needed)."""
        client = OllamaClient(base_url="http://127.0.0.1:9999")  # nothing runs here
        # This is a fast, purely network-level refusal - should not raise
        result = client.health_check()
        assert result is False

    def test_generate_raises_connection_error_on_bad_url(self):
        client = OllamaClient(base_url="http://127.0.0.1:9999")
        with pytest.raises(LLMProviderError):  # Catches OllamaConnectionError via base
            client.generate("hello", "llama2")

    def test_generate_json_raises_connection_error_on_bad_url(self):
        client = OllamaClient(base_url="http://127.0.0.1:9999")
        with pytest.raises(LLMProviderError):
            client.generate_json("hello", "llama2")

    def test_generate_accepts_kwargs(self):
        """generate() must accept **kwargs without TypeError (interface contract)."""
        client = OllamaClient(base_url="http://127.0.0.1:9999")
        with pytest.raises(LLMProviderError):
            # passes temperature as kwarg - should not raise TypeError
            client.generate("hello", "llama2", temperature=0.3)

    def test_generate_json_accepts_kwargs(self):
        """generate_json() must accept **kwargs without TypeError."""
        client = OllamaClient(base_url="http://127.0.0.1:9999")
        with pytest.raises(LLMProviderError):
            client.generate_json("hello", "llama2", temperature=0.1)


# ---------------------------------------------------------------------------
# 4. PlannerAgent decoupling (core Adapter Pattern test)
# ---------------------------------------------------------------------------


class TestPlannerAgentDecoupling:
    """
    PlannerAgent must work with ANY LLMProvider, not just OllamaClient.
    These tests inject a FakeLLMProvider to prove full decoupling.
    """

    def test_planner_accepts_any_llm_provider(self):
        """PlannerAgent can be constructed with FakeLLMProvider."""
        fake_provider = FakeLLMProvider()
        agent = PlannerAgent(llm_provider=fake_provider, model_name="test-model")
        assert agent.client is fake_provider

    def test_planner_uses_injected_provider_for_generation(self):
        """PlannerAgent routes generate_json calls to the injected provider."""
        plan_dict = _make_valid_plan_dict()
        fake_provider = FakeLLMProvider(json_response=plan_dict)
        agent = PlannerAgent(llm_provider=fake_provider, model_name="test-model")

        scan = _make_scan_result()
        prefs = PreferencesSchema()
        rule_match = RuleMatchResult(
            file_path=scan.files[0].path,
            matched_rule="PDF Rule",
            suggested_category="Documents",
            confidence=0.95,
        )

        result = agent.create_plan(
            task_id="task_001",
            scan_result=scan,
            rule_matches=[rule_match],
            preferences=prefs,
        )

        # Provider was called
        assert len(fake_provider._generate_json_called_with) == 1
        # Correct model was used
        _, called_model, _ = fake_provider._generate_json_called_with[0]
        assert called_model == "test-model"

        # Result is a PlanSchema
        assert result.task_id == "task_001"
        assert result.summary == "Moving 1 PDF to the PDFs folder."
        assert len(result.actions) == 1

    def test_planner_does_not_import_ollama_client_at_runtime(self):
        """
        PlannerAgent must not hold a hard reference to OllamaClient.
        We verify there is no direct mention in __init__'s annotations.
        """
        import inspect

        sig = inspect.signature(PlannerAgent.__init__)
        param = sig.parameters.get("llm_provider")
        assert param is not None, "PlannerAgent.__init__ must have llm_provider parameter"
        # The old parameter name should be gone
        assert "ollama_client" not in sig.parameters

    def test_planner_with_different_model_name(self):
        """PlannerAgent forwards the correct model name to the provider."""
        plan_dict = _make_valid_plan_dict()
        fake_provider = FakeLLMProvider(json_response=plan_dict)
        agent = PlannerAgent(llm_provider=fake_provider, model_name="mistral")

        scan = _make_scan_result()
        prefs = PreferencesSchema()
        agent.create_plan(
            task_id="task_002",
            scan_result=scan,
            rule_matches=[],
            preferences=prefs,
        )

        _, called_model, _ = fake_provider._generate_json_called_with[0]
        assert called_model == "mistral"

    def test_planner_raises_value_error_on_invalid_plan(self):
        """PlannerAgent raises ValueError when provider returns invalid schema."""
        # Provider returns a bad dict (missing required fields)
        fake_provider = FakeLLMProvider(json_response={"broken": True})
        agent = PlannerAgent(llm_provider=fake_provider)

        scan = _make_scan_result()
        prefs = PreferencesSchema()

        with pytest.raises(ValueError, match="LLM produced invalid plan schema"):
            agent.create_plan(
                task_id="task_003",
                scan_result=scan,
                rule_matches=[],
                preferences=prefs,
            )

    def test_planner_propagates_provider_errors(self):
        """PlannerAgent propagates LLMProviderError from the injected provider."""
        agent = PlannerAgent(llm_provider=ErrorLLMProvider())

        scan = _make_scan_result()
        prefs = PreferencesSchema()

        with pytest.raises(LLMProviderError):
            agent.create_plan(
                task_id="task_004",
                scan_result=scan,
                rule_matches=[],
                preferences=prefs,
            )

    def test_rule_confidence_filter_applied(self):
        """Only rule matches above MIN_RULE_CONFIDENCE are sent to the LLM."""
        plan_dict = _make_valid_plan_dict()
        fake_provider = FakeLLMProvider(json_response=plan_dict)
        agent = PlannerAgent(llm_provider=fake_provider)

        scan = _make_scan_result()
        prefs = PreferencesSchema()

        low_confidence = RuleMatchResult(
            file_path=scan.files[0].path,
            matched_rule="Weak Match",
            suggested_category="Misc",
            confidence=0.4,  # Below MIN_RULE_CONFIDENCE (0.8)
        )
        high_confidence = RuleMatchResult(
            file_path=scan.files[0].path,
            matched_rule="Strong Match",
            suggested_category="Documents",
            confidence=0.95,  # Above MIN_RULE_CONFIDENCE
        )

        agent.create_plan(
            task_id="task_005",
            scan_result=scan,
            rule_matches=[low_confidence, high_confidence],
            preferences=prefs,
        )

        # Inspect the prompt that was passed to the provider
        prompt, _, _ = fake_provider._generate_json_called_with[0]
        # "Weak Match" should NOT appear in the prompt
        assert "Weak Match" not in prompt
        # "Strong Match" should appear
        assert "Strong Match" in prompt


# ---------------------------------------------------------------------------
# 5. Backward compatibility
# ---------------------------------------------------------------------------


class TestBackwardCompatibility:
    """
    Existing code that passes OllamaClient to PlannerAgent must continue
    to work without any modification - OllamaClient IS-A LLMProvider.
    """

    def test_ollama_client_is_accepted_by_planner(self):
        """OllamaClient can be passed as llm_provider (backward compatibility)."""
        client = OllamaClient()  # No network needed for construction
        agent = PlannerAgent(llm_provider=client)
        assert agent.client is client

    def test_planner_module_exports_are_complete(self):
        """All expected names are exported from sentinel_core.planner."""
        import sentinel_core.planner as planner_pkg

        assert hasattr(planner_pkg, "LLMProvider")
        assert hasattr(planner_pkg, "LLMProviderError")
        assert hasattr(planner_pkg, "LLMConnectionError")
        assert hasattr(planner_pkg, "LLMGenerationError")
        assert hasattr(planner_pkg, "OllamaClient")
        assert hasattr(planner_pkg, "OllamaClientError")
        assert hasattr(planner_pkg, "OllamaConnectionError")
        assert hasattr(planner_pkg, "OllamaGenerationError")
        assert hasattr(planner_pkg, "PlannerAgent")

    @patch("httpx.Client.get")
    def test_ollama_client_health_check_true_when_200(self, mock_get):
        """health_check() returns True on HTTP 200."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = OllamaClient()
        assert client.health_check() is True

    @patch("httpx.Client.post")
    def test_ollama_client_generate_json_mocked(self, mock_post):
        """OllamaClient.generate_json works correctly when Ollama responds properly."""
        payload = {"key": "value"}
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": json.dumps(payload)}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = OllamaClient()
        result = client.generate_json("test prompt", "llama2")
        assert result == payload
