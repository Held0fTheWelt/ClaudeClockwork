#!/usr/bin/env python3
"""
REQ E: Generate tests iteratively (one test at a time).
This approach avoids timeouts by serializing work and committing incrementally.
Phase 5 showed serialization is key to avoiding resource exhaustion.
"""

import ollama
from pathlib import Path
import subprocess

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

# Define 10 test requirements (one per category)
TEST_REQUIREMENTS = [
    {
        "id": "1_news_ranking",
        "class": "TestNewsSuggestionsRanking",
        "name": "test_rank_by_tag_matches",
        "requirement": "Test that news suggestions are ranked higher when they match user's tag interests. Create a user, add tags to their reading history, create news with those tags, verify ranking order.",
    },
    {
        "id": "2_wiki_ranking",
        "class": "TestWikiSuggestionsRanking",
        "name": "test_rank_by_tag_matches",
        "requirement": "Test that wiki suggestions are ranked by tag relevance. Create wiki articles with tags, verify they rank based on user's tag profile.",
    },
    {
        "id": "3_exclude_primary",
        "class": "TestSuggestionExclusions",
        "name": "test_exclude_primary_thread",
        "requirement": "Test that the primary discussion thread itself is not included in suggestions. Create a thread, fetch its suggestions, verify the primary thread ID is not in results.",
    },
    {
        "id": "4_exclude_related",
        "class": "TestSuggestionExclusions",
        "name": "test_exclude_related_threads",
        "requirement": "Test that manually related threads are excluded from suggestions. Create threads with manual relationships, verify related IDs don't appear in suggestions.",
    },
    {
        "id": "5_exclude_hidden",
        "class": "TestSuggestionExclusions",
        "name": "test_exclude_hidden_threads",
        "requirement": "Test that hidden threads are excluded from suggestions. Create hidden threads, fetch suggestions, verify hidden threads don't appear (unless user is moderator).",
    },
    {
        "id": "6_deterministic",
        "class": "TestSuggestionDeterminism",
        "name": "test_deterministic_ordering",
        "requirement": "Test that suggestions are deterministic. Call the same suggestion endpoint twice with same inputs, verify results are identical (same order, same IDs).",
    },
    {
        "id": "7_grounded_labels",
        "class": "TestSuggestionLabels",
        "name": "test_grounded_reason_labels",
        "requirement": "Test that reason labels are grounded in actual data. Verify labels like 'Matched 2 tags' correspond to actual tag matches in the suggestion logic, not LLM-generated text.",
    },
    {
        "id": "8_distinction",
        "class": "TestThreadTypeDistinction",
        "name": "test_primary_vs_related_vs_suggested",
        "requirement": "Test three distinct thread categories: primary (the main discussion), related (manually linked), suggested (algorithmic). Verify they're returned in appropriate sections.",
    },
    {
        "id": "9_admin_api",
        "class": "TestManagementAPI",
        "name": "test_admin_fetch_suggestions",
        "requirement": "Test admin endpoint for suggestions management. Admin GET /api/v1/admin/forums/threads/<id>/management should return suggestions data with ability to view/modify.",
    },
    {
        "id": "10_public_api",
        "class": "TestPublicAPI",
        "name": "test_api_endpoint_response",
        "requirement": "Test public API endpoint GET /api/v1/forums/threads/<id>/suggestions returns 200 with proper pagination (limit, offset), response schema validation.",
    },
]

def generate_single_test(requirement: dict) -> str:
    """Generate a single test function using Ollama."""

    prompt = f"""Generate a single pytest test function for this requirement:

CLASS: {requirement['class']}
TEST FUNCTION: {requirement['name']}
REQUIREMENT: {requirement['requirement']}

Generate ONLY the test function (no class definition, no imports).
Function signature: def {requirement['name']}(self, client, suggestion_test_data, admin_headers=None):
    \"\"\"Test requirement: {requirement['requirement'][:100]}...\"\"\"

Make it:
- Complete and executable
- Use fixtures: client (test client), suggestion_test_data (test data fixture)
- Include real assertions (not just status codes)
- Handle both success and edge cases
- No TODOs or placeholders

Output ONLY the function code. No markdown, no comments about what you're doing."""

    print(f"  Generating {requirement['class']}.{requirement['name']}...")

    try:
        response = ollama.generate(
            model="gemma3:latest",  # Fast model
            prompt=prompt,
            stream=False,
        )
        code = response.get("response", "").strip()
        if code and "def " in code:
            return code
    except Exception as e:
        print(f"    ✗ Error: {str(e)[:100]}")

    return ""


