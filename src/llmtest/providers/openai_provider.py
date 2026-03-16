"""OpenAI provider implementation."""

import os
from typing import Dict, Optional

from llmtest.providers.base import BaseProvider, ProviderError


class OpenAIProvider(BaseProvider):
    """
    OpenAI API provider.

    Requires OPENAI_API_KEY environment variable.
    Supports GPT-4, GPT-3.5, and other OpenAI models.

    Context handling:
    - If context (knowledge base) is provided, it's injected into the system prompt
    - Format: "Context documents:\n\n{doc1}\n\n{doc2}\n\n{original_system_prompt}"
    """

    def __init__(self, model: str, api_key: Optional[str] = None):
        """
        Initialize OpenAI provider.

        Args:
            model: Model identifier (e.g., "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo")
            api_key: Optional API key. If not provided, uses OPENAI_API_KEY env var

        Raises:
            ProviderError: If API key is not found
        """
        super().__init__(model)

        # Get API key
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ProviderError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Lazy import to avoid requiring openai for users who don't need it
        try:
            from openai import OpenAI
        except ImportError:
            raise ProviderError(
                "openai package not installed. Install it with: "
                "pip install llmtest[openai] or pip install openai"
            )

        self.client = OpenAI(api_key=self.api_key)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        context: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Generate a response using OpenAI API.

        Args:
            system_prompt: System prompt/instructions
            user_prompt: User input/question
            context: Optional knowledge base documents (injected into system prompt)

        Returns:
            Generated response text

        Raises:
            ProviderError: If API call fails
        """
        # Build system prompt with context if provided
        final_system_prompt = system_prompt
        if context:
            context_text = self._format_context(context)
            final_system_prompt = f"{context_text}\n\n{system_prompt}"

        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": final_system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,  # Deterministic for testing
            )

            return response.choices[0].message.content or ""

        except Exception as e:
            raise ProviderError(f"OpenAI API error: {str(e)}")

    def _format_context(self, context: Dict[str, str]) -> str:
        """
        Format context documents for injection into system prompt.

        Args:
            context: Dictionary mapping file paths to content

        Returns:
            Formatted context string
        """
        if not context:
            return ""

        context_parts = ["Context documents:"]
        for path, content in context.items():
            context_parts.append(f"\n--- {path} ---\n{content}")

        return "\n".join(context_parts)

    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "openai"
