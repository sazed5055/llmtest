#!/usr/bin/env python
"""Example: Running llmtest with Anthropic provider.

Requirements:
- Set ANTHROPIC_API_KEY environment variable
- Install: pip install llmtest[anthropic]

Usage:
    export ANTHROPIC_API_KEY=your-api-key
    python run_test.py
"""

import os
import sys

from llmtest import TestRunner
from llmtest.reporting import ConsoleReporter, JSONReporter

# Check for API key
if not os.getenv("ANTHROPIC_API_KEY"):
    print("ERROR: ANTHROPIC_API_KEY environment variable not set")
    print("\nSet it with:")
    print("  export ANTHROPIC_API_KEY=your-api-key-here")
    sys.exit(1)

# Try to import Anthropic provider
try:
    from llmtest.providers.anthropic_provider import AnthropicProvider
except ImportError:
    print("ERROR: anthropic package not installed")
    print("\nInstall it with:")
    print("  pip install llmtest[anthropic]")
    print("  # or")
    print("  pip install anthropic")
    sys.exit(1)

# Create Anthropic provider
print("Initializing Anthropic provider...")
provider = AnthropicProvider(model="claude-3-haiku-20240307")

# Create runner
runner = TestRunner(provider)

# Run tests from YAML file
print("=" * 70)
print("Running llmtest with Anthropic Claude")
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
