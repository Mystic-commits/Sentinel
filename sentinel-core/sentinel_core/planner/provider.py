"""
LLM Provider Interface (Adapter Pattern)

This module defines the abstract interface that ALL LLM backends must implement.
By depending on this abstraction, the PlannerAgent is decoupled from any specific
LLM provider (Ollama, OpenAI, Groq, Claude, etc.).

To add a new LLM backend, simply create a new class that inherits from
`LLMProvider` and implements `generate()` and `generate_json()`.

Example:
    class OpenAIProvider(LLMProvider):
        def __init__(self, api_key: str):
            ...
        def generate(self, prompt: str, model: str, **kwargs: Any) -> str:
            ...
        def generate_json(self, prompt: str, model: str, **kwargs: Any) -> Dict[str, Any]:
            ...
"""

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """
    Abstract base class (interface) for all LLM provider adapters.

    The PlannerAgent depends only on this abstraction, not on any
    concrete implementation. This enforces the Dependency Inversion Principle
    (D in SOLID) and the Adapter Pattern.

    Any class that inherits from LLMProvider and implements its abstract
    methods can be passed into PlannerAgent as a drop-in provider.
    """

    @abstractmethod
    def generate(self, prompt: str, model: str, **kwargs: Any) -> str:
        """
        Generate a free-text response from the LLM.

        Args:
            prompt: The prompt to send to the LLM.
            model: Model identifier string (e.g., "llama2", "gpt-4o").
            **kwargs: Optional provider-specific parameters (e.g., temperature).

        Returns:
            The generated text string.

        Raises:
            LLMProviderError: If the generation fails for any reason.
        """
        ...

    @abstractmethod
    def generate_json(self, prompt: str, model: str, **kwargs: Any) -> dict[str, Any]:
        """
        Generate a structured JSON response from the LLM.

        Implementations should enforce JSON-only output internally,
        including retrying or reformatting as needed.

        Args:
            prompt: The prompt to send to the LLM.
            model: Model identifier string (e.g., "llama2", "gpt-4o").
            **kwargs: Optional provider-specific parameters (e.g., temperature).

        Returns:
            A parsed Python dictionary from the LLM's JSON response.

        Raises:
            LLMProviderError: If the generation or JSON parsing fails.
        """
        ...

    def health_check(self) -> bool:
        """
        Optional: Check if the provider/service is reachable.

        Returns:
            True if the provider is healthy, False otherwise.
            Default implementation always returns True (no-op).
        """
        return True


class LLMProviderError(Exception):
    """
    Base exception for all LLM provider errors.

    All concrete provider implementations should raise this (or a
    subclass of it) so that the PlannerAgent can handle errors uniformly,
    without knowing which backend is in use.
    """

    pass


class LLMConnectionError(LLMProviderError):
    """Raised when the provider service cannot be reached."""

    pass


class LLMGenerationError(LLMProviderError):
    """Raised when the LLM fails to produce a valid response."""

    pass
