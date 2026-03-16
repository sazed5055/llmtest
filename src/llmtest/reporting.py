"""Test result reporting."""

import json
from pathlib import Path
from typing import List, Union

from llmtest.models import ComparisonResult, TestSuiteResult, TestType


class ConsoleReporter:
    """Console output reporter for test results."""

    def report(self, results: TestSuiteResult) -> None:
        """
        Print test results to console.

        Args:
            results: Test suite results to report
        """
        print(
            f"\nRunning {results.total} tests against {results.provider} / {results.model} ...\n"
        )

        for test_result in results.test_results:
            status_symbol = "✓" if test_result.status.value == "pass" else "✗"
            status_label = test_result.status.value.upper()

            print(f"[{status_label}] {test_result.test_id}")

            if test_result.status.value == "error":
                print(f"  error: {test_result.error_message}")
            elif test_result.evaluator_result:
                eval_result = test_result.evaluator_result
                if eval_result.passed:
                    print(f"  {status_symbol} All checks passed")
                else:
                    for issue in eval_result.issues:
                        print(f"  ✗ {issue}")

                # Show relevant details
                if "must_include_check" in eval_result.details:
                    check = eval_result.details["must_include_check"]
                    if check["matched"]:
                        print(f"  matched_required: {check['matched']}")
                    if check["missing"]:
                        print(f"  missing_required: {check['missing']}")

                if "must_not_include_check" in eval_result.details:
                    check = eval_result.details["must_not_include_check"]
                    if check["found"]:
                        print(f"  forbidden_found: {check['found']}")

                if "refused" in eval_result.details:
                    print(f"  refused: {eval_result.details['refused']}")

                if "potential_leakage" in eval_result.details:
                    if eval_result.details["potential_leakage"]:
                        print(f"  potential_leakage: yes")

            print()

        # Summary
        print("Summary")
        print("-------")
        print(f"Total tests: {results.total}")
        print(f"Passed: {results.passed}")
        print(f"Failed: {results.failed}")
        if results.errors > 0:
            print(f"Errors: {results.errors}")

        # Per-type pass rates
        for test_type in TestType:
            rate = results.pass_rate_by_type(test_type)
            if rate > 0 or any(r.test_type == test_type for r in results.test_results):
                print(f"{test_type.value.capitalize()} pass rate: {rate:.1f}%")

        print()


class JSONReporter:
    """JSON file reporter for test results."""

    def report(self, results: TestSuiteResult, output_path: Union[str, Path]) -> None:
        """
        Write test results to JSON file.

        Args:
            results: Test suite results to report
            output_path: Path to output JSON file
        """
        output_path = Path(output_path)

        # Convert to JSON-serializable format
        report_data = {
            "provider": results.provider,
            "model": results.model,
            "summary": {
                "total": results.total,
                "passed": results.passed,
                "failed": results.failed,
                "errors": results.errors,
                "skipped": results.skipped,
                "pass_rate": results.pass_rate,
            },
            "pass_rates_by_type": {
                test_type.value: results.pass_rate_by_type(test_type)
                for test_type in TestType
            },
            "tests": [
                {
                    "id": r.test_id,
                    "type": r.test_type.value,
                    "status": r.status.value,
                    "input": r.input,
                    "response": r.response,
                    "evaluator_result": (
                        {
                            "passed": r.evaluator_result.passed,
                            "details": r.evaluator_result.details,
                            "issues": r.evaluator_result.issues,
                        }
                        if r.evaluator_result
                        else None
                    ),
                    "error_message": r.error_message,
                }
                for r in results.test_results
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"JSON report written to: {output_path}")


class ComparisonReporter:
    """Reporter for comparison/regression results."""

    def report(self, comparisons: List[ComparisonResult]) -> None:
        """
        Print comparison results to console.

        Args:
            comparisons: List of comparison results
        """
        print(f"\nComparing model behavior across {len(comparisons)} tests ...\n")

        unchanged_count = 0
        changed_count = 0
        critical_count = 0

        for comp in comparisons:
            if not comp.changed:
                print(f"[UNCHANGED] {comp.test_id}")
                print("  baseline and candidate responses are identical")
                unchanged_count += 1
            else:
                print(f"[CHANGED] {comp.test_id}")
                print(f"  severity: {comp.severity}")
                if comp.reason:
                    print(f"  reason: {comp.reason}")
                print(f"  baseline: {comp.baseline_response[:100]}...")
                print(f"  candidate: {comp.candidate_response[:100]}...")
                changed_count += 1

                if comp.severity == "CRITICAL":
                    critical_count += 1

            print()

        # Summary
        print("Regression Summary")
        print("------------------")
        print(f"Tests compared: {len(comparisons)}")
        print(f"Unchanged: {unchanged_count}")
        print(f"Changed: {changed_count}")
        print(f"Critical regressions: {critical_count}")
        print(f"Safe to promote: {'NO' if critical_count > 0 else 'YES'}")
        print()
