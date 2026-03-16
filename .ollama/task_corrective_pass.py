#!/usr/bin/env python3
"""
Corrective Pass Orchestrator: Fix 4 specific issues in suggested-discussions.
Uses Ollama agents with small, focused tasks for 100% working behavior.
"""

import ollama
from pathlib import Path
import subprocess

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

# 4 Corrective Pass Tasks
TASKS = [
    {
        "id": "A",
        "name": "Fix News UI Rendering Bug",
        "file": "administration-tool/static/news.js",
        "issue": "suggested-discussions entries append to wrong list (related instead of suggested)",
    },
    {
        "id": "B",
        "name": "Truthful Ranking Docs/Postman",
        "file": "postman/WorldOfShadows_API.postman_collection.json + docs/",
        "issue": "docs/Postman claim 'Same category' reason, but real logic uses tag matches + recency",
    },
    {
        "id": "C",
        "name": "Wiki Route Shape Alignment",
        "file": "backend/app/api/v1/wiki_routes.py + postman + docs/",
        "issue": "docs/Postman may use /slug route but code uses /id route",
    },
    {
        "id": "D",
        "name": "Focused Backend Tests",
        "file": "backend/tests/test_narrow_followup.py",
        "issue": "need tests for: duplicate exclusion, hidden/inaccessible exclusion, deterministic ordering, truthful labels",
    },
]

def inspect_file(file_path: str, question: str) -> str:
    """Have Ollama inspect a file and answer a question."""
    try:
        full_path = PROJECT_ROOT / file_path
        if not full_path.exists():
            return f"File not found: {file_path}"

        with open(full_path) as f:
            content = f.read()

        # Limit to first 3000 chars for analysis
        content_sample = content[:3000]

        prompt = f"""Inspect this code snippet and answer: {question}

FILE: {file_path}
CONTENT (first 3000 chars):

{content_sample}

Answer concisely (1-2 sentences), pointing to specific code/line if possible."""

        response = ollama.generate(
            model="gemma3:latest",
            prompt=prompt,
            stream=False,
        )
        return response.get("response", "").strip()

    except Exception as e:
        return f"Error: {str(e)[:100]}"


def main():
    """Execute corrective pass with small, focused tasks."""

    print("\n" + "="*70)
    print("  CORRECTIVE PASS ORCHESTRATOR")
    print("="*70)
    print("\nTASK A: Fix News UI Rendering Bug")
    print("Task B: Truthful Ranking Docs/Postman")
    print("Task C: Wiki Route Shape Alignment")
    print("Task D: Focused Backend Tests")
    print("\nInspecting current state...\n")

    # Step 1: Inspect news.js for the bug
    print("─" * 70)
    print("TASK A: News UI Bug Analysis")
    print("─" * 70)

    news_js_issue = inspect_file(
        "administration-tool/static/news.js",
        "Where does suggested-discussions get appended? Is it to the correct list or wrong list (related)?"
    )
    print(f"\nFinding: {news_js_issue}\n")

    # Step 2: Inspect ranking logic
    print("─" * 70)
    print("TASK B: Ranking Logic Analysis")
    print("─" * 70)

    forum_service = inspect_file(
        "backend/app/services/forum_service.py",
        "What is the actual ranking logic for suggested threads? What signals are used?"
    )
    print(f"\nRanking logic: {forum_service}\n")

    # Step 3: Inspect Wiki route
    print("─" * 70)
    print("TASK C: Wiki Route Analysis")
    print("─" * 70)

    wiki_route = inspect_file(
        "backend/app/api/v1/wiki_routes.py",
        "What is the exact route for suggested-threads endpoint? Does it use /id or /slug?"
    )
    print(f"\nWiki route: {wiki_route}\n")

    # Step 4: Check existing tests
    print("─" * 70)
    print("TASK D: Current Test Coverage")
    print("─" * 70)

    existing_tests = inspect_file(
        "backend/tests/test_narrow_followup.py",
        "What tests already exist? Are there tests for duplicate exclusion, hidden exclusion, deterministic ordering?"
    )
    print(f"\nExisting tests: {existing_tests}\n")

    print("="*70)
    print("  ANALYSIS COMPLETE - Ready for fixes")
    print("="*70)
    print("\nNext: Create Ollama agents for each fix")
    print("Task A: Fix news.js bug")
    print("Task B: Update Postman and docs")
    print("Task C: Align Wiki docs with real route")
    print("Task D: Add focused tests\n")

    return True


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
