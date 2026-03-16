"""Tests for reporting functionality."""

import json
from pathlib import Path

import pytest

from llmtest.models import (
    EvaluatorResult,
    TestResult,
    TestStatus,
    TestSuiteResult,
    TestType,
)
from llmtest.reporting import ConsoleReporter, JSONReporter


@pytest.fixture
def sample_test_result() -> TestResult:
    """Create a sample test result."""
    return TestResult(
        test_id="test-001",
        test_type=TestType.GROUNDING,
        status=TestStatus.PASS,
        input="What is the policy?",
        response="The policy states that returns are allowed within 30 days.",
        evaluator_result=EvaluatorResult(
            passed=True,
            details={"checks_passed": ["must_include"], "checks_failed": []},
            issues=[],
        ),
        error_message=None,
    )


@pytest.fixture
def sample_suite_result(sample_test_result: TestResult) -> TestSuiteResult:
    """Create a sample test suite result."""
    return TestSuiteResult(
        provider="mock",
        model="mock-model",
        total=1,
        passed=1,
        failed=0,
        errors=0,
        skipped=0,
        test_results=[sample_test_result],
    )


def test_console_reporter_initialization() -> None:
    """Test console reporter initialization."""
    reporter = ConsoleReporter()
    assert reporter is not None


def test_console_reporter_report(sample_suite_result: TestSuiteResult) -> None:
    """Test console reporter generates output."""
    reporter = ConsoleReporter()
    # Should not raise an exception
    reporter.report(sample_suite_result)


def test_json_reporter_initialization() -> None:
    """Test JSON reporter initialization."""
    reporter = JSONReporter()
    assert reporter is not None


def test_json_reporter_to_file(
    sample_suite_result: TestSuiteResult, tmp_path: Path
) -> None:
    """Test JSON reporter writes to file."""
    reporter = JSONReporter()
    output_file = tmp_path / "results.json"

    reporter.report(sample_suite_result, str(output_file))

    assert output_file.exists()

    # Verify JSON content
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["provider"] == "mock"
    assert data["model"] == "mock-model"
    assert data["summary"]["total"] == 1
    assert data["summary"]["passed"] == 1
    assert data["summary"]["pass_rate"] == 100.0
    assert len(data["tests"]) == 1
    assert data["tests"][0]["id"] == "test-001"


def test_json_reporter_to_stdout(sample_suite_result: TestSuiteResult, tmp_path: Path) -> None:
    """Test JSON reporter writes output."""
    reporter = JSONReporter()
    output_file = tmp_path / "stdout.json"
    # Should not raise an exception
    reporter.report(sample_suite_result, str(output_file))
    assert output_file.exists()


def test_json_reporter_handles_errors(tmp_path: Path) -> None:
    """Test JSON reporter handles test errors."""
    result = TestSuiteResult(
        provider="mock",
        model="mock-model",
        total=1,
        passed=0,
        failed=0,
        errors=1,
        skipped=0,
        test_results=[
            TestResult(
                test_id="error-test",
                test_type=TestType.GROUNDING,
                status=TestStatus.ERROR,
                input="Test",
                response="",
                evaluator_result=None,
                error_message="Something went wrong",
            )
        ],
    )

    reporter = JSONReporter()
    output_file = tmp_path / "errors.json"

    reporter.report(result, str(output_file))

    assert output_file.exists()

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["summary"]["errors"] == 1
    assert data["tests"][0]["error_message"] == "Something went wrong"


def test_json_serialization_complete(sample_suite_result: TestSuiteResult) -> None:
    """Test that all fields are properly serialized to JSON."""
    # Convert TestSuiteResult to dict to verify it has the right structure
    data = sample_suite_result.model_dump()

    # Verify all required fields
    assert "provider" in data
    assert "model" in data
    assert "total" in data
    assert "passed" in data
    assert "failed" in data
    assert "errors" in data
    assert "skipped" in data
    assert "test_results" in data

    # Verify test result fields
    test = data["test_results"][0]
    assert all(
        k in test
        for k in ["test_id", "test_type", "status", "input", "response", "evaluator_result"]
    )
