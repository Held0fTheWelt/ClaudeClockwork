#!/usr/bin/env python3
"""
Final Summary Agent: Ollama generates the completion report.
No human work - agent reads artifacts and writes summary.
"""

import ollama
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

def read_artifacts():
    """Read all generated artifacts."""
    artifacts = {}

    # REQ D
    d_file = PROJECT_ROOT / "docs/SUGGESTED_DISCUSSIONS_ANALYSIS.md"
    if d_file.exists():
        artifacts["req_d"] = d_file.read_text()[:1000]

    # REQ E
    e_file = PROJECT_ROOT / "backend/tests/test_suggestion_coverage_complete.py"
    if e_file.exists():
        artifacts["req_e"] = e_file.read_text()[:1000]

    # REQ F
    f_file = PROJECT_ROOT / "docs/SUGGESTED_DISCUSSIONS.md"
    if f_file.exists():
        artifacts["req_f"] = f_file.read_text()[:1000]

    # Validation reports
    val_file = PROJECT_ROOT / ".ollama/REQ_E_GRANULAR_VALIDATION.md"
    if val_file.exists():
        artifacts["validation"] = val_file.read_text()[:1000]

    return artifacts

def generate_final_report(artifacts: dict) -> str:
    """Have Ollama agent generate final summary."""

    prompt = f"""You are a technical project manager. Analyze these completion artifacts and generate a concise final summary report.

ARTIFACTS OVERVIEW:
- REQ D (API Analysis): {len(artifacts.get('req_d', ''))} chars
- REQ E (Tests): {len(artifacts.get('req_e', ''))} chars
- REQ F (Docs): {len(artifacts.get('req_f', ''))} chars
- Validation: {len(artifacts.get('validation', ''))} chars

REQ D SAMPLE:
{artifacts.get('req_d', 'N/A')[:300]}...

REQ E SAMPLE:
{artifacts.get('req_e', 'N/A')[:300]}...

REQ F SAMPLE:
{artifacts.get('req_f', 'N/A')[:300]}...

VALIDATION SAMPLE:
{artifacts.get('validation', 'N/A')[:300]}...

Generate a FINAL PROJECT COMPLETION REPORT with sections:

## EXECUTIVE SUMMARY
- Overall status (complete/partial/failed)
- Key metrics (tests generated, files committed, quality scores)

## REQUIREMENT COMPLETION
For each (D, E, F):
- Status (✓/⚠/✗)
- What was delivered
- Quality assessment
- Known limitations

## APPROACH & METHODOLOGY
- Explain the iterative/Ollama-agent approach used
- Why it worked (Phase 5 findings)
- Optimization techniques applied

## DELIVERABLES
- List all committed files with line counts
- Verification results
- Test metrics

## KNOWN ISSUES & NEXT STEPS
- Current limitations
- Recommended improvements
- Priority order

## CONCLUSION
- One paragraph summary of completion
- Grade the overall work (A/B/C/D)
- Readiness assessment

Format as markdown, technical but concise. This is the FINAL REPORT for stakeholders."""

    print("\n" + "="*70)
    print("  FINAL SUMMARY AGENT (Ollama)")
    print("="*70)
    print("\n  Analyzing artifacts...\n")

    try:
        response = ollama.generate(
            model="gemma3:latest",
            prompt=prompt,
            stream=False,
        )
        report = response.get("response", "").strip()
        return report
    except Exception as e:
        return f"Error generating report: {str(e)}"

def main():
    """Execute final summary generation."""

    # Read artifacts
    artifacts = read_artifacts()

    if not artifacts:
        print("✗ No artifacts found")
        return False

    # Generate report
    report = generate_final_report(artifacts)

    # Save report
    report_file = PROJECT_ROOT / ".ollama/FINAL_COMPLETION_REPORT.md"
    report_file.write_text(report)

    print("✓ Report generated\n")
    print("="*70)
    print(report)
    print("="*70)
    print(f"\nSaved to: {report_file}\n")

    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
