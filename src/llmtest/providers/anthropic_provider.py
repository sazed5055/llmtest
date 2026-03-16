"""Anthropic provider implementation."""

import os
from typing import Dict, Optional

from llmtest.providers.base import BaseProvider, ProviderError


class AnthropicProvider(BaseProvider):
    """
    Anthropic API provider.

    Requires ANTHROPIC_API_KEY environment variable.
    Supports Claude 3, Claude 3.5, and other Anthropic models.

    Context handling:
    - If context (knowledge base) is provided, it's injected into the system prompt
    - Format: "Context documents:\n\n{doc1}\n\n{doc2}\n\n{original_system_prompt}"
    """

    def __init__(self, model: str, api_key: Optional[str] = None):
        """
        Initialize Anthropic provider.

        Args:
            model: Model identifier (e.g., "claude-3-5-sonnet-20241022", "claude-3-opus-20240229")
            api_key: Optional API key. If not provided, uses ANTHROPIC_API_KEY env var

        Raises:
            ProviderError: If API key is not found
        """
        super().__init__(model)

        # Get API key
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ProviderError(
                "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Lazy import to avoid requiring anthropic for users who don't need it
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ProviderError(
                "anthropic package not installed. Install it with: "
                "pip install llmtest[anthropic] or pip install anthropic"
            )

        self.client = Anthropic(api_key=self.api_key)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        context: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Generate a response using Anthropic API.

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

        # Call Anthropic API
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.0,  # Deterministic for testing
                system=final_system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt},
                ],
            )

            # Extract text from response
            if response.content and len(response.content) > 0:
                return response.content[0].text
            return ""

        except Exception as e:
            raise ProviderError(f"Anthropic API error: {str(e)}")

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
        return "anthropic"
