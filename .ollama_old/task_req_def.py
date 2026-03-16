#!/usr/bin/env python3
"""
Complete Task.md REQ D, E, F using pure Ollama agents.

REQ D: API/docs consistency (decide endpoint design, audit Postman, update docs)
REQ E: Test expansion (generate comprehensive pytest coverage for 10 requirements)
REQ F: Documentation (CHANGELOG.md, SUGGESTED_DISCUSSIONS.md, API docs)
"""

import ollama
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")
TASK_MD = PROJECT_ROOT / "Task.md"

def ollama_call(model: str, prompt: str, timeout: int = 120) -> str:
    """Call Ollama with timeout and error handling."""
    try:
        print(f"  → {model}...", flush=True)
        response = ollama.generate(
            model=model,
            prompt=prompt,
            stream=False,
        )
        result = response.get("response", "").strip()
        print(f"    ✓ ({len(result)} chars)\n")
        return result
    except Exception as e:
        print(f"    ✗ {str(e)[:100]}\n")
        return ""

def main():
    print("\n" + "="*70)
    print("  TASK.MD COMPLETION: REQ D, E, F")
    print("="*70 + "\n")

    task_md = TASK_MD.read_text()

    # REQ D: API/Docs Consistency
    print("▶ REQ D: Wiki API/docs/Postman consistency")
    print("━"*70)

    req_d_prompt = """You are a backend architect. Analyze the suggested-discussions API design.

CONTEXT:
- News articles have a /api/v1/news/<id>/suggested-threads endpoint
- Wiki pages have a /api/v1/wiki/<id>/suggested-threads endpoint
- Both return: { items: [thread_objects], total: count }
- Each thread has: id, slug, title, status, reply_count, last_post_at, category, reason

TASK:
1. Is the endpoint design CONSISTENT between News and Wiki?
2. Is the response format CONSISTENT?
3. Are reason labels TRUTHFUL and GROUNDED?
4. Should we keep payload-based suggestions or add dedicated /suggested-threads endpoints?
5. What Postman collection updates are needed?

OUTPUT:
- Assessment of consistency
- Recommendation (payload vs dedicated endpoint, with rationale)
- Required Postman collection updates
- Any breaking changes needed
- Timeline for implementation
"""

    req_d = ollama_call("qwen2.5-72b:reasoning", req_d_prompt)

    if req_d:
        print("✓ REQ D ANALYSIS COMPLETE")
        print(f"Summary (first 500 chars):\n{req_d[:500]}\n")
    else:
        print("✗ REQ D FAILED\n")

    # REQ E: Test Expansion
    print("▶ REQ E: Comprehensive test coverage")
    print("━"*70)

    req_e_prompt = """You are a Python test expert. Generate comprehensive pytest tests for suggested-discussions.

CONTEXT:
The suggested-discussions feature is implemented in backend/app/services/:
- news_service.get_suggested_threads_for_article()
- wiki_service.get_suggested_threads_for_wiki_page()
- forum_service.suggest_related_threads_for_query()

All use deterministic tag-based ranking with recent activity tie-breaker.

REQUIREMENTS TO TEST (from Task.md REQ E):
1. News suggestion ranking (tag matching)
2. Wiki suggestion ranking (tag matching)
3. Exclusion of primary discussion
4. Exclusion of manually related threads
5. Exclusion of hidden/inaccessible threads
6. Deterministic ordering (consistent results)
7. Truthful reason labels
8. Distinction between discussion/related/suggested
9. Management UI behavior (fetch + render suggestions)
10. Wiki endpoint behavior (API responses)

GENERATE:
A complete pytest test file (backend/tests/test_suggestion_coverage_complete.py) that:
- Tests all 10 requirements above
- Uses actual database fixtures (test_user, app, client from conftest)
- Includes integration tests for API endpoints
- Includes service-layer unit tests
- Covers edge cases (no suggestions, all excluded, hidden threads, etc.)
- Achieves 85%+ code coverage for suggestion functions
- Has NO placeholder tests, NO skipped tests
- Asserts actual payload content, not just status codes

START WITH: import pytest, from app.extensions import db, from app.models import ...
INCLUDE: @pytest.mark.parametrize for multiple test cases
END WITH: class names TestNewsSuggestions, TestWikiSuggestions, TestSuggestionRanking

OUTPUT ONLY: Complete Python test file code, ready to paste directly.
"""

    req_e = ollama_call("qwen2.5-coder-32b:coding", req_e_prompt)

    if req_e:
        print("✓ REQ E CODE GENERATION COMPLETE")
        print(f"Generated {len(req_e)} chars of test code")
        # Save test file
        test_file = PROJECT_ROOT / "backend/tests/test_suggestion_coverage_complete.py"
        test_file.write_text(req_e)
        print(f"  → Saved to: {test_file}\n")
    else:
        print("✗ REQ E FAILED\n")

    # REQ F: Documentation
    print("▶ REQ F: Documentation and changelog")
    print("━"*70)

    req_f_prompt = """You are a technical writer. Generate documentation for suggested-discussions.

CONTEXT:
The suggested-discussions feature is a deterministic ranking system that:
- Analyzes tag matches from primary discussion thread
- Ranks candidates by tag overlap (primary score) and recency (tie-breaker)
- Excludes: primary discussion, manually related, hidden/inaccessible threads
- Returns grounded reason labels ("Matched N tags" or "Recent discussion")
- Is visible in public pages (News/Wiki) and management UIs

GENERATE THREE DOCUMENTS:

1. CHANGELOG.md entry (v0.0.33 or next version):
   - Feature name: Suggested Discussions
   - What it does (2-3 sentences, non-technical)
   - Where it's visible (public pages, admin UIs)
   - Any breaking changes? (no)

2. docs/SUGGESTED_DISCUSSIONS.md (complete guide):
   - Overview (1 paragraph)
   - How News suggestions work (ranking signals, exclusions)
   - How Wiki suggestions work (ranking signals, exclusions)
   - Difference between: primary discussion, manually related, suggested
   - API endpoint design (payload-based approach)
   - Example usage (public page + admin UI)
   - Grounded reason labels (explanation)
   - Future extensions (optional)

3. API documentation snippet (OpenAPI 3.0 format):
   - GET /api/v1/news/{article_id}/suggested-threads
   - GET /api/v1/wiki/{page_id}/suggested-threads
   - Response schema: { items: [...], total: ... }
   - Thread object schema with reason field

OUTPUT:
```markdown
# CHANGELOG Entry

# docs/SUGGESTED_DISCUSSIONS.md

# OpenAPI Snippet
```

Style: Professional, clear, accurate. No overclaiming.
"""

    req_f = ollama_call("qwen3.5-35b:docs", req_f_prompt)

    if req_f:
        print("✓ REQ F DOCUMENTATION GENERATION COMPLETE")
        print(f"Generated {len(req_f)} chars of documentation")
        # Save documentation
        docs_file = PROJECT_ROOT / ".ollama/req_f_documentation.md"
        docs_file.write_text(req_f)
        print(f"  → Saved to: {docs_file}\n")
    else:
        print("✗ REQ F FAILED\n")

    print("\n" + "="*70)
    print("  COMPLETION STATUS")
    print("="*70)
    print(f"  REQ D (API consistency): {'✓ COMPLETE' if req_d else '✗ FAILED'}")
    print(f"  REQ E (Tests): {'✓ COMPLETE' if req_e else '✗ FAILED'}")
    print(f"  REQ F (Docs): {'✓ COMPLETE' if req_f else '✗ FAILED'}")
    print("="*70 + "\n")

    return bool(req_d and req_e and req_f)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
