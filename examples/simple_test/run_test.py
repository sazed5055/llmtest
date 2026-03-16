#!/usr/bin/env python
"""Example: How to run llmtest programmatically."""

from llmtest import TestRunner
from llmtest.providers.mock import MockProvider
from llmtest.reporting import ConsoleReporter, JSONReporter

# Create mock provider
provider = MockProvider()

# Create runner
runner = TestRunner(provider)

# Run tests from YAML file
print("=" * 70)
print("Running llmtest example")
print("=" * 70)

results = runner.run_from_file("test_config.yaml")

# Print results to console
reporter = ConsoleReporter()
reporter.report(results)

# Also save to JSON
json_reporter = JSONReporter()
json_reporter.report(results, "test_results.json")

print("\n" + "=" * 70)
print(f"Overall pass rate: {results.pass_rate:.1f}%")
print("=" * 70)
