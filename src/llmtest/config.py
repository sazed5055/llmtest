"""Configuration loading and validation."""

from pathlib import Path
from typing import Dict, Union

import yaml
from pydantic import ValidationError

from llmtest.models import TestConfig


class ConfigError(Exception):
    """Error loading or validating configuration."""

    pass


def load_config(config_path: Union[str, Path]) -> TestConfig:
    """
    Load and validate a test configuration from YAML file.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        Validated TestConfig instance

    Raises:
        ConfigError: If file cannot be read or config is invalid
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise ConfigError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML syntax: {e}")
    except Exception as e:
        raise ConfigError(f"Error reading configuration file: {e}")

    if not isinstance(raw_config, dict):
        raise ConfigError("Configuration must be a YAML dictionary")

    try:
        config = TestConfig(**raw_config)
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            loc = " -> ".join(str(x) for x in error["loc"])
            msg = error["msg"]
            error_messages.append(f"  {loc}: {msg}")
        raise ConfigError(
            f"Configuration validation failed:\n" + "\n".join(error_messages)
        )

    return config


def load_knowledge_base(config: TestConfig, base_path: Path) -> Dict[str, str]:
    """
    Load knowledge base documents referenced in config.

    Args:
        config: Test configuration
        base_path: Base directory for resolving relative paths

    Returns:
        Dictionary mapping file paths to content

    Raises:
        ConfigError: If knowledge base files cannot be read
    """
    docs_content: Dict[str, str] = {}

    if not config.knowledge_base:
        return docs_content

    for doc_path_str in config.knowledge_base:
        doc_path = base_path / doc_path_str

        if not doc_path.exists():
            raise ConfigError(f"Knowledge base file not found: {doc_path}")

        try:
            with open(doc_path, "r", encoding="utf-8") as f:
                content = f.read()
                docs_content[doc_path_str] = content
        except Exception as e:
            raise ConfigError(f"Error reading knowledge base file {doc_path}: {e}")

    return docs_content
