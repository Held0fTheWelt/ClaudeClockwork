#!/usr/bin/env python3
"""Minimal test implementation plan via agent."""

import ollama
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from helper_functions import write_file, git_commit

# Very simple prompt
prompt = """Create an implementation checklist for pytest tests (3 areas):

1. SETUP
   - [ ] Import pytest, datetime, db, models, services
   - [ ] Create suggestion_test_data fixture with forums, threads, tags
   - [ ] Create test categories: News, Wiki, Exclusions, Ranking, API

2. TEST CLASSES
   - [ ] TestNewsSuggestions (3 methods)
   - [ ] TestWikiSuggestions (3 methods)
   - [ ] TestExclusions (4 methods - primary, related, hidden, deleted)
   - [ ] TestRanking (3 methods - deterministic, labels, distinction)
   - [ ] TestAPI (5 methods - endpoints, limits, errors)

3. VALIDATION
   - [ ] All tests use assertions on actual behavior
   - [ ] Coverage >= 85%
   - [ ] No syntax errors
   - [ ] All 10 areas covered

Format as markdown checklist."""

print("Generating checklist...\n")

response = ollama.generate(
    model="qwen3.5-35b:taskrunner",
    prompt=prompt,
    stream=False
)

plan = response.get("response", "").strip()

if plan and len(plan) > 300:
    content = f"""# Test Implementation Checklist

## Overview
Implementation guide for backend/tests/test_suggestion_coverage_complete.py

{plan}

## Execution Notes
- Follow checklist in order
- Run pytest after each section
- Verify coverage increases
- Commit after all tests pass
"""
    write_file("docs/TEST_IMPLEMENTATION_PLAN.md", content)
    git_commit(["docs/TEST_IMPLEMENTATION_PLAN.md"], "docs: test implementation checklist")
    print("✓ Checklist created and committed\n")
    
    # Show it
    print(content[:800])
else:
    print("Failed - empty response")
    sys.exit(1)
