"""Base provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class ProviderError(Exception):
    """Error during provider operation."""

    pass


class BaseProvider(ABC):
    """
    Base class for LLM provider implementations.

    Providers handle communication with specific LLM backends
    (OpenAI, Anthropic, custom HTTP endpoints, etc.)
    """

    def __init__(self, model: str):
        """
        Initialize provider.

        Args:
            model: Model identifier to use
        """
        self.model = model

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        context: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Generate a response from the LLM.

        Args:
            system_prompt: System prompt/instructions for the LLM
            user_prompt: User input/question to send to the LLM
            context: Optional knowledge base documents as dict mapping
                     file paths to content. Providers may choose to:
                     - Inject context into the system prompt
                     - Include context as a separate message
                     - Ignore context entirely (e.g., for mock providers)
                     Real providers should document their context handling.

        Returns:
            Generated response text

        Raises:
            ProviderError: If generation fails
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'openai', 'anthropic', 'mock')."""
        pass
