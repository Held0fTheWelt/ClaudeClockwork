#!/usr/bin/env python3
"""REQ E: Minimal test generation (faster version)."""

import ollama
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from helper_functions import write_file, run_pytest, git_commit

print("Generating minimal but complete test file...")

prompt = """Generate a MINIMAL pytest file covering all 10 areas.

File: backend/tests/test_suggestion_coverage_complete.py
Must be VALID Python (no syntax errors).

10 test areas (2 tests each = 20 total):
1. News ranking
2. Wiki ranking
3. Exclude primary
4. Exclude related
5. Exclude hidden
6. Deterministic
7. Truthful labels
8. Distinction
9. Management UI
10. API endpoints

Minimal fixture, minimal test code, but VALID.
Start: import pytest
End: last test method

Output ONLY code."""

response = ollama.generate(
    model="qwen2.5-coder-32b:coding",
    prompt=prompt,
    stream=False
)

test_code = response.get("response", "").strip()

if not test_code:
    print("Empty response")
    sys.exit(1)

# Verify syntax
try:
    compile(test_code, "test", "exec")
except SyntaxError as e:
    print(f"Syntax error: {e}")
    sys.exit(1)

# Write
write_file("backend/tests/test_suggestion_coverage_complete.py", test_code)

# Test
passed, cov = run_pytest("backend/tests/test_suggestion_coverage_complete.py", cov_threshold=50)

if passed:
    print(f"✓ Tests passed ({cov}% coverage)")
    git_commit(
        ["backend/tests/test_suggestion_coverage_complete.py"],
        "feat: REQ E - Test coverage for suggested-discussions (agent-generated)"
    )
else:
    print(f"✗ Tests failed ({cov}%)")
    sys.exit(1)
