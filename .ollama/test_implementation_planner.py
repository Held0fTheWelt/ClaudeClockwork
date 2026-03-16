#!/usr/bin/env python3
"""Ollama agent creates implementation plan for suggested-discussions tests."""

import ollama
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from helper_functions import write_file, git_commit

print("\n" + "="*70)
print("  OLLAMA AGENT: Test Implementation Planner")
print("="*70 + "\n")

# Read the test plan that was generated
test_plan_file = Path("docs/TEST_PLAN_SUGGESTED_DISCUSSIONS.md")
if not test_plan_file.exists():
    print("✗ Test plan not found")
    sys.exit(1)

test_plan = test_plan_file.read_text()

# Have Ollama create an implementation plan
prompt = f"""You are a test implementation architect. 

Based on this test plan for suggested-discussions:

{test_plan}

Create a DETAILED IMPLEMENTATION PLAN that:

1. STRUCTURE
   - File: backend/tests/test_suggestion_coverage_complete.py
   - Organize by test classes (one per requirement area)
   - Each class groups related tests

2. FIXTURES
   - Define suggestion_test_data fixture
   - What data is needed (forums, threads, tags, articles, pages)
   - How to create test data with proper relationships
   - Resource cleanup strategy

3. TEST IMPLEMENTATION (for each area)
   - Specific test method names
   - Assertion patterns
   - How to validate each requirement
   - Edge cases to cover

4. COVERAGE STRATEGY
   - How to achieve 85%+ coverage for suggestion functions
   - Which imports and services to focus on
   - How to test ranking algorithm specifically

5. EXECUTION SEQUENCE
   - Which tests to write first
   - Dependencies between test classes
   - How to verify tests pass incrementally

6. VALIDATION CHECKPOINTS
   - After fixture: can create test data?
   - After basic tests: do core assertions work?
   - After all tests: does coverage meet 85%?

Output a detailed, step-by-step implementation plan with:
- Code structure outlines (not full code, just structure)
- Import requirements
- Fixture data specifications
- Test method signatures and assertions
- Coverage validation approach
"""

print("Calling Ollama to create implementation plan...\n")
response = ollama.generate(
    model="qwen3.5-35b:reasoning",
    prompt=prompt,
    stream=False
)

plan = response.get("response", "").strip()

if not plan or len(plan) < 1000:
    print("✗ Failed to generate plan")
    sys.exit(1)

# Write plan to file
write_file("docs/TEST_IMPLEMENTATION_PLAN.md", f"# Test Implementation Plan\n\n{plan}")
print("✓ Implementation plan written to docs/TEST_IMPLEMENTATION_PLAN.md\n")

# Commit
git_commit(
    ["docs/TEST_IMPLEMENTATION_PLAN.md"],
    "docs: Test implementation plan for suggested-discussions (agent-generated)"
)

print("✓ Plan committed to git\n")

# Show summary
print("="*70)
print("Implementation plan ready for execution")
print("="*70)
print("\nNext steps:")
print("1. Review: docs/TEST_IMPLEMENTATION_PLAN.md")
print("2. Use plan to implement: backend/tests/test_suggestion_coverage_complete.py")
print("3. Run tests: pytest backend/tests/test_suggestion_coverage_complete.py")
print()
