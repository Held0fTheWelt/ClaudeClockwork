#!/usr/bin/env python3
"""REQ E: Generate comprehensive test coverage using Ollama."""

import ollama
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

def main():
    print("\n" + "="*70)
    print("  REQ E: Comprehensive Test Coverage")
    print("="*70 + "\n")

    # Use smaller, faster model
    model = "qwen2.5-14b:agent"

    prompt = """Generate complete pytest tests for suggested-discussions feature.

COVERAGE NEEDED (10 tests minimum):
1. News suggestion ranking by tags
2. Wiki suggestion ranking by tags
3. Exclude primary discussion thread
4. Exclude manually related threads
5. Exclude hidden/deleted threads
6. Deterministic ordering (same result twice)
7. Grounded reason labels ("Matched N tags" or "Recent discussion")
8. Distinction between discussion/related/suggested sections
9. Admin UI: fetch and render suggestions
10. API endpoint: 200 response with items array

GENERATE PYTEST FILE:
- File: backend/tests/test_suggestion_coverage_complete.py
- Use fixtures: app, client, test_user, admin_user
- Test both news and wiki endpoints
- Assert actual payload content, not just status codes
- Include parametrize decorators for variations
- No placeholders, no skipped tests

START CODE NOW (no preamble):
"""

    try:
        print(f"  → {model}...")
        response = ollama.generate(
            model=model,
            prompt=prompt,
            stream=False,
        )
        result = response.get("response", "").strip()
        print(f"    ✓ ({len(result)} chars)\n")

        if result:
            # Save test file
            test_file = PROJECT_ROOT / "backend/tests/test_suggestion_coverage_complete.py"
            test_file.write_text(result)
            print(f"✓ TEST FILE SAVED to {test_file}\n")
            print("First 1000 chars:\n")
            print(result[:1000])
            return True
        else:
            print("✗ No response from model\n")
            return False
    except Exception as e:
        print(f"    ✗ Error: {str(e)[:150]}\n")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
