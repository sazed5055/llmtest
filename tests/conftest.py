"""Shared pytest fixtures for llmtest tests."""

from pathlib import Path
from typing import Dict

import pytest

from llmtest.models import TestCase, TestConfig, TestType
from llmtest.providers.mock import MockProvider


@pytest.fixture
def mock_provider() -> MockProvider:
    """Create a mock provider instance."""
    return MockProvider(model="mock-model")


@pytest.fixture
def sample_test_case() -> TestCase:
    """Create a sample test case."""
    return TestCase(
        id="test-001",
        type=TestType.GROUNDING,
        input="What is the policy?",
        must_include=["policy", "approved"],
        must_not_include=["forbidden"],
    )


@pytest.fixture
def sample_config() -> TestConfig:
    """Create a sample test configuration."""
    return TestConfig(
        provider="mock",
        model="mock-model",
        agent={"type": "prompt", "system_prompt": "You are a helpful assistant."},
        tests=[
            TestCase(
                id="test-001",
                type=TestType.GROUNDING,
                input="What is the policy?",
                must_include=["policy"],
            )
        ],
    )


@pytest.fixture
def temp_yaml_config(tmp_path: Path) -> Path:
    """Create a temporary YAML config file."""
    config_content = """provider: mock
model: mock-model

agent:
  type: prompt
  system_prompt: |
    You are a helpful assistant.

tests:
  - id: test-001
    type: grounding
    input: "What is the policy?"
    must_include:
      - "policy"
"""
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def temp_knowledge_base(tmp_path: Path) -> Dict[str, Path]:
    """Create temporary knowledge base files."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    policy_file = docs_dir / "policy.txt"
    policy_file.write_text("This is the approved policy document.")

    guide_file = docs_dir / "guide.txt"
    guide_file.write_text("This is the user guide.")

    return {"policy": policy_file, "guide": guide_file}
