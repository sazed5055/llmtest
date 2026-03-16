"""Tests for config loading and validation."""

from pathlib import Path

import pytest

from llmtest.config import ConfigError, load_config, load_knowledge_base
from llmtest.models import TestType


def test_load_valid_config(temp_yaml_config: Path) -> None:
    """Test loading a valid YAML configuration."""
    config = load_config(temp_yaml_config)

    assert config.provider == "mock"
    assert config.model == "mock-model"
    assert config.agent.type.value == "prompt"
    assert "helpful assistant" in config.agent.system_prompt
    assert len(config.tests) == 1
    assert config.tests[0].id == "test-001"
    assert config.tests[0].type == TestType.GROUNDING


def test_load_nonexistent_config() -> None:
    """Test loading a config file that doesn't exist."""
    with pytest.raises(ConfigError, match="Configuration file not found"):
        load_config(Path("/nonexistent/config.yaml"))


def test_load_invalid_yaml(tmp_path: Path) -> None:
    """Test loading an invalid YAML file."""
    invalid_file = tmp_path / "invalid.yaml"
    invalid_file.write_text("invalid: yaml: content:")

    with pytest.raises(ConfigError):
        load_config(invalid_file)


def test_load_missing_required_fields(tmp_path: Path) -> None:
    """Test loading a config with missing required fields."""
    config_file = tmp_path / "incomplete.yaml"
    config_file.write_text("provider: mock\n")  # Missing model, agent, tests

    with pytest.raises(ConfigError, match="Configuration validation failed"):
        load_config(config_file)


def test_load_knowledge_base(temp_knowledge_base: dict, tmp_path: Path) -> None:
    """Test loading knowledge base documents."""
    # Get docs directory path
    docs_dir = temp_knowledge_base["policy"].parent

    # Create config with knowledge base (using relative paths from parent of docs)
    config_content = f"""provider: mock
model: mock-model

agent:
  type: prompt
  system_prompt: "Test"

knowledge_base:
  - docs/{temp_knowledge_base['policy'].name}
  - docs/{temp_knowledge_base['guide'].name}

tests:
  - id: test-001
    type: grounding
    input: "Test"
"""
    config_file = docs_dir.parent / "config.yaml"
    config_file.write_text(config_content)

    config = load_config(config_file)
    docs = load_knowledge_base(config, config_file.parent)

    assert len(docs) == 2
    assert any("approved policy" in content for content in docs.values())
    assert any("user guide" in content for content in docs.values())


def test_load_knowledge_base_missing_file(sample_config: "TestConfig", tmp_path: Path) -> None:
    """Test loading knowledge base with missing file."""
    sample_config.knowledge_base = ["nonexistent.txt"]

    with pytest.raises(ConfigError, match="Knowledge base file not found"):
        load_knowledge_base(sample_config, tmp_path)


def test_load_knowledge_base_none(sample_config: "TestConfig", tmp_path: Path) -> None:
    """Test loading with no knowledge base."""
    sample_config.knowledge_base = None
    docs = load_knowledge_base(sample_config, tmp_path)
    assert docs == {}
