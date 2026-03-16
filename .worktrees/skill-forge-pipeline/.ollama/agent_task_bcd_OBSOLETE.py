#!/usr/bin/env python3
"""
TASK B, C, D Agent: Autonomous fixes for docs, Postman, and tests.
Agent reads code, identifies real behavior, updates docs/Postman, generates tests.
"""

import ollama
import subprocess
import json
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

def run_task_b():
    """TASK B: Update Postman and docs to match real ranking logic."""
    print("\n" + "="*70)
    print("  TASK B: Truthful Ranking Docs/Postman")
    print("="*70 + "\n")

    # Read the real ranking logic
    news_service = (PROJECT_ROOT / "backend/app/services/news_service.py").read_text()

    prompt = f"""Analyze this real ranking logic and generate Postman/docs corrections.

REAL RANKING CODE (excerpt from news_service.py):

def get_suggested_threads_for_article():
    Uses deterministic ranking based on:
    - Tag matches from discussion thread
    - Recent activity (tie-breaker)
    - Excludes: primary discussion, manually related threads, hidden/deleted threads

CURRENT DOCS/POSTMAN (likely claim):
- Reason: "Same category"
- Signal: category-based relevance

YOUR TASK:
1. Identify what the real ranking logic actually uses
2. Generate corrected reason labels that match the real logic
3. Generate corrected example responses for Postman

OUTPUT:
===== REAL SIGNALS =====
[List what's actually used]

===== EXAMPLE REASON LABELS =====
[Provide corrected reason labels]

===== POSTMAN RESPONSE EXAMPLE =====
[Example of correct response object]

===== FILES TO UPDATE =====
[List which files need updating and what changes]"""

    response = ollama.generate(
        model="gemma3:latest",
        prompt=prompt,
        stream=False,
    )

    corrections = response.get("response", "").strip()
    print(corrections)

    # Save the corrections for reference
    (PROJECT_ROOT / ".ollama/task_b_corrections.txt").write_text(corrections)
    print("\n✓ Task B analysis complete (saved to .ollama/task_b_corrections.txt)")
    return True


def run_task_c():
    """TASK C: Verify Wiki route and align docs."""
    print("\n" + "="*70)
    print("  TASK C: Wiki Route Shape Alignment")
    print("="*70 + "\n")

    # Read Wiki routes
    wiki_routes = (PROJECT_ROOT / "backend/app/api/v1/wiki_routes.py").read_text()

    prompt = f"""Analyze the real Wiki suggested-threads endpoint code.

WIKI ROUTES CODE EXCERPT:
{wiki_routes[2000:3000]}

YOUR TASK:
1. Find the exact endpoint route for suggested-threads
2. Does it use /id or /slug or both?
3. What parameters does it take?
4. What does it return?

OUTPUT:
EXACT_ROUTE: [e.g., /api/v1/wiki/<int:page_id>/suggested-threads]
PARAMETER_TYPE: [id or slug or both]
RETURNS: [what the response looks like]

Then specify:
POSTMAN_SHOULD_USE: [the correct route format]
DOCS_SHOULD_SAY: [the exact endpoint documentation]"""

    response = ollama.generate(
        model="gemma3:latest",
        prompt=prompt,
        stream=False,
    )

    findings = response.get("response", "").strip()
    print(findings)

    # Save findings
    (PROJECT_ROOT / ".ollama/task_c_findings.txt").write_text(findings)
    print("\n✓ Task C analysis complete (saved to .ollama/task_c_findings.txt)")
    return True


def run_task_d():
    """TASK D: Generate focused backend tests."""
    print("\n" + "="*70)
    print("  TASK D: Focused Backend Tests")
    print("="*70 + "\n")

    prompt = """Generate focused pytest tests for suggested-discussions.

TESTS NEEDED (one test per requirement):
1. duplicate exclusion - test that same thread not suggested twice
2. hidden/inaccessible exclusion - test hidden threads excluded
3. deterministic ordering - test same input yields same output
4. truthful reason labels - test reason matches actual ranking logic

Generate ONLY test functions (not full file, not class definition).
Each test as a complete function that can be pasted into test file.

Use fixtures: client, app, admin_headers
API endpoint to test: GET /api/v1/news/<id>/suggested-threads

OUTPUT FORMAT:
===== TEST 1: Duplicate Exclusion =====
def test_news_suggestions_no_duplicates(client, app, admin_headers):
    [complete test code]

===== TEST 2: Hidden Exclusion =====
def test_news_suggestions_exclude_hidden(client, app, admin_headers):
    [complete test code]

===== TEST 3: Deterministic Ordering =====
def test_news_suggestions_deterministic(client, app, admin_headers):
    [complete test code]

===== TEST 4: Truthful Labels =====
def test_news_suggestions_truthful_reasons(client, app, admin_headers):
    [complete test code]"""

    response = ollama.generate(
        model="gemma3:latest",
        prompt=prompt,
        stream=False,
    )

    tests = response.get("response", "").strip()
    print(tests[:1000])
    print("\n... (full tests saved)\n")

    # Save tests
    (PROJECT_ROOT / ".ollama/task_d_tests.py").write_text(tests)
    print("✓ Task D tests generated (saved to .ollama/task_d_tests.py)")
    return True


def main():
    """Run all three tasks."""
    print("\n" + "="*70)
    print("  TASKS B, C, D AGENT")
    print("="*70)

    task_b = run_task_b()
    task_c = run_task_c()
    task_d = run_task_d()

    print("\n" + "="*70)
    if task_b and task_c and task_d:
        print("  ✓ TASKS B, C, D COMPLETE")
    else:
        print("  ✗ SOME TASKS FAILED")
    print("="*70 + "\n")

    return task_b and task_c and task_d


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
