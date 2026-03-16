"""Test runner implementation."""

from pathlib import Path
from typing import Dict, List, Optional, Union

from llmtest.config import load_config, load_knowledge_base
from llmtest.evaluators.grounding import GroundingEvaluator
from llmtest.evaluators.injection import InjectionEvaluator
from llmtest.evaluators.regression import RegressionEvaluator
from llmtest.evaluators.safety import SafetyEvaluator
from llmtest.models import (
    ComparisonResult,
    EvaluatorResult,
    TestCase,
    TestConfig,
    TestResult,
    TestStatus,
    TestSuiteResult,
    TestType,
)
from llmtest.providers.base import BaseProvider, ProviderError


class TestRunner:
    """
    Core test runner for executing test suites.

    Coordinates provider calls, evaluator execution, and result collection.
    """

    def __init__(self, provider: BaseProvider):
        """
        Initialize test runner.

        Args:
            provider: LLM provider to use for test execution
        """
        self.provider = provider
        self.grounding_evaluator = GroundingEvaluator()
        self.injection_evaluator = InjectionEvaluator()
        self.safety_evaluator = SafetyEvaluator()
        self.regression_evaluator = RegressionEvaluator()

    def run_from_file(self, config_path: Union[str, Path]) -> TestSuiteResult:
        """
        Run tests from a configuration file.

        Args:
            config_path: Path to YAML configuration file

        Returns:
            Test suite results
        """
        config_path = Path(config_path)
        config = load_config(config_path)

        # Load knowledge base documents
        base_path = config_path.parent
        docs_content = load_knowledge_base(config, base_path)

        return self.run(config, docs_content)

    def run(
        self, config: TestConfig, docs_content: Optional[Dict[str, str]] = None
    ) -> TestSuiteResult:
        """
        Run a test suite.

        Args:
            config: Test configuration
            docs_content: Optional knowledge base document content

        Returns:
            Test suite results
        """
        test_results = []

        for test_case in config.tests:
            result = self._run_test(test_case, config, docs_content or {})
            test_results.append(result)

        # Compute summary statistics
        passed = sum(1 for r in test_results if r.status == TestStatus.PASS)
        failed = sum(1 for r in test_results if r.status == TestStatus.FAIL)
        errors = sum(1 for r in test_results if r.status == TestStatus.ERROR)
        skipped = sum(1 for r in test_results if r.status == TestStatus.SKIPPED)

        return TestSuiteResult(
            provider=self.provider.provider_name,
            model=self.provider.model,
            total=len(test_results),
            passed=passed,
            failed=failed,
            errors=errors,
            skipped=skipped,
            test_results=test_results,
        )

    def _run_test(
        self, test_case: TestCase, config: TestConfig, docs_content: Dict[str, str]
    ) -> TestResult:
        """
        Run a single test case.

        Args:
            test_case: Test case to execute
            config: Test configuration
            docs_content: Knowledge base document content

        Returns:
            Test result
        """
        try:
            # Generate response from provider
            response = self.provider.generate(
                system_prompt=config.agent.system_prompt,
                user_prompt=test_case.input,
                context=docs_content if docs_content else None,
            )

            # Evaluate response
            evaluator_result = self._evaluate(test_case, response)

            # Determine status
            status = TestStatus.PASS if evaluator_result.passed else TestStatus.FAIL

            return TestResult(
                test_id=test_case.id,
                test_type=test_case.type,
                status=status,
                input=test_case.input,
                response=response,
                evaluator_result=evaluator_result,
            )

        except ProviderError as e:
            return TestResult(
                test_id=test_case.id,
                test_type=test_case.type,
                status=TestStatus.ERROR,
                input=test_case.input,
                error_message=f"Provider error: {str(e)}",
            )
        except Exception as e:
            return TestResult(
                test_id=test_case.id,
                test_type=test_case.type,
                status=TestStatus.ERROR,
                input=test_case.input,
                error_message=f"Unexpected error: {str(e)}",
            )

    def _evaluate(self, test_case: TestCase, response: str) -> EvaluatorResult:
        """
        Evaluate a test response using the appropriate evaluator.

        Args:
            test_case: Test case definition
            response: LLM response to evaluate

        Returns:
            Evaluation result
        """
        if test_case.type == TestType.GROUNDING:
            return self.grounding_evaluator.evaluate(test_case, response)
        elif test_case.type == TestType.INJECTION:
            return self.injection_evaluator.evaluate(test_case, response)
        elif test_case.type == TestType.SAFETY:
            return self.safety_evaluator.evaluate(test_case, response)
        elif test_case.type == TestType.REGRESSION:
            # Regression tests require baseline comparison (compare mode)
            # Skip with clear message when run in normal mode
            return EvaluatorResult(
                passed=False,
                details={"skipped_reason": "regression tests require compare mode"},
                issues=["Regression test cannot be evaluated in normal run mode"],
            )
        else:
            raise ValueError(f"Unknown test type: {test_case.type}")

    def compare(
        self,
        baseline_config: TestConfig,
        candidate_config: TestConfig,
        baseline_docs: Optional[Dict[str, str]] = None,
        candidate_docs: Optional[Dict[str, str]] = None,
    ) -> List[ComparisonResult]:
        """
        Compare baseline and candidate test runs.

        Args:
            baseline_config: Baseline test configuration
            candidate_config: Candidate test configuration
            baseline_docs: Optional baseline knowledge base documents
            candidate_docs: Optional candidate knowledge base documents

        Returns:
            List of comparison results
        """
        # Find matching test IDs
        baseline_tests = {test.id: test for test in baseline_config.tests}
        candidate_tests = {test.id: test for test in candidate_config.tests}

        common_ids = set(baseline_tests.keys()) & set(candidate_tests.keys())

        comparison_results = []

        for test_id in common_ids:
            baseline_test = baseline_tests[test_id]
            candidate_test = candidate_tests[test_id]

            # Generate responses from both configs
            baseline_response = self.provider.generate(
                system_prompt=baseline_config.agent.system_prompt,
                user_prompt=baseline_test.input,
                context=baseline_docs,
            )

            candidate_response = self.provider.generate(
                system_prompt=candidate_config.agent.system_prompt,
                user_prompt=candidate_test.input,
                context=candidate_docs,
            )

            # Compare responses
            comparison = self.regression_evaluator.compare(
                baseline_test, baseline_response, candidate_response
            )
            comparison_results.append(comparison)

        return comparison_results

    def compare_from_files(
        self, baseline_path: Union[str, Path], candidate_path: Union[str, Path]
    ) -> List[ComparisonResult]:
        """
        Compare baseline and candidate configurations from files.

        Args:
            baseline_path: Path to baseline YAML configuration
            candidate_path: Path to candidate YAML configuration

        Returns:
            List of comparison results
        """
        baseline_path = Path(baseline_path)
        candidate_path = Path(candidate_path)

        # Load configurations
        baseline_config = load_config(baseline_path)
        candidate_config = load_config(candidate_path)

        # Load knowledge bases
        baseline_docs = load_knowledge_base(baseline_config, baseline_path.parent)
        candidate_docs = load_knowledge_base(candidate_config, candidate_path.parent)

        return self.compare(baseline_config, candidate_config, baseline_docs, candidate_docs)
