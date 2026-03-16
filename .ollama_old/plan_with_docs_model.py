#!/usr/bin/env python3
"""Use docs model (which works fast) to create test plan."""

import ollama
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from helper_functions import write_file, git_commit

prompt = """Write markdown documentation for a test implementation guide.

Topic: How to implement pytest tests for suggested-discussions feature

Sections:
1. Fixture Setup - what test data is needed
2. Test Class Organization - how to organize 5 test classes
3. Test Methods - what each test should verify
4. Assertions - what to check in each test
5. Coverage - how to achieve 85%+ coverage

Keep it concise and actionable."""

print("Creating plan with docs model...\n")

response = ollama.generate(
    model="qwen3.5-35b:docs",
    prompt=prompt,
    stream=False
)

plan = response.get("response", "").strip()

if plan and len(plan) > 500:
    write_file("docs/TEST_IMPLEMENTATION_PLAN.md", f"# Test Implementation Guide\n\n{plan}")
    git_commit(["docs/TEST_IMPLEMENTATION_PLAN.md"], "docs: test implementation guide (agent-generated)")
    print("✓ Plan created and committed\n")
    print(plan[:1000])
else:
    print("Empty response")
    sys.exit(1)
