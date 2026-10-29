import json
import httpx
import logging
from typing import Any, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from sentinel_core.planner.provider import (
    LLMProvider,
    LLMProviderError,
    LLMConnectionError,
    LLMGenerationError,
)

# Configure logger
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Ollama-specific error aliases (kept for backward compatibility)
# ---------------------------------------------------------------------------


class OllamaClientError(LLMProviderError):
    """Base exception for Ollama client errors. Inherits from LLMProviderError."""

    pass


class OllamaConnectionError(OllamaClientError, LLMConnectionError):
    """Failed to connect to Ollama."""

    pass


class OllamaGenerationError(OllamaClientError, LLMGenerationError):
    """Error during generation."""

    pass


class OllamaClient(LLMProvider):
    """
    Concrete Adapter: implements LLMProvider using the Ollama REST API.

    This is one specific implementation of the LLMProvider interface.
    The PlannerAgent does NOT import this class directly - it receives an
    LLMProvider instance via constructor injection (Dependency Inversion).
    """

    def __init__(self, base_url: str = "http://localhost:11434", timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout
        from urllib.parse import urlparse

        parsed = urlparse(base_url)
        if (
            parsed.scheme != "http"
            or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}
            or parsed.username
            or parsed.password
        ):
            raise ValueError("Ollama must use a local loopback HTTP address")
        self.client = httpx.Client(
            base_url=base_url, timeout=timeout, trust_env=False, follow_redirects=False
        )

    def health_check(self) -> bool:
        """Checks if Ollama instance is reachable."""
        try:
            response = self.client.get("/")
            return response.status_code == 200
        except httpx.RequestError:
            return False

    def generate(self, prompt: str, model: str, temperature: float = 0.7, **kwargs: Any) -> str:
        """
        Generates text completion.
        """
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature},
            }
            response = self.client.post("/api/generate", json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except httpx.RequestError as e:
            raise OllamaConnectionError(f"Connection error: {e}")
        except httpx.HTTPStatusError as e:
            raise OllamaGenerationError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise OllamaGenerationError(f"Unexpected error: {e}")

    @retry(
        stop=stop_after_attempt(3),  # 1 initial + 2 retries
        wait=wait_fixed(1),
        retry=retry_if_exception_type((json.JSONDecodeError, OllamaGenerationError)),
        reraise=True,
    )
    def generate_json(
        self, prompt: str, model: str, temperature: float = 0.2, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generates structured JSON output. Retries if output is not valid JSON.
        """
        prompt_with_instruction = f"{prompt}\n\nIMPORTANT: Respond ONLY with valid JSON."

        try:
            payload = {
                "model": model,
                "prompt": prompt_with_instruction,
                "format": kwargs.get("schema", "json"),
                "think": False,
                "stream": False,
                "options": {"temperature": temperature},
            }

            response = self.client.post("/api/generate", json=payload)
            response.raise_for_status()

            raw_response = response.json().get("response", "")

            try:
                parsed = json.loads(raw_response)
                if not isinstance(parsed, dict):
                    raise OllamaGenerationError("Expected a JSON object")
                return parsed
            except json.JSONDecodeError:
                logger.warning("Invalid JSON received from Ollama")
                raise  # Triggers retry

        except httpx.RequestError as e:
            raise OllamaConnectionError(f"Connection error: {e}")
        except httpx.HTTPStatusError as e:
            raise OllamaGenerationError(f"HTTP error {e.response.status_code}: {e.response.text}")

    def close(self):
        self.client.close()
