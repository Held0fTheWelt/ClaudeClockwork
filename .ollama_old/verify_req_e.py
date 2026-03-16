#!/usr/bin/env python3
"""
Verification Agent: Ollama analyzes test results and reports quality.
Uses Phase 5 findings: single-model (gemma3:latest for speed) + serialization.
"""

import subprocess
import ollama
from pathlib import Path
import json

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

def run_tests() -> tuple[bool, str, str]:
    """Run the generated test file and capture output."""
    print("\n" + "="*70)
    print("  Step 1: Execute Tests")
    print("="*70)

    test_file = PROJECT_ROOT / "backend/tests/test_suggestion_coverage_complete.py"

    try:
        result = subprocess.run(
            ["python3", "-m", "pytest", str(test_file), "-v", "--tb=short", "--no-cov"],
            cwd=str(PROJECT_ROOT / "backend"),
            capture_output=True,
            text=True,
            timeout=120,
        )

        print(f"\nExit Code: {result.returncode}")
        print(f"Output Length: {len(result.stdout)} chars")

        # Check for specific patterns
        if "passed" in result.stdout.lower():
            print("✓ Tests executed (some passed)")
        elif "error" in result.stdout.lower() or result.returncode != 0:
            print(f"⚠ Tests failed or errored")

        return (result.returncode == 0, result.stdout, result.stderr)

    except subprocess.TimeoutExpired:
        error_msg = "Test execution timed out (120s)"
        print(f"✗ {error_msg}")
        return (False, "", error_msg)
    except Exception as e:
        error_msg = f"Test execution error: {str(e)}"
        print(f"✗ {error_msg}")
        return (False, "", error_msg)


def analyze_tests(stdout: str, stderr: str) -> str:
    """Use Ollama agent to analyze test results."""
    print("\n" + "="*70)
    print("  Step 2: Analyze Test Results with Ollama")
    print("="*70)

    # Prepare analysis prompt
    test_output = stdout[:2000] if stdout else stderr[:2000]  # Truncate for context

    prompt = f"""You are a Python testing expert. Analyze this test execution output and provide a quality report.

TEST OUTPUT (first 2000 chars):
{test_output}

ANALYSIS TASK:
1. **Test Status**: Are the tests passing or failing? Count how many passed/failed if visible.
2. **Coverage**: Are all 10 requirement areas tested? List which are covered.
3. **Fixture Quality**: Does the suggestion_test_data fixture create proper test data?
4. **Assertion Quality**: Are assertions validating real behavior or just checking status codes?
5. **Issues Found**: List any problems, errors, or gaps.
6. **Recommendations**: What improvements would strengthen these tests?

OUTPUT FORMAT:
===== TEST STATUS =====
[PASS/FAIL/PARTIAL - explain]

===== COVERAGE ANALYSIS =====
- Requirement 1 (News Ranking): [✓/✗]
- Requirement 2 (Wiki Ranking): [✓/✗]
- ... (all 10)

===== FIXTURE QUALITY =====
[Assessment of test data setup]

===== ASSERTION QUALITY =====
[Assessment of what's being tested]

===== ISSUES FOUND =====
[List of any problems]

===== RECOMMENDATIONS =====
[Suggestions for improvement]

===== OVERALL ASSESSMENT =====
[One paragraph summary]"""

    print("\n  Calling Ollama analysis agent...")

    try:
        response = ollama.generate(
            model="gemma3:latest",  # Fast model for analysis
            prompt=prompt,
            stream=False,
        )

        analysis = response.get("response", "").strip()
        if analysis and len(analysis) > 100:
            print(f"✓ Analysis complete ({len(analysis)} chars)\n")
            return analysis
        else:
            print("✗ Analysis incomplete")
            return ""

    except Exception as e:
        print(f"✗ Ollama error: {str(e)[:100]}")
        return ""


def save_report(test_passed: bool, analysis: str) -> Path:
    """Save verification report to file."""
    print("="*70)
    print("  Step 3: Save Verification Report")
    print("="*70)

    report = f"""# REQ E Verification Report

**Generated**: {__import__('datetime').datetime.now().isoformat()}
**Test Status**: {'PASSED' if test_passed else 'FAILED/PARTIAL'}

## Analysis

{analysis}

## Next Steps

If any issues were identified:
1. Review the recommendations above
2. Have Ollama agent generate updated test implementations
3. Re-run verification
4. Commit updates

If tests are passing:
1. Run full backend test suite to ensure no regressions
2. Verify coverage meets 85% threshold
3. Proceed to merge

---
"""

    report_file = PROJECT_ROOT / ".ollama/REQ_E_VERIFICATION_REPORT.md"
    report_file.write_text(report)

    print(f"✓ Report saved: {report_file}\n")
    return report_file


def main():
    """Execute verification workflow."""
    print("\n" + "="*70)
    print("  VERIFICATION AGENT: REQ E Test Quality Analysis")
    print("="*70)

    # Step 1: Run tests
    test_passed, stdout, stderr = run_tests()

    # Step 2: Analyze with Ollama
    analysis = analyze_tests(stdout, stderr)

    if not analysis:
        print("\n✗ Verification failed: could not analyze results")
        return False

    # Step 3: Save report
    report_file = save_report(test_passed, analysis)

    # Display report
    print("\n" + "="*70)
    print("  VERIFICATION REPORT")
    print("="*70 + "\n")
    with open(report_file) as f:
        print(f.read())

    print("\n" + "="*70)
    print("  ✓ VERIFICATION COMPLETE")
    print("="*70 + "\n")

    return True


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
