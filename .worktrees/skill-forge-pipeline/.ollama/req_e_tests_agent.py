#!/usr/bin/env python3
"""REQ E: Test coverage (simplified agent orchestration)."""

import ollama
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from helper_functions import write_file, run_pytest, verify_coverage, git_commit, run_existing_tests

print("\n" + "="*70)
print("  REQ E: Comprehensive Test Coverage")
print("="*70 + "\n")

baseline = run_existing_tests()
print(f"  Baseline coverage: {baseline}%\n")

prompt = """Generate a MINIMAL but COMPLETE pytest test file for suggested-discussions.

CRITICAL: Must be VALID Python (no syntax errors).

Structure:
- Import: pytest, datetime, timezone, db, models, services
- Fixture: suggestion_test_data (creates test forum threads, tags, articles)
- Test classes: 10 classes, 25+ methods total
  * TestNewsSuggestions (4 methods)
  * TestWikiSuggestions (3 methods) 
  * TestExcludePrimary (2 methods)
  * TestExcludeRelated (2 methods)
  * TestExcludeHidden (2 methods)
  * TestDeterministic (2 methods)
  * TestReasonLabels (2 methods)
  * TestDistinction (2 methods)
  * TestMgmtUI (2 methods)
  * TestAPIEndpoint (5 methods)

Each test method:
- Has clear assertion
- Tests ONE thing
- Is independent

Output ONLY valid Python code."""

print("  Calling Ollama to generate tests...")
response = ollama.generate(model="qwen2.5-coder-32b:coding", prompt=prompt, stream=False)
test_code = response.get("response", "").strip()

if not test_code:
    print("  ✗ Empty response")
    sys.exit(1)

# Verify syntax
try:
    compile(test_code, "test_file", "exec")
except SyntaxError as e:
    print(f"  ✗ Syntax error: {e}")
    sys.exit(1)

# Write and test
print("  Writing test file...")
write_file(".ollama/test_suggestion_coverage_complete.py", test_code)

print("  Running tests...")
passed, cov = run_pytest(".ollama/test_suggestion_coverage_complete.py")

if not passed:
    print(f"  ✗ Tests failed (coverage: {cov}%)")
    sys.exit(1)

if cov < baseline:
    print(f"  ✗ Coverage decreased ({baseline}% → {cov}%)")
    sys.exit(1)

# Commit
git_commit(
    [".ollama/test_suggestion_coverage_complete.py"],
    f"feat(ollama): REQ E - Tests {cov}% coverage (agent-generated)"
)

print(f"\n✓ REQ E COMPLETE ({cov}% coverage)\n")
