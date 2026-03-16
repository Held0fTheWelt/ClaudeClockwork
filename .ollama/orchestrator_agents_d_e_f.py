#!/usr/bin/env python3
"""Orchestrator: Autonomous Ollama agents for Task.md REQ D, E, F."""

import ollama
import sys
import logging
from pathlib import Path
import subprocess

sys.path.insert(0, str(Path(__file__).parent))

from helper_functions import (
    write_file, run_pytest, verify_coverage, git_commit, run_existing_tests
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def orchestrate_req_d():
    """REQ D: API Consistency Analysis"""
    print("\n" + "="*70)
    print("  REQ D: API Consistency Analysis")
    print("="*70 + "\n")

    prompt = """You are a backend architect. Generate a Python script that analyzes API consistency.

Script must:
1. Import: from helper_functions import write_file
2. Analyze News vs Wiki endpoints (URL patterns, response format, breaking changes)
3. Call: write_file(".ollama/req_d_analysis.txt", analysis_text)
4. Define main() function

Generate complete, executable Python script. Output ONLY code."""

    try:
        print("  Calling Ollama...")
        response = ollama.generate(model="qwen3.5-35b:reasoning", prompt=prompt, stream=False)
        agent_code = response.get("response", "").strip()

        if not agent_code:
            logger.error("✗ Empty response")
            return False

        print("  Executing agent code...\n")
        namespace = {"write_file": write_file, "git_commit": git_commit}
        exec(agent_code, namespace)

        if not Path(".ollama/req_d_analysis.txt").exists():
            logger.error("✗ Agent did not write file")
            return False

        success = git_commit(
            [".ollama/req_d_analysis.txt"],
            "feat(ollama): REQ D - API consistency (agent-generated)"
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

    prompt = """You are a Python testing expert. Generate a complete pytest test file.

File: .ollama/test_suggestion_coverage_complete.py

Must test 10 requirement areas:
1. News ranking by tags
2. Wiki ranking by tags
3. Exclude primary discussion
4. Exclude manually related threads
5. Exclude hidden/deleted threads
6. Deterministic ordering
7. Truthful reason labels
8. Distinction between types
9. Management UI behavior
10. API endpoint responses

Requirements:
- Create fixture: suggestion_test_data with forums, threads, tags, articles, pages
- Create 25+ test methods across test classes
- All assertions validate actual behavior
- Include parametrized tests
- No placeholders, valid Python

Generate complete pytest file. Output ONLY code."""

    try:
        print("  Calling Ollama...")
        response = ollama.generate(model="qwen2.5-coder-32b:coding", prompt=prompt, stream=False)
        test_code = response.get("response", "").strip()

        if not test_code:
            logger.error("✗ Empty response")
            return False

        print("  Writing test file...")
        if not write_file(".ollama/test_suggestion_coverage_complete.py", test_code):
            return False

        print("  Running tests...\n")
        passed, new_cov = run_pytest(".ollama/test_suggestion_coverage_complete.py", cov_threshold=85)

        if not passed:
            logger.error("✗ Tests failed")
            return False

        if not verify_coverage(baseline_cov, new_cov):
            logger.error(f"✗ Coverage did not improve")
            return False

        success = git_commit(
            [".ollama/test_suggestion_coverage_complete.py"],
            f"feat(ollama): REQ E - Tests {new_cov:.1f}% (agent-generated)"
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

    prompt = """You are a technical writer. Generate THREE documents as a Python script.

Script must:
1. Import: from helper_functions import write_file
2. Generate and write:
   - .ollama/CHANGELOG_entry_v0.0.35.md (v0.0.35 entry, feature complete)
   - .ollama/docs_SUGGESTED_DISCUSSIONS.md (500+ line guide)
   - .ollama/postman_api_reference.md (API reference)
3. Define main() function

Documents must cover:
- CHANGELOG: REQ D, E, F completion, API endpoints, test coverage, production-ready
- DOCS: Overview, ranking algorithm, API reference, troubleshooting, determinism, truthfulness
- POSTMAN: Both suggested-threads endpoints with schemas and examples

Generate complete, executable Python script. Output ONLY code."""

    try:
        print("  Calling Ollama...")
        response = ollama.generate(model="qwen3.5-35b:docs", prompt=prompt, stream=False)
        docs_code = response.get("response", "").strip()

        if not docs_code:
            logger.error("✗ Empty response")
            return False

        print("  Executing agent code...\n")
        namespace = {"write_file": write_file}
        exec(docs_code, namespace)

        required = [
            ".ollama/CHANGELOG_entry_v0.0.35.md",
            ".ollama/docs_SUGGESTED_DISCUSSIONS.md",
        ]
        missing = [f for f in required if not Path(f).exists()]
        if missing:
            logger.error(f"✗ Missing: {missing}")
            return False

        files_to_commit = required
        if Path(".ollama/postman_api_reference.md").exists():
            files_to_commit.append(".ollama/postman_api_reference.md")

        success = git_commit(
            files_to_commit,
            "feat(ollama): REQ F - Docs & changelog (agent-generated)"
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
    print("  AUTONOMOUS OLLAMA AGENTS: REQ D, E, F")
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
