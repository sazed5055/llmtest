"""HTTP provider for custom API endpoints."""

import os
from typing import Any, Dict, Optional

from llmtest.providers.base import BaseProvider, ProviderError


class HTTPProvider(BaseProvider):
    """
    Generic HTTP provider for custom API endpoints.

    Sends POST requests to a configurable endpoint.
    Supports custom request/response field mapping.

    Example YAML config:
        provider: http
        model: my-model
        http_config:
          url: http://localhost:8000/generate
          request_fields:
            system: system_prompt
            user: user_message
          response_field: text
          headers:
            Authorization: Bearer ${API_KEY}
    """

    def __init__(
        self,
        model: str,
        url: str,
        request_fields: Optional[Dict[str, str]] = None,
        response_field: str = "response",
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
    ):
        """
        Initialize HTTP provider.

        Args:
            model: Model identifier (passed in request)
            url: API endpoint URL
            request_fields: Mapping of request field names
                           (default: {"system": "system", "user": "user", "model": "model"})
            response_field: JSON path to response text in API response
                           (default: "response")
            headers: Optional HTTP headers
            timeout: Request timeout in seconds (default: 30)

        Example:
            provider = HTTPProvider(
                model="my-model",
                url="http://localhost:8000/generate",
                request_fields={"system": "system_prompt", "user": "input"},
                response_field="output.text",
                headers={"Authorization": "Bearer token"}
            )
        """
        super().__init__(model)
        self.url = url
        self.request_fields = request_fields or {
            "system": "system",
            "user": "user",
            "model": "model",
        }
        self.response_field = response_field
        self.headers = self._process_headers(headers or {})
        self.timeout = timeout

        # Lazy import requests
        try:
            import requests

            self.requests = requests
        except ImportError:
            raise ProviderError(
                "requests package not installed. "
                "Install it with: pip install requests"
            )

    def _process_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Process headers, expanding environment variables.

        Args:
            headers: Raw headers dict

        Returns:
            Processed headers with env vars expanded
        """
        processed = {}
        for key, value in headers.items():
            # Expand ${VAR_NAME} style environment variables
            if value.startswith("${") and value.endswith("}"):
                var_name = value[2:-1]
                env_value = os.getenv(var_name)
                if not env_value:
                    raise ProviderError(
                        f"Environment variable {var_name} not set (required for header {key})"
                    )
                processed[key] = env_value
            else:
                processed[key] = value
        return processed

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        context: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Generate response via HTTP POST request.

        Args:
            system_prompt: System prompt
            user_prompt: User input
            context: Optional context (injected into system prompt if provided)

        Returns:
            Generated response text

        Raises:
            ProviderError: If request fails
        """
        # Build system prompt with context if provided
        final_system_prompt = system_prompt
        if context:
            context_text = self._format_context(context)
            final_system_prompt = f"{context_text}\n\n{system_prompt}"

        # Build request body
        request_body: Dict[str, Any] = {}

        # Map fields
        if "system" in self.request_fields:
            request_body[self.request_fields["system"]] = final_system_prompt
        if "user" in self.request_fields:
            request_body[self.request_fields["user"]] = user_prompt
        if "model" in self.request_fields:
            request_body[self.request_fields["model"]] = self.model

        try:
            response = self.requests.post(
                self.url,
                json=request_body,
                headers=self.headers,
                timeout=self.timeout,
            )

            response.raise_for_status()

            # Parse response
            response_data = response.json()

            # Extract response text using field path
            return self._extract_response(response_data, self.response_field)

        except self.requests.exceptions.Timeout:
            raise ProviderError(f"Request timeout after {self.timeout}s")
        except self.requests.exceptions.ConnectionError:
            raise ProviderError(f"Failed to connect to {self.url}")
        except self.requests.exceptions.HTTPError as e:
            raise ProviderError(f"HTTP error: {e}")
        except Exception as e:
            raise ProviderError(f"HTTP provider error: {str(e)}")

    def _extract_response(self, data: Any, field_path: str) -> str:
        """
        Extract response text from JSON using dot notation.

        Args:
            data: Response JSON data
            field_path: Dot-separated path (e.g., "output.text")

        Returns:
            Extracted string

        Raises:
            ProviderError: If field not found
        """
        parts = field_path.split(".")
        current = data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                raise ProviderError(
                    f"Response field '{field_path}' not found in response"
                )

        if not isinstance(current, str):
            # Try to convert to string
            return str(current)

        return current

    def _format_context(self, context: Dict[str, str]) -> str:
        """
        Format context documents for injection.

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
        return "http"
