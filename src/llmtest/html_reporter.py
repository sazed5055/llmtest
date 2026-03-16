"""HTML reporter for test results."""

from datetime import datetime
from pathlib import Path
from typing import Union

from llmtest.models import TestSuiteResult, TestType


class HTMLReporter:
    """Generate HTML reports for test results."""

    def report(self, results: TestSuiteResult, output_path: Union[str, Path]) -> None:
        """
        Generate HTML report file.

        Args:
            results: Test suite results
            output_path: Path to output HTML file
        """
        output_path = Path(output_path)

        html_content = self._generate_html(results)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"HTML report written to: {output_path}")

    def _generate_html(self, results: TestSuiteResult) -> str:
        """
        Generate HTML content for results.

        Args:
            results: Test suite results

        Returns:
            HTML string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Generate test cards
        test_cards = []
        for test_result in results.test_results:
            status_class = {
                "pass": "success",
                "fail": "danger",
                "error": "warning",
                "skipped": "secondary",
            }.get(test_result.status.value, "secondary")

            status_icon = {
                "pass": "✓",
                "fail": "✗",
                "error": "⚠",
                "skipped": "○",
            }.get(test_result.status.value, "?")

            # Build details section
            details_html = ""
            if test_result.evaluator_result:
                eval_result = test_result.evaluator_result

                if eval_result.issues:
                    details_html += "<div class='issues'><h4>Issues:</h4><ul>"
                    for issue in eval_result.issues:
                        details_html += f"<li>{self._escape_html(issue)}</li>"
                    details_html += "</ul></div>"

                # Show must_include check details
                if "must_include_check" in eval_result.details:
                    check = eval_result.details["must_include_check"]
                    if check.get("matched"):
                        details_html += (
                            f"<div class='check-passed'>✓ Matched required: "
                            f"{', '.join(check['matched'])}</div>"
                        )
                    if check.get("missing"):
                        details_html += (
                            f"<div class='check-failed'>✗ Missing required: "
                            f"{', '.join(check['missing'])}</div>"
                        )

                # Show must_not_include check details
                if "must_not_include_check" in eval_result.details:
                    check = eval_result.details["must_not_include_check"]
                    if check.get("found"):
                        details_html += (
                            f"<div class='check-failed'>✗ Found forbidden: "
                            f"{', '.join(check['found'])}</div>"
                        )

                # Show refusal status
                if "refused" in eval_result.details:
                    refused = eval_result.details["refused"]
                    if refused:
                        details_html += "<div class='check-passed'>✓ Request refused</div>"
                    else:
                        details_html += "<div class='check-failed'>✗ Did not refuse</div>"

                # Show leakage detection
                if eval_result.details.get("potential_leakage"):
                    details_html += (
                        "<div class='check-failed'>⚠ Potential information leakage</div>"
                    )

            elif test_result.error_message:
                details_html += (
                    f"<div class='error-message'><h4>Error:</h4>"
                    f"<p>{self._escape_html(test_result.error_message)}</p></div>"
                )

            # Response preview
            response_preview = ""
            if test_result.response:
                response_text = test_result.response[:200]
                if len(test_result.response) > 200:
                    response_text += "..."
                response_preview = f"""
                <div class='response-preview'>
                    <h4>Response:</h4>
                    <p>{self._escape_html(response_text)}</p>
                </div>
                """

            test_card = f"""
            <div class='test-card status-{status_class}'>
                <div class='test-header'>
                    <span class='status-badge status-{status_class}'>{status_icon} {test_result.status.value.upper()}</span>
                    <h3>{self._escape_html(test_result.test_id)}</h3>
                    <span class='test-type'>{test_result.test_type.value}</span>
                </div>
                <div class='test-input'>
                    <strong>Input:</strong> {self._escape_html(test_result.input)}
                </div>
                {details_html}
                {response_preview}
            </div>
            """
            test_cards.append(test_card)

        # Calculate pass rates by type
        type_rates = []
        for test_type in TestType:
            rate = results.pass_rate_by_type(test_type)
            # Only show types that have tests
            if any(r.test_type == test_type for r in results.test_results):
                type_rates.append(
                    f"<div class='type-rate'>{test_type.value.capitalize()}: {rate:.1f}%</div>"
                )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>llmtest Report - {results.provider}/{results.model}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}

        .meta {{
            color: #7f8c8d;
            margin-bottom: 30px;
        }}

        .summary {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 30px;
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}

        .summary-item {{
            text-align: center;
        }}

        .summary-value {{
            font-size: 32px;
            font-weight: bold;
            display: block;
        }}

        .summary-label {{
            font-size: 14px;
            color: #7f8c8d;
            text-transform: uppercase;
        }}

        .pass-rate {{
            font-size: 48px;
            font-weight: bold;
            color: #27ae60;
        }}

        .pass-rate.low {{
            color: #e74c3c;
        }}

        .pass-rate.medium {{
            color: #f39c12;
        }}

        .type-rates {{
            margin-top: 20px;
        }}

        .type-rate {{
            display: inline-block;
            padding: 5px 15px;
            background: white;
            border-radius: 4px;
            margin: 5px;
            font-size: 14px;
        }}

        .test-card {{
            border: 2px solid #ecf0f1;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 20px;
            background: white;
        }}

        .test-card.status-success {{
            border-left: 4px solid #27ae60;
        }}

        .test-card.status-danger {{
            border-left: 4px solid #e74c3c;
        }}

        .test-card.status-warning {{
            border-left: 4px solid #f39c12;
        }}

        .test-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }}

        .test-header h3 {{
            flex: 1;
            color: #2c3e50;
        }}

        .status-badge {{
            padding: 5px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}

        .status-badge.status-success {{
            background: #27ae60;
            color: white;
        }}

        .status-badge.status-danger {{
            background: #e74c3c;
            color: white;
        }}

        .status-badge.status-warning {{
            background: #f39c12;
            color: white;
        }}

        .status-badge.status-secondary {{
            background: #95a5a6;
            color: white;
        }}

        .test-type {{
            padding: 4px 10px;
            background: #ecf0f1;
            border-radius: 4px;
            font-size: 12px;
            color: #7f8c8d;
        }}

        .test-input {{
            margin-bottom: 15px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
        }}

        .issues {{
            margin: 15px 0;
            padding: 15px;
            background: #fee;
            border-left: 3px solid #e74c3c;
            border-radius: 4px;
        }}

        .issues h4 {{
            color: #e74c3c;
            margin-bottom: 10px;
        }}

        .issues ul {{
            list-style-position: inside;
        }}

        .check-passed {{
            color: #27ae60;
            margin: 5px 0;
        }}

        .check-failed {{
            color: #e74c3c;
            margin: 5px 0;
        }}

        .error-message {{
            margin: 15px 0;
            padding: 15px;
            background: #fef5e7;
            border-left: 3px solid #f39c12;
            border-radius: 4px;
        }}

        .error-message h4 {{
            color: #f39c12;
            margin-bottom: 10px;
        }}

        .response-preview {{
            margin-top: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
        }}

        .response-preview h4 {{
            color: #7f8c8d;
            margin-bottom: 10px;
            font-size: 14px;
        }}

        .response-preview p {{
            color: #2c3e50;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }}

        footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>llmtest Test Report</h1>
        <div class="meta">
            Provider: {results.provider} | Model: {results.model} | Generated: {timestamp}
        </div>

        <div class="summary">
            <div class="summary-grid">
                <div class="summary-item">
                    <span class="summary-value pass-rate {'low' if results.pass_rate < 50 else 'medium' if results.pass_rate < 80 else ''}">{results.pass_rate:.1f}%</span>
                    <span class="summary-label">Pass Rate</span>
                </div>
                <div class="summary-item">
                    <span class="summary-value">{results.total}</span>
                    <span class="summary-label">Total Tests</span>
                </div>
                <div class="summary-item">
                    <span class="summary-value" style="color: #27ae60">{results.passed}</span>
                    <span class="summary-label">Passed</span>
                </div>
                <div class="summary-item">
                    <span class="summary-value" style="color: #e74c3c">{results.failed}</span>
                    <span class="summary-label">Failed</span>
                </div>
                {f'<div class="summary-item"><span class="summary-value" style="color: #f39c12">{results.errors}</span><span class="summary-label">Errors</span></div>' if results.errors > 0 else ''}
            </div>
            {f'<div class="type-rates"><strong>Pass Rates by Type:</strong><br>{"".join(type_rates)}</div>' if type_rates else ''}
        </div>

        <div class="tests">
            {''.join(test_cards)}
        </div>

        <footer>
            Generated by llmtest - pytest for LLM apps<br>
            Test for grounding failures, prompt injection, safety, and regressions
        </footer>
    </div>
</body>
</html>
"""
        return html

    def _escape_html(self, text: str) -> str:
        """
        Escape HTML special characters.

        Args:
            text: Text to escape

        Returns:
            Escaped text
        """
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
        )
