"""Grounding test evaluator."""

from typing import List, Optional

from llmtest.models import EvaluatorResult, TestCase
from llmtest.utils.text import contains_all_phrases, contains_any_phrase, find_matching_phrases


class GroundingEvaluator:
    """
    Evaluator for grounding tests.

    Checks whether responses are properly grounded in provided context,
    using phrase matching heuristics.
    """

    # Patterns indicating "I don't know" responses
    UNKNOWN_PATTERNS = [
        "i do not know",
        "i don't know",
        "i am not sure",
        "i'm not sure",
        "not in the approved documents",
        "not in the documents",
        "not available in",
        "i cannot determine",
        "cannot determine based on",
        "i don't have information",
        "do not have information",
        "information is not available",
        "not mentioned in",
    ]

    def evaluate(self, test_case: TestCase, response: str) -> EvaluatorResult:
        """
        Evaluate a grounding test.

        Args:
            test_case: Test case definition
            response: LLM response to evaluate

        Returns:
            Evaluation result with pass/fail and details
        """
        details = {}
        issues = []
        checks_passed = []
        checks_failed = []

        # Check must_include phrases
        if test_case.must_include:
            matched = find_matching_phrases(response, test_case.must_include)
            missing = [p for p in test_case.must_include if p not in matched]

            details["must_include_check"] = {
                "required": test_case.must_include,
                "matched": matched,
                "missing": missing,
            }

            if missing:
                checks_failed.append("must_include")
                issues.append(f"Missing required phrases: {missing}")
            else:
                checks_passed.append("must_include")

        # Check must_not_include phrases
        if test_case.must_not_include:
            found = find_matching_phrases(response, test_case.must_not_include)

            details["must_not_include_check"] = {
                "forbidden": test_case.must_not_include,
                "found": found,
            }

            if found:
                checks_failed.append("must_not_include")
                issues.append(f"Found forbidden phrases: {found}")
            else:
                checks_passed.append("must_not_include")

        # Check expected_behavior
        if test_case.expected_behavior:
            behavior_passed = self._check_expected_behavior(
                test_case.expected_behavior, response
            )

            details["expected_behavior_check"] = {
                "expected": test_case.expected_behavior,
                "matched": behavior_passed,
            }

            if behavior_passed:
                checks_passed.append("expected_behavior")
            else:
                checks_failed.append("expected_behavior")
                issues.append(
                    f"Response does not match expected behavior: {test_case.expected_behavior}"
                )

        # Overall pass requires all checks to pass
        passed = len(checks_failed) == 0

        details["checks_passed"] = checks_passed
        details["checks_failed"] = checks_failed

        return EvaluatorResult(passed=passed, details=details, issues=issues)

    def _check_expected_behavior(self, expected: str, response: str) -> bool:
        """
        Check if response matches expected behavior.

        Args:
            expected: Expected behavior description
            response: LLM response

        Returns:
            True if response matches expected behavior
        """
        expected_lower = expected.lower().strip()

        # Handle "say unknown if not in docs" pattern
        if "unknown" in expected_lower or "don't know" in expected_lower:
            return contains_any_phrase(response, self.UNKNOWN_PATTERNS)

        # Could add more expected behavior patterns here in future
        return False
