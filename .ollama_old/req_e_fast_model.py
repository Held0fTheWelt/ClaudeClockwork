#!/usr/bin/env python3
"""
REQ E: Generate pytest tests using Phase 5 optimization.
Uses gemma3:latest (fast, 3.3GB) instead of large models to avoid memory exhaustion.
Phase 5 showed that large models exhaust 54GB system RAM, causing timeouts.
"""

import ollama
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

def generate_tests():
    """Generate comprehensive pytest test file using fast model."""

    prompt = """Generate a complete, production-ready pytest test file for the suggested-discussions feature.

FILE: backend/tests/test_suggestion_coverage_complete.py

TEST COVERAGE (all 10 areas):
1. NEWS RANKING - by tag matches and recency
2. WIKI RANKING - by tag matches and recency
3. EXCLUDE PRIMARY - primary discussion not suggested
4. EXCLUDE RELATED - manually related not suggested
5. EXCLUDE HIDDEN - deleted/hidden threads excluded
6. DETERMINISTIC - same input = same output
7. TRUTHFUL LABELS - reason labels grounded (no hallucination)
8. DISTINCTION - primary vs related vs suggested
9. MANAGEMENT UI - admin API endpoints
10. API ENDPOINT - response format and pagination

Code structure:
```python
import pytest
from datetime import datetime, timezone
from app.extensions import db
from app.models import User, Forum, Thread, Tag, News, WikiArticle, Discussion

@pytest.fixture
def suggestion_test_data(app):
    \"\"\"Create test data for suggestions testing.\"\"\"
    # Create test users, forums, threads, tags, news, wiki
    return {...}

class TestNewsSuggestionsRanking:
    def test_rank_by_tag_matches(self, client, suggestion_test_data): ...
    def test_rank_by_recency(self, client, suggestion_test_data): ...
    def test_multiple_tags(self, client, suggestion_test_data): ...

class TestWikiSuggestionsRanking:
    def test_rank_by_tag_matches(self, client, suggestion_test_data): ...
    def test_rank_by_recency(self, client, suggestion_test_data): ...

class TestSuggestionExclusions:
    def test_exclude_primary_thread(self, client, suggestion_test_data): ...
    def test_exclude_related_threads(self, client, suggestion_test_data): ...
    def test_exclude_hidden_threads(self, client, suggestion_test_data): ...
    def test_exclude_deleted_threads(self, client, suggestion_test_data): ...

class TestSuggestionDeterminism:
    def test_deterministic_ordering(self, client, suggestion_test_data): ...
    def test_deterministic_with_tags_tie(self, client, suggestion_test_data): ...

class TestSuggestionLabels:
    def test_grounded_tag_match_label(self, client, suggestion_test_data): ...
    def test_grounded_recency_label(self, client, suggestion_test_data): ...
    def test_label_accuracy(self, client, suggestion_test_data): ...

class TestThreadTypeDistinction:
    def test_primary_thread(self, client, suggestion_test_data): ...
    def test_related_threads(self, client, suggestion_test_data): ...
    def test_suggested_threads(self, client, suggestion_test_data): ...

class TestManagementAPI:
    def test_admin_fetch_suggestions(self, client, admin_headers, suggestion_test_data): ...
    def test_admin_pin_suggestion(self, client, admin_headers, suggestion_test_data): ...

class TestPublicAPI:
    def test_api_endpoint_200(self, client, suggestion_test_data): ...
    def test_api_pagination(self, client, suggestion_test_data): ...
    def test_api_response_schema(self, client, suggestion_test_data): ...
```

Generate the FULL, COMPLETE, EXECUTABLE pytest file with all classes and methods.
NO PLACEHOLDERS. NO SKIPPED TESTS. ALL ASSERTIONS MUST BE REAL.
Valid Python only, ready to run."""

    print("\n" + "="*70)
    print("  REQ E: Generate Tests (Fast Model - Avoiding Memory Exhaustion)")
    print("="*70)
    print("  Model: gemma3:latest (3.3GB, fast response)")
    print("  Status: Calling Ollama...\n")

    try:
        response = ollama.generate(
            model="gemma3:latest",
            prompt=prompt,
            stream=False,
        )
        code = response.get("response", "").strip()

        if code and len(code) > 500:  # Sanity check
            test_file = PROJECT_ROOT / "backend/tests/test_suggestion_coverage_complete.py"
            test_file.write_text(code)
            print(f"✓ Test file generated: {len(code)} bytes")
            print(f"  Location: {test_file}")
            print(f"\nFirst 500 chars:\n")
            print(code[:500])
            return True
        else:
            print(f"✗ Invalid response: {len(code) if code else 0} bytes")
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)[:200]}")
        return False


if __name__ == "__main__":
    import sys
    success = generate_tests()
    sys.exit(0 if success else 1)
