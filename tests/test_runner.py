"""Tests for test runner."""

from pathlib import Path

import pytest

from llmtest.models import TestCase, TestConfig, TestType
from llmtest.providers.mock import MockProvider
from llmtest.runner import TestRunner


def test_runner_initialization(mock_provider: MockProvider) -> None:
    """Test runner initialization."""
    runner = TestRunner(mock_provider)
    assert runner.provider == mock_provider


def test_run_single_test(mock_provider: MockProvider) -> None:
    """Test running a single test case via run() method."""
    runner = TestRunner(mock_provider)
    config = TestConfig(
        provider="mock",
        model="mock-model",
        agent={"type": "prompt", "system_prompt": "You are helpful."},
        tests=[
            TestCase(
                id="test-001",
                type=TestType.GROUNDING,
                input="What is the policy?",
                must_include=["policy"],
            )
        ],
    )

    results = runner.run(config)

    assert results.total == 1
    assert len(results.test_results) == 1
    test_result = results.test_results[0]
    assert test_result.test_id == "test-001"
    assert test_result.test_type == TestType.GROUNDING
    assert test_result.input == "What is the policy?"
    assert test_result.response is not None
    assert test_result.status.value in ["pass", "fail", "error"]
    assert test_result.evaluator_result is not None


def test_run_suite(mock_provider: MockProvider, sample_config: TestConfig) -> None:
    """Test running a test suite."""
    runner = TestRunner(mock_provider)
    results = runner.run(sample_config)

    assert results.provider == "mock"
    assert results.model == "mock-model"
    assert results.total == 1
    assert results.passed + results.failed + results.errors == 1
    assert len(results.test_results) == 1


def test_run_from_file(mock_provider: MockProvider, temp_yaml_config: Path) -> None:
    """Test running tests from a YAML file."""
    runner = TestRunner(mock_provider)
    results = runner.run_from_file(temp_yaml_config)

    assert results.provider == "mock"
    assert results.total >= 1
    assert len(results.test_results) >= 1


def test_run_with_knowledge_base(
    mock_provider: MockProvider, temp_knowledge_base: dict
) -> None:
    """Test running tests with knowledge base."""
    config_dir = temp_knowledge_base["policy"].parent.parent
    docs_dir = temp_knowledge_base["policy"].parent

    config_content = f"""provider: mock
model: mock-model

agent:
  type: prompt
  system_prompt: "Answer from docs only."

knowledge_base:
  - docs/{temp_knowledge_base['policy'].name}

tests:
  - id: test-kb
    type: grounding
    input: "What is the policy?"
    must_include:
      - "policy"
"""
    config_file = config_dir / "config_kb.yaml"
    config_file.write_text(config_content)

    runner = TestRunner(mock_provider)
    results = runner.run_from_file(config_file)

    assert results.total == 1
    assert len(results.test_results) == 1


def test_compare_mode(mock_provider: MockProvider, tmp_path: Path) -> None:
    """Test compare mode for regression detection."""
    # Create baseline config
    baseline_content = """provider: mock
model: mock-v1

agent:
  type: prompt
  system_prompt: "You are helpful."

tests:
  - id: test-001
    type: grounding
    input: "What is the policy?"
    must_include:
      - "policy"
"""
    baseline_file = tmp_path / "baseline.yaml"
    baseline_file.write_text(baseline_content)

    # Create candidate config
    candidate_content = """provider: mock
model: mock-v2

agent:
  type: prompt
  system_prompt: "You are very helpful."

tests:
  - id: test-001
    type: grounding
    input: "What is the policy?"
    must_include:
      - "policy"
"""
    candidate_file = tmp_path / "candidate.yaml"
    candidate_file.write_text(candidate_content)

    runner = TestRunner(mock_provider)
    comparisons = runner.compare_from_files(baseline_file, candidate_file)

    assert len(comparisons) >= 1
    assert all(hasattr(c, "test_id") for c in comparisons)
    assert all(hasattr(c, "changed") for c in comparisons)
    assert all(hasattr(c, "severity") for c in comparisons)


def test_run_test_error_handling(mock_provider: MockProvider) -> None:
    """Test error handling in test execution."""
    runner = TestRunner(mock_provider)

    # Create a config with potentially problematic input
    config = TestConfig(
        provider="mock",
        model="mock-model",
        agent={"type": "prompt", "system_prompt": "Test"},
        tests=[
            TestCase(
                id="error-test",
                type=TestType.GROUNDING,
                input="Test input",
                must_include=["test"],
            )
        ],
    )

    results = runner.run(config)

    # Should handle gracefully
    assert results.total == 1
    assert len(results.test_results) == 1
    assert results.test_results[0].test_id == "error-test"
    assert results.test_results[0].status.value in ["pass", "fail", "error"]


def test_pass_rate_calculation(mock_provider: MockProvider) -> None:
    """Test pass rate calculation."""
    config = TestConfig(
        provider="mock",
        model="mock-model",
        agent={"type": "prompt", "system_prompt": "Test"},
        tests=[
            TestCase(
                id=f"test-{i}",
                type=TestType.GROUNDING,
                input="Test",
                must_include=["test"],
            )
            for i in range(5)
        ],
    )

    runner = TestRunner(mock_provider)
    results = runner.run(config)

    assert results.total == 5
    assert 0 <= results.pass_rate <= 100
    assert results.pass_rate == (results.passed / results.total * 100)


def test_pass_rates_by_type(mock_provider: MockProvider) -> None:
    """Test pass rate calculation by test type."""
    config = TestConfig(
        provider="mock",
        model="mock-model",
        agent={"type": "prompt", "system_prompt": "Test"},
        tests=[
            TestCase(id="g1", type=TestType.GROUNDING, input="Test", must_include=["test"]),
            TestCase(id="g2", type=TestType.GROUNDING, input="Test", must_include=["test"]),
            TestCase(id="i1", type=TestType.INJECTION, input="Test", must_refuse=True),
            TestCase(id="s1", type=TestType.SAFETY, input="Test", must_refuse=True),
        ],
    )

    runner = TestRunner(mock_provider)
    results = runner.run(config)

    # Verify we can calculate pass rates by type
    grounding_rate = results.pass_rate_by_type(TestType.GROUNDING)
    injection_rate = results.pass_rate_by_type(TestType.INJECTION)
    safety_rate = results.pass_rate_by_type(TestType.SAFETY)

    assert 0 <= grounding_rate <= 100
    assert 0 <= injection_rate <= 100
    assert 0 <= safety_rate <= 100
