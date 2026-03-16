#!/usr/bin/env python3
"""
Granular Test Validator: Validates each test function independently.
Checks syntax, structure, and logic without running full pytest.
"""

import ast
import re
from pathlib import Path
import ollama

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

def parse_test_file() -> dict:
    """Parse test file and extract individual test functions."""
    test_file = PROJECT_ROOT / "backend/tests/test_suggestion_coverage_complete.py"

    with open(test_file) as f:
        content = f.read()

    # Parse AST to find classes and methods
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return {"error": f"Syntax error: {e}"}

    tests = {}
    current_class = None

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            current_class = node.name
            tests[current_class] = []

            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                    # Extract test info
                    test_info = {
                        "class": current_class,
                        "name": item.name,
                        "line": item.lineno,
                        "docstring": ast.get_docstring(item) or "No docstring",
                        "assertions": 0,
                        "api_calls": 0,
                    }

                    # Count assertions
                    for sub_node in ast.walk(item):
                        if isinstance(sub_node, ast.Assert):
                            test_info["assertions"] += 1
                        elif isinstance(sub_node, ast.Call):
                            if isinstance(sub_node.func, ast.Attribute):
                                if sub_node.func.attr in ["post", "get", "put", "delete"]:
                                    test_info["api_calls"] += 1

                    tests[current_class].append(test_info)

    return tests


def validate_test_structure(tests: dict) -> dict:
    """Validate structure of each test."""
    print("\n" + "="*70)
    print("  Step 1: Validate Test Structure")
    print("="*70 + "\n")

    results = {
        "total_tests": 0,
        "valid_tests": 0,
        "issues": [],
        "details": [],
    }

    for class_name, test_list in tests.items():
        if class_name == "error":
            results["issues"].append(tests["error"])
            continue

        print(f"[{class_name}]")

        for test in test_list:
            results["total_tests"] += 1
            name = f"{class_name}.{test['name']}"

            # Check for required properties
            issues = []

            if not test["docstring"]:
                issues.append("No docstring")

            if test["assertions"] == 0:
                issues.append("No assertions found")

            if test["api_calls"] == 0:
                issues.append("No API calls (test may not interact with system)")

            if not issues:
                results["valid_tests"] += 1
                status = "✓"
            else:
                status = "⚠"
                results["issues"].extend([f"{name}: {issue}" for issue in issues])

            detail = {
                "test": name,
                "assertions": test["assertions"],
                "api_calls": test["api_calls"],
                "docstring_len": len(test["docstring"]),
                "status": status,
                "issues": issues,
            }

            results["details"].append(detail)

            print(f"  {status} {test['name']}")
            print(f"     Assertions: {test['assertions']}, API calls: {test['api_calls']}")
            if issues:
                print(f"     Issues: {', '.join(issues)}")

    return results


def get_ollama_assessment(test_info: dict) -> str:
    """Have Ollama assess test quality."""
    print("\n" + "="*70)
    print("  Step 2: Ollama Quality Assessment")
    print("="*70)

    # Summarize test info for Ollama
    test_counts = {
        "total": test_info["total_tests"],
        "valid": test_info["valid_tests"],
        "with_issues": test_info["total_tests"] - test_info["valid_tests"],
    }

    issues_text = "\n".join(test_info["issues"][:10]) if test_info["issues"] else "None"

    prompt = f"""Assessment Summary:
- Total test functions: {test_counts['total']}
- Valid/well-formed: {test_counts['valid']}
- With issues: {test_counts['with_issues']}

Issues identified:
{issues_text}

Provide a brief assessment of test quality:
1. Strengths: What's working well?
2. Weaknesses: What needs improvement?
3. Next Steps: How to fix the issues?
4. Overall Grade: A/B/C/D (and why)

Be concise, technical, actionable."""

    print("\n  Calling Ollama for assessment...\n")

    try:
        response = ollama.generate(
            model="gemma3:latest",
            prompt=prompt,
            stream=False,
        )

        assessment = response.get("response", "").strip()
        if assessment:
            print("✓ Assessment received\n")
            return assessment
    except Exception as e:
        print(f"✗ Error: {str(e)[:100]}\n")

    return ""


def save_granular_report(test_info: dict, assessment: str) -> Path:
    """Save granular validation report."""
    print("="*70)
    print("  Step 3: Save Granular Report")
    print("="*70)

    report = f"""# REQ E Granular Test Validation Report

**Test Execution Date**: {__import__('datetime').datetime.now().isoformat()}

## Validation Summary

| Metric | Value |
|--------|-------|
| Total Test Functions | {test_info['total_tests']} |
| Valid/Well-formed Tests | {test_info['valid_tests']} |
| Tests with Issues | {test_info['total_tests'] - test_info['valid_tests']} |
| Validation Pass Rate | {(test_info['valid_tests'] / test_info['total_tests'] * 100) if test_info['total_tests'] > 0 else 0:.1f}% |

## Detailed Results

| Test Name | Assertions | API Calls | Status | Issues |
|-----------|-----------|-----------|--------|--------|
"""

    for detail in test_info["details"]:
        issues = ", ".join(detail["issues"]) if detail["issues"] else "None"
        report += f"| {detail['test']} | {detail['assertions']} | {detail['api_calls']} | {detail['status']} | {issues} |\n"

    report += f"""

## Issues Found

{chr(10).join(f"- {issue}" for issue in test_info['issues']) if test_info['issues'] else "No critical issues"}

## Ollama Assessment

{assessment}

## Recommendations

1. **Import Errors**: Fix missing model imports (Forum, Thread, etc.)
2. **Fixture Setup**: Ensure suggestion_test_data creates proper test objects
3. **Test Execution**: Once imports are fixed, run pytest to validate assertions
4. **Coverage**: Verify that all 10 requirement areas are adequately tested

## Next Steps

- Fix import errors in test file
- Run pytest to validate test execution
- Address any assertion failures
- Iterate until all tests pass

---
Generated by Ollama-assisted granular validation
"""

    report_file = PROJECT_ROOT / ".ollama/REQ_E_GRANULAR_VALIDATION.md"
    report_file.write_text(report)

    print(f"\n✓ Report saved: {report_file}\n")
    return report_file


def main():
    """Execute granular validation workflow."""
    print("\n" + "="*70)
    print("  REQ E GRANULAR TEST VALIDATOR")
    print("="*70)

    # Step 1: Parse and validate structure
    tests = parse_test_file()

    if "error" in tests:
        print(f"\n✗ Error parsing test file: {tests['error']}")
        return False

    validation_results = validate_test_structure(tests)

    # Step 2: Get Ollama assessment
    assessment = get_ollama_assessment(validation_results)

    # Step 3: Save report
    report_file = save_granular_report(validation_results, assessment)

    # Display summary
    print("\n" + "="*70)
    print("  VALIDATION SUMMARY")
    print("="*70)
    print(f"\nTotal Tests: {validation_results['total_tests']}")
    print(f"Valid Tests: {validation_results['valid_tests']}")
    print(f"Pass Rate: {(validation_results['valid_tests'] / validation_results['total_tests'] * 100) if validation_results['total_tests'] > 0 else 0:.1f}%")

    if validation_results["issues"]:
        print(f"\nIssues Found: {len(validation_results['issues'])}")
        for issue in validation_results["issues"][:5]:
            print(f"  - {issue}")

    print("\n" + "="*70)
    print(f"  ✓ VALIDATION COMPLETE")
    print(f"  Report: {report_file}")
    print("="*70 + "\n")

    return True


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
