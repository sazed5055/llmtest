#!/usr/bin/env python3
"""
Generate sample HTML and JSON reports for documentation.
Run this script to create example reports that show what llmtest output looks like.
"""

import os
from pathlib import Path
from llmtest import TestRunner
from llmtest.providers.mock import MockProvider
from llmtest.reporting import ConsoleReporter, JSONReporter
from llmtest.html_reporter import HTMLReporter

def main():
    print("Generating sample reports for llmtest...")
    print("=" * 60)

    # Create reports directory
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    # Initialize mock provider (no API key needed)
    provider = MockProvider()
    runner = TestRunner(provider)

    # 1. Generate basic test report
    print("\n1. Running basic tests...")
    config_path = Path(__file__).parent / "simple_test" / "test_config.yaml"
    results = runner.run_from_file(str(config_path))

    # Save JSON report
    json_reporter = JSONReporter()
    json_path = reports_dir / "sample_results.json"
    json_reporter.report(results, str(json_path))
    print(f"   ✓ JSON report: {json_path}")

    # Save HTML report
    html_reporter = HTMLReporter()
    html_path = reports_dir / "sample_report.html"
    html_reporter.report(results, str(html_path))
    print(f"   ✓ HTML report: {html_path}")

    # 2. Generate customer support example report
    print("\n2. Running customer support tests...")
    customer_config = Path(__file__).parent / "customer_support_bot.yaml"
    if customer_config.exists():
        customer_results = runner.run_from_file(str(customer_config))

        json_path = reports_dir / "customer_support_results.json"
        json_reporter.report(customer_results, str(json_path))
        print(f"   ✓ JSON report: {json_path}")

        html_path = reports_dir / "customer_support_report.html"
        html_reporter.report(customer_results, str(html_path))
        print(f"   ✓ HTML report: {html_path}")

    # 3. Generate RAG example report
    print("\n3. Running RAG application tests...")
    rag_config = Path(__file__).parent / "rag_application.yaml"
    if rag_config.exists():
        rag_results = runner.run_from_file(str(rag_config))

        json_path = reports_dir / "rag_application_results.json"
        json_reporter.report(rag_results, str(json_path))
        print(f"   ✓ JSON report: {json_path}")

        html_path = reports_dir / "rag_application_report.html"
        html_reporter.report(rag_results, str(html_path))
        print(f"   ✓ HTML report: {html_path}")

    # 4. Console summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total tests: {results.total}")
    print(f"  Passed: {results.passed}")
    print(f"  Failed: {results.failed}")
    print(f"  Pass rate: {results.pass_rate:.1f}%")
    print("=" * 60)

    print(f"\n✅ Sample reports generated in: {reports_dir.absolute()}")
    print("\nThese reports can be:")
    print("  • Included in documentation")
    print("  • Shared as examples with users")
    print("  • Used for screenshots in README")
    print("  • Referenced in blog posts/articles")

if __name__ == "__main__":
    main()
