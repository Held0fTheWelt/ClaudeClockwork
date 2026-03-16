#!/usr/bin/env python3
"""Quick test implementation plan."""

import ollama
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from helper_functions import write_file, git_commit

# Read test plan
plan_text = Path("docs/TEST_PLAN_SUGGESTED_DISCUSSIONS.md").read_text()

# Simpler prompt with faster model
prompt = f"""Based on this test plan:

{plan_text[:2000]}

Create a CONCISE implementation plan for backend/tests/test_suggestion_coverage_complete.py:

1. IMPORTS & FIXTURE
2. TEST CLASSES (one per area)
3. EACH CLASS: 2-3 test methods
4. ASSERTIONS to validate requirements
5. COVERAGE APPROACH

Keep it structured, actionable, brief."""

print("Generating implementation plan...\n")

# Use faster, smaller model
response = ollama.generate(
    model="qwen3.5-35b:planner",
    prompt=prompt,
    stream=False
)

plan = response.get("response", "").strip()

if plan and len(plan) > 500:
    write_file("docs/TEST_IMPLEMENTATION_PLAN.md", f"# Test Implementation Plan\n\n{plan}")
    git_commit(["docs/TEST_IMPLEMENTATION_PLAN.md"], "docs: test implementation plan")
    print("✓ Plan saved and committed\n")
else:
    print("Empty plan")
    sys.exit(1)
