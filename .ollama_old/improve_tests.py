#!/usr/bin/env python3
"""
Test Improvement Agent: Regenerate tests that lack API calls.
Fixes 3 tests identified in granular validation:
1. test_exclude_related_threads
2. test_exclude_hidden_threads
3. test_primary_vs_related_vs_suggested
"""

import ollama
import re
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

TESTS_TO_IMPROVE = [
    {
        "class": "TestSuggestionExclusions",
        "name": "test_exclude_related_threads",
        "requirement": "Test that manually related threads are excluded from suggestions. Need API calls to create threads, link them manually, fetch suggestions, and verify linked threads don't appear.",
    },
    {
        "class": "TestSuggestionExclusions",
        "name": "test_exclude_hidden_threads",
        "requirement": "Test that hidden/deleted threads are excluded. Need API calls to create hidden threads, fetch suggestions, verify hidden threads are not included.",
    },
    {
        "class": "TestThreadTypeDistinction",
        "name": "test_primary_vs_related_vs_suggested",
        "requirement": "Test three thread types: primary (1:1), related (manual), suggested (algorithmic). Need API calls to fetch each type and verify they're returned in correct sections.",
    },
]

def regenerate_test(test_spec: dict) -> str:
    """Regenerate a single test with API interactions."""

    prompt = f"""Regenerate this test with proper API interactions:

TEST: {test_spec['class']}.{test_spec['name']}
REQUIREMENT: {test_spec['requirement']}

The test MUST:
1. Create test data using API calls (POST /api/v1/forums/threads, etc.)
2. Perform actions using API calls (linking, hiding, etc.)
3. Fetch results using GET API calls
4. Assert on API response data

Structure:
```python
def {test_spec['name']}(self, client, suggestion_test_data, admin_headers=None):
    \"\"\"Test: {test_spec['requirement'][:80]}...\"\"\"

    # Setup: Create threads via API
    response = client.post('/api/v1/forums/threads', ...)
    assert response.status_code == 201
    thread1 = response.json

    # Action: Perform API operation
    response = client.post(f'/api/v1/forums/threads/{{thread1["id"]}}/link', ...)
    assert response.status_code == 200

    # Verify: Fetch and assert
    response = client.get(f'/api/v1/forums/threads/{{primary_id}}/suggestions', ...)
    assert response.status_code == 200
    suggestions = response.json
    assert thread1['id'] not in [s['id'] for s in suggestions]
```

Output ONLY the complete function (no class, no markdown, no explanations).
Use fixtures: client, suggestion_test_data, admin_headers=None
All assertions must validate actual API behavior."""

    print(f"  Regenerating {test_spec['class']}.{test_spec['name']}...", end=" ")

    try:
        response = ollama.generate(
            model="gemma3:latest",
            prompt=prompt,
            stream=False,
        )

        code = response.get("response", "").strip()
        if code and "def " in code:
            print("✓")
            return code
        else:
            print("✗ (empty response)")
            return ""

    except Exception as e:
        print(f"✗ ({str(e)[:50]})")
        return ""


def update_test_file():
    """Update test file with improved versions."""
    print("\n" + "="*70)
    print("  TEST IMPROVEMENT AGENT")
    print("="*70 + "\n")

    test_file = PROJECT_ROOT / "backend/tests/test_suggestion_coverage_complete.py"

    # Read current file
    with open(test_file) as f:
        content = f.read()

    improved_count = 0

    for test_spec in TESTS_TO_IMPROVE:
        # Regenerate test
        new_code = regenerate_test(test_spec)

        if not new_code:
            continue

        # Find and replace old test in file
        # Pattern: def test_name(self, ... ): ... up to next def or class
        pattern = rf"(    def {test_spec['name']}\(.*?\):.*?)(?=\n    def |\nclass |\Z)"
        match = re.search(pattern, content, re.DOTALL)

        if match:
            # Replace old test with new one
            indented_code = "\n".join(f"    {line}" if line else "" for line in new_code.split("\n"))
            content = content[:match.start()] + indented_code + content[match.end():]
            improved_count += 1
            print(f"  ✓ Updated {test_spec['name']}")
        else:
            print(f"  ✗ Could not find {test_spec['name']} in file")

    # Write updated file
    with open(test_file, "w") as f:
        f.write(content)

    print(f"\n✓ Updated {improved_count}/{len(TESTS_TO_IMPROVE)} tests")

    # Verify syntax
    try:
        import ast
        ast.parse(content)
        print("✓ Syntax valid\n")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}\n")
        return False


def main():
    """Execute test improvement workflow."""
    success = update_test_file()

    if success:
        print("="*70)
        print("  TEST IMPROVEMENT COMPLETE")
        print("="*70)
        print("\nNext: Run pytest to validate improved tests")
        print("Command: pytest backend/tests/test_suggestion_coverage_complete.py -v\n")
        return True
    else:
        print("✗ Test improvement failed")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
