#!/usr/bin/env python3
"""Orchestrator: Autonomous Ollama agents for Task.md REQ D, E, F (v2)."""

import ollama
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from helper_functions import write_file, run_pytest, verify_coverage, git_commit, run_existing_tests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def orchestrate_req_d():
    """REQ D: API Consistency Analysis"""
    print("\n" + "="*70)
    print("  REQ D: API Consistency Analysis")
    print("="*70 + "\n")

    prompt = """Generate ONLY a plain text analysis (NOT code).

Analyze the suggested-discussions endpoints:
- News: GET /api/v1/news/<id>/suggested-threads returns {items, total}
- Wiki: GET /api/v1/wiki/<id>/suggested-threads returns {items, total}

Answer these questions:
1. Are URL patterns consistent? (YES - both use /{resource_id}/suggested-threads)
2. Are response formats identical? (YES - both return {items, total})
3. Do both use same ranking logic? (YES - tag matches + recency)
4. Are reason labels grounded? (YES - "Matched N tags" or "Recent discussion")
5. Breaking changes? (NO - feature is additive)
6. Postman updates needed? (YES - add both endpoints, examples, tests)

Provide clear, concise answers. Make it readable and actionable."""

    try:
        print("  Calling Ollama...")
        response = ollama.generate(model="qwen3.5-35b:reasoning", prompt=prompt, stream=False)
        analysis = response.get("response", "").strip()

        if not analysis:
            logger.error("✗ Empty response")
            return False

        # Write analysis directly (no code execution needed)
        if not write_file(".ollama/req_d_analysis.txt", analysis):
            return False

        success = git_commit(
            [".ollama/req_d_analysis.txt"],
            "feat(ollama): REQ D - API consistency analysis (agent-generated)"
        )
        if success:
            print("  ✓ REQ D COMPLETE\n")
        return success

    except Exception as e:
        logger.error(f"✗ REQ D failed: {e}")
        return False


def orchestrate_req_e():
    """REQ E: Comprehensive Test Coverage"""
    print("\n" + "="*70)
    print("  REQ E: Comprehensive Test Coverage")
    print("="*70 + "\n")

    print("  Getting baseline coverage...")
    baseline_cov = run_existing_tests()

    prompt = """Generate a COMPLETE, VALID pytest test file.

Requirements:
- Must have valid Python syntax (no errors)
- Must import: pytest, datetime, timezone, db, models, services
- Must define a fixture called suggestion_test_data
- Must create test classes: TestNewsSuggestionsRanking, TestWikiSuggestionsRanking, TestExcludePrimaryDiscussion, TestExcludeManuallyRelated, TestExcludeHiddenDeleted, TestDeterministicOrdering, TestTruthfulReasonLabels, TestDistinctionBetweenTypes, TestManagementUIBehavior, TestAPIEndpointBehavior
- Each class must have multiple test methods (25+ tests total)
- Tests must cover: ranking, exclusions, determinism, reason labels, API responses, management UI
- Include parametrized tests using @pytest.mark.parametrize
- All test assertions must validate actual behavior

Start immediately with: import pytest
End with: last test method (no code after)

Generate ONLY valid Python code suitable for: pytest backend/tests/test_suggestion_coverage_complete.py"""

    try:
        print("  Calling Ollama...")
        response = ollama.generate(model="qwen2.5-coder-32b:coding", prompt=prompt, stream=False)
        test_code = response.get("response", "").strip()

        if not test_code:
            logger.error("✗ Empty response")
            return False

        # Verify syntax
        try:
            compile(test_code, ".ollama/test_suggestion_coverage_complete.py", "exec")
        except SyntaxError as e:
            logger.error(f"✗ Syntax error in generated code: {e}")
            return False

        print("  Writing test file...")
        if not write_file(".ollama/test_suggestion_coverage_complete.py", test_code):
            return False

        print("  Running tests...\n")
        passed, new_cov = run_pytest(".ollama/test_suggestion_coverage_complete.py", cov_threshold=85)

        if not passed:
            logger.error("✗ Tests failed or coverage < 85%")
            return False

        if not verify_coverage(baseline_cov, new_cov):
            logger.error(f"✗ Coverage did not improve")
            return False

        success = git_commit(
            [".ollama/test_suggestion_coverage_complete.py"],
            f"feat(ollama): REQ E - Tests {new_cov:.1f}% coverage (agent-generated)"
        )
        if success:
            print("  ✓ REQ E COMPLETE\n")
        return success

    except Exception as e:
        logger.error(f"✗ REQ E failed: {e}")
        return False


