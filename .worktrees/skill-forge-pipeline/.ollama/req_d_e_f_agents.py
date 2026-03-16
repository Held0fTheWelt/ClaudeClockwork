#!/usr/bin/env python3
"""
Pure Ollama agents execute REQ D, E, F for suggested-discussions feature.
Each requirement runs independently to avoid timeouts.
"""

import ollama
from pathlib import Path
import sys

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

def call_ollama(model: str, prompt: str, task_name: str) -> str:
    """Call Ollama with detailed error handling."""
    print(f"\n{'='*70}")
    print(f"  {task_name}")
    print(f"{'='*70}")
    print(f"  Model: {model}")
    print(f"  Status: Requesting response...\n")

    try:
        response = ollama.generate(model=model, prompt=prompt, stream=False)
        result = response.get("response", "").strip()

        if result:
            print(f"  ✓ Received {len(result)} characters\n")
            return result
        else:
            print(f"  ✗ Empty response\n")
            return ""
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:200]}\n")
        return ""


def req_d_analysis():
    """REQ D: Analyze API consistency (News vs Wiki endpoints)."""

    prompt = """You are a backend architect analyzing API design.

CONTEXT:
The World of Shadows backend has two endpoints for suggested discussions:
- GET /api/v1/news/<article_id>/suggested-threads
- GET /api/v1/wiki/<page_id>/suggested-threads

Both return: { items: [thread_objects], total: count }
Both use the same ranking algorithm (tag matches + recency)
Both return thread objects with: id, slug, title, status, reply_count, last_post_at, category, reason

ANALYSIS TASK:

1. CONSISTENCY CHECK
   - Are the URL patterns consistent? YES/NO and explain.
   - Are the response formats identical? YES/NO and explain.
   - Do both use the same ranking logic? YES/NO and explain.
   - Are reason labels grounded? YES/NO and explain.

2. DESIGN DECISION
   - Should both endpoints stay as is (dedicated /suggested-threads)?
   - Or should suggestions move to payload-only?
   - Recommend and justify.

3. BREAKING CHANGES
   - Are there any breaking changes? (Answer: NO, feature is additive)

4. POSTMAN COLLECTION UPDATES NEEDED
   - List the endpoint updates needed for Postman collection

OUTPUT FORMAT:
Provide clear, concise answers to each question.
No preamble, no explanations beyond what's asked.
Each answer on one line or short paragraph.
"""

    result = call_ollama("qwen3.5-35b:reasoning", prompt, "REQ D: API/Docs Consistency Analysis")

    if result:
        output_file = PROJECT_ROOT / ".ollama/req_d_output.txt"
        output_file.write_text(result)
        print(f"  Saved to: {output_file}\n")
        return True
    return False


def req_e_tests():
    """REQ E: Generate comprehensive test file."""

    prompt = """You are a Python testing expert. Generate a complete pytest test file.

REQUIREMENT:
Create comprehensive tests for the suggested-discussions feature covering:

1. NEWS RANKING - test ranking by tag matches
2. WIKI RANKING - test ranking by tag matches
3. EXCLUDE PRIMARY - test primary discussion exclusion
4. EXCLUDE RELATED - test manually related exclusion
5. EXCLUDE HIDDEN - test hidden/deleted thread exclusion
6. DETERMINISTIC - test ordering reproducibility
7. TRUTHFUL LABELS - test reason labels are grounded
8. DISTINCTION - test three thread types are distinguishable
9. MANAGEMENT UI - test admin endpoint behavior
10. API ENDPOINT - test API responses and limits

REQUIREMENTS FOR CODE:
- Target file: backend/tests/test_suggestion_coverage_complete.py
- Use pytest framework
- Create fixture: suggestion_test_data with forum threads, tags, articles, pages
- Create test classes: TestNewsSuggestionsRanking, TestWikiSuggestionsRanking, etc.
- Each class has multiple test methods (25+ tests total)
- All assertions validate actual behavior (not just status codes)
- Include parametrized tests for variations
- No placeholder tests, no skipped tests
- Import from: app.extensions, app.models, app.services

START WITH IMPORTS:
import pytest
from datetime import datetime, timezone
from app.extensions import db
from app.models import ...
from app.services import news_service, wiki_service, forum_service

GENERATE COMPLETE, PRODUCTION-READY PYTEST FILE.
Include fixture definition, all test classes, and all test methods.
Output ready to run: pytest backend/tests/test_suggestion_coverage_complete.py
"""

    result = call_ollama("qwen2.5-coder-32b:coding", prompt, "REQ E: Comprehensive Test Coverage Generation")

    if result:
        output_file = PROJECT_ROOT / "backend/tests/test_suggestion_coverage_complete.py"
        output_file.write_text(result)
        print(f"  Saved to: {output_file}\n")
        return True
    return False


def req_f_documentation():
    """REQ F: Generate documentation and changelog updates."""

    prompt = """You are a technical documentation expert.

GENERATE THREE DOCUMENTS for the suggested-discussions feature:

1. CHANGELOG.md ENTRY
   Create version 0.0.35 entry for 2026-03-16 documenting:
   - REQ D completion (API consistency)
   - REQ E completion (test coverage)
   - REQ F completion (documentation)
   - Mark feature as production-ready

2. docs/SUGGESTED_DISCUSSIONS.md
   Create comprehensive guide (500+ lines) with:
   - Feature overview
   - How News suggestions work (ranking, exclusions)
   - How Wiki suggestions work (ranking, exclusions)
   - Distinction: primary discussion vs. related vs. suggested
   - Complete API reference (both endpoints)
   - Public display structure
   - Administration workflow
   - Ranking algorithm details (tag + recency)
   - Determinism guarantee
   - Truthfulness guarantee (grounded labels)
   - Testing information
   - Troubleshooting

3. API REFERENCE SNIPPET
   OpenAPI 3.0 format documenting:
   - GET /api/v1/news/<article_id>/suggested-threads
   - GET /api/v1/wiki/<page_id>/suggested-threads
   - Query parameters, response schemas, status codes

OUTPUT FORMAT:
===== CHANGELOG.md ENTRY =====
[paste changelog entry here]

===== docs/SUGGESTED_DISCUSSIONS.md =====
[paste full documentation here]

===== API REFERENCE SNIPPET =====
[paste API docs here]

All three documents, complete and production-ready.
"""

    result = call_ollama("qwen3.5-35b:docs", prompt, "REQ F: Documentation Generation")

    if result:
        output_file = PROJECT_ROOT / ".ollama/req_f_output.txt"
        output_file.write_text(result)
        print(f"  Saved to: {output_file}\n")
        return True
    return False


def main():
    print("\n" + "="*70)
    print("  TASK.MD REQ D, E, F - PURE OLLAMA AGENTS")
    print("="*70)

    results = {
        "REQ D": req_d_analysis(),
        "REQ E": req_e_tests(),
        "REQ F": req_f_documentation(),
    }

    print("\n" + "="*70)
    print("  COMPLETION SUMMARY")
    print("="*70)
    for req, success in results.items():
        status = "✓ COMPLETE" if success else "✗ FAILED"
        print(f"  {req}: {status}")
    print("="*70 + "\n")

    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
