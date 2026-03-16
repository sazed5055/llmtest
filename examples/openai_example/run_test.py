#!/usr/bin/env python
"""Example: Running llmtest with OpenAI provider.

Requirements:
- Set OPENAI_API_KEY environment variable
- Install: pip install llmtest[openai]

Usage:
    export OPENAI_API_KEY=your-api-key
    python run_test.py
"""

import os
import sys

from llmtest import TestRunner
from llmtest.reporting import ConsoleReporter, JSONReporter

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY environment variable not set")
    print("\nSet it with:")
    print("  export OPENAI_API_KEY=your-api-key-here")
    sys.exit(1)

# Try to import OpenAI provider
try:
    from llmtest.providers.openai_provider import OpenAIProvider
except ImportError:
    print("ERROR: openai package not installed")
    print("\nInstall it with:")
    print("  pip install llmtest[openai]")
    print("  # or")
    print("  pip install openai")
    sys.exit(1)

# Create OpenAI provider
print("Initializing OpenAI provider...")
provider = OpenAIProvider(model="gpt-4o-mini")

# Create runner
runner = TestRunner(provider)

# Run tests from YAML file
print("=" * 70)
print("Running llmtest with OpenAI")
print("=" * 70)

results = runner.run_from_file("llmtest.yaml")

# Print results to console
reporter = ConsoleReporter()
reporter.report(results)

# Save to JSON
json_reporter = JSONReporter()
json_reporter.report(results, "test_results.json")

print("\n" + "=" * 70)
print(f"Overall pass rate: {results.pass_rate:.1f}%")
print("=" * 70)