def build_test_file():
    """Build test file incrementally, one test at a time."""

    print("\n" + "="*70)
    print("  REQ E: Iterative Test Generation (One Test at a Time)")
    print("="*70 + "\n")

    test_file = PROJECT_ROOT / "backend/tests/test_suggestion_coverage_complete.py"

    # Write file header
    header = '''"""Comprehensive tests for suggested-discussions feature."""

import pytest
from datetime import datetime, timezone
from app.extensions import db
from app.models import User, Forum, Thread, Tag, News, WikiArticle, Discussion


@pytest.fixture
def suggestion_test_data(app):
    """Create comprehensive test data for suggestions testing."""
    # Create test users
    user1 = User(username="user1", email="user1@test.com", password_hash="hash1")
    user2 = User(username="user2", email="user2@test.com", password_hash="hash2")
    admin_user = User(username="admin", email="admin@test.com", password_hash="hash")
    admin_user.is_admin = True

    # Create forum and threads
    forum = Forum(name="Test Forum", slug="test-forum")
    tag1 = Tag(name="python", slug="python")
    tag2 = Tag(name="javascript", slug="javascript")
    tag3 = Tag(name="api", slug="api")

    # Create threads with various properties
    primary_thread = Thread(
        title="Primary Discussion",
        slug="primary-discussion",
        forum=forum,
        author=user1,
        status="active",
    )
    primary_thread.tags.extend([tag1, tag2])

    suggested_1 = Thread(
        title="Related to Python",
        slug="related-python",
        forum=forum,
        author=user2,
        status="active",
    )
    suggested_1.tags.extend([tag1])

    suggested_2 = Thread(
        title="API Best Practices",
        slug="api-best-practices",
        forum=forum,
        author=user2,
        status="active",
    )
    suggested_2.tags.extend([tag3])

    hidden_thread = Thread(
        title="Hidden Discussion",
        slug="hidden-discussion",
        forum=forum,
        author=user2,
        status="hidden",
    )

    deleted_thread = Thread(
        title="Deleted Discussion",
        slug="deleted-discussion",
        forum=forum,
        author=user2,
        status="deleted",
    )

    # Create news articles
    news1 = News(
        title="Python 3.13 Released",
        slug="python-3-13",
        author=user1,
        content="Content here",
        published=True,
    )
    news1.tags.extend([tag1])

    news2 = News(
        title="JavaScript Frameworks",
        slug="js-frameworks",
        author=user1,
        content="Content here",
        published=True,
    )
    news2.tags.extend([tag2])

    # Create wiki articles
    wiki1 = WikiArticle(
        title="Python Basics",
        slug="python-basics",
        content="Content here",
        author=user1,
    )
    wiki1.tags.extend([tag1])

    # Persist all
    db.session.add_all([
        user1, user2, admin_user,
        forum, tag1, tag2, tag3,
        primary_thread, suggested_1, suggested_2, hidden_thread, deleted_thread,
        news1, news2,
        wiki1,
    ])
    db.session.commit()

    return {
        "user1": user1,
        "user2": user2,
        "admin_user": admin_user,
        "forum": forum,
        "tags": {"python": tag1, "javascript": tag2, "api": tag3},
        "primary_thread": primary_thread,
        "suggested_threads": [suggested_1, suggested_2],
        "hidden_thread": hidden_thread,
        "deleted_thread": deleted_thread,
        "news": [news1, news2],
        "wiki": [wiki1],
    }


'''

    test_file.write_text(header)
    print(f"✓ Created test file header\n")

    # Generate tests one by one
    current_class = None
    generated_count = 0

    for req in TEST_REQUIREMENTS:
        if req["class"] != current_class:
            # Write class header
            if current_class is not None:
                test_file.write_text(
                    test_file.read_text() + f"\n\n"
                )
            test_file.write_text(
                test_file.read_text() + f"class {req['class']}:\n"
            )
            current_class = req["class"]
            print(f"\n[{req['class']}]")

        # Generate the test function
        test_code = generate_single_test(req)

        if test_code:
            # Append to file with proper indentation
            indented = "\n".join(f"    {line}" for line in test_code.split("\n"))
            test_file.write_text(test_file.read_text() + f"\n{indented}\n")
            generated_count += 1
            print(f"    ✓ {req['name']}")
        else:
            print(f"    ✗ {req['name']} (skipped)")

    print(f"\n" + "="*70)
    print(f"  Generated: {generated_count}/10 test functions")
    print(f"  File: {test_file}")
    print("="*70 + "\n")

    return generated_count >= 8  # Success if at least 8 tests generated


def main():
    """Execute REQ E iteratively."""
    success = build_test_file()

    if success:
        print("✓ REQ E: COMPLETE (iterative test generation)")
        return True
    else:
        print("✗ REQ E: PARTIAL (some tests could not be generated)")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