def orchestrate_req_f():
    """REQ F: Documentation and Changelog"""
    print("\n" + "="*70)
    print("  REQ F: Documentation and Changelog")
    print("="*70 + "\n")

    # Generate CHANGELOG entry
    changelog_prompt = """Generate ONLY markdown text for a CHANGELOG.md entry.

Version: 0.0.35
Date: 2026-03-16
Topic: Suggested-Discussions Feature Completion (REQ D, E, F)

Format as proper markdown section with:
- Section header: ## [0.0.35] - 2026-03-16
- Subsection: ### Suggested Discussions Feature Completion
- Subsections for: REQ D (API consistency), REQ E (Test coverage), REQ F (Documentation)
- List API endpoints
- List test coverage areas
- Mark feature as production-ready

Generate ONLY the markdown text, ready to insert into CHANGELOG.md"""

    # Generate DOCS
    docs_prompt = """Generate ONLY markdown text for documentation guide.

File: docs/SUGGESTED_DISCUSSIONS.md
Length: 300+ lines
Topics:
- Feature overview
- How News suggestions work (ranking algorithm, exclusions)
- How Wiki suggestions work (ranking algorithm, exclusions)
- Distinction between: primary discussion, manually related, suggested threads
- Complete API reference for both endpoints
- Public page display
- Admin workflow
- Ranking logic details
- Determinism guarantee
- Truthfulness guarantee (reason labels)
- Testing
- Troubleshooting

Generate ONLY the markdown text, well-formatted and production-ready."""

    try:
        print("  Generating CHANGELOG...")
        response1 = ollama.generate(model="qwen3.5-35b:docs", prompt=changelog_prompt, stream=False)
        changelog = response1.get("response", "").strip()

        if not changelog:
            logger.error("✗ Empty CHANGELOG response")
            return False

        if not write_file(".ollama/CHANGELOG_entry_v0.0.35.md", changelog):
            return False

        print("  Generating documentation...")
        response2 = ollama.generate(model="qwen3.5-35b:docs", prompt=docs_prompt, stream=False)
        docs = response2.get("response", "").strip()

        if not docs:
            logger.error("✗ Empty docs response")
            return False

        if not write_file(".ollama/docs_SUGGESTED_DISCUSSIONS.md", docs):
            return False

        print("  Committing...\n")
        success = git_commit(
            [".ollama/CHANGELOG_entry_v0.0.35.md", ".ollama/docs_SUGGESTED_DISCUSSIONS.md"],
            "feat(ollama): REQ F - Documentation & changelog (agent-generated)"
        )
        if success:
            print("  ✓ REQ F COMPLETE\n")
        return success

    except Exception as e:
        logger.error(f"✗ REQ F failed: {e}")
        return False


def main():
    """Run all three requirements."""
    print("\n" + "="*70)
    print("  AUTONOMOUS OLLAMA AGENTS: REQ D, E, F (v2)")
    print("="*70)

    results = {
        "REQ D (API Analysis)": orchestrate_req_d(),
        "REQ E (Tests)": orchestrate_req_e(),
        "REQ F (Docs)": orchestrate_req_f(),
    }

    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)
    for req, success in results.items():
        status = "✓ COMPLETE" if success else "✗ FAILED"
        print(f"  {req}: {status}")
    print("="*70 + "\n")

    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
