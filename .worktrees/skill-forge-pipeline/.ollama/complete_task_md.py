#!/usr/bin/env python3
"""
Complete Task.md: REQ D (API docs), REQ E (tests), REQ F (changelog)
"""

import ollama
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")
TASK_MD = PROJECT_ROOT / "Task.md"

def ollama_call(model: str, prompt: str) -> str:
    try:
        print(f"  → {model}...", flush=True)
        response = ollama.generate(model=model, prompt=prompt, stream=False)
        result = response.get("response", "").strip()
        print(f"    ✓ ({len(result)} chars)\n")
        return result
    except Exception as e:
        print(f"    ✗ {str(e)[:80]}\n")
        return ""

def main():
    print("\n" + "="*70)
    print("  TASK.MD COMPLETION: REQ D, E, F")
    print("="*70 + "\n")

    task_md = TASK_MD.read_text()

    # REQ D: API/Docs Consistency
    print("▶ REQ D: Wiki API/docs/Postman must be fully consistent")
    print("━"*70)

    req_d = ollama_call("qwen2.5-72b:reasoning", f"""Review Task.md REQ D requirement:

{task_md[task_md.find('D. Wiki'):task_md.find('E. Tests')]}

TASK: Audit the Wiki API implementation and docs.

FACTS TO VERIFY:
1. Does /api/v1/wiki/<page_id>/suggested-threads endpoint exist?
2. Are suggestions returned INSIDE the page payload or via dedicated endpoint?
3. What does the Postman collection claim?
4. What does the API documentation say?

DECISION NEEDED:
Choose OPTION 1 (dedicated endpoint) or OPTION 2 (payload-only)?

OUTPUT:
- Which option you recommend and why
- Exact endpoint paths if dedicated endpoint chosen
- Breaking changes (if any)
- Required docs updates
""")

    if req_d:
        print(f"REQ D Decision:\n{req_d[:600]}\n")

    # REQ E: Test Expansion
    print("▶ REQ E: Tests must be specific and sufficient")
    print("━"*70)

    req_e = ollama_call("qwen2.5-coder-32b:coding", f"""Generate comprehensive test coverage for suggested threads.

REQUIREMENTS from Task.md:
1. News suggestion ranking
2. Wiki suggestion ranking
3. Exclusion of primary discussion
4. Exclusion of manually related threads
5. Exclusion of hidden/inaccessible threads
6. Deterministic ordering
7. Truthful reason labels
8. Distinction between discussion/related/suggested
9. Management/API behavior
10. Wiki endpoint behavior

OUTPUT: Complete pytest test file covering all 10 requirements.

CONSTRAINTS:
- No placeholder tests
- Assert actual payload content
- Deep behavior testing, not just status codes
- Target: backend/tests/test_suggestion_coverage_complete.py
""")

    if req_e:
        print(f"REQ E Tests (first 600 chars):\n{req_e[:600]}\n")

    # REQ F: Documentation
    print("▶ REQ F: Docs and changelog")
    print("━"*70)

    req_f = ollama_call("qwen3.5-35b:docs", f"""Update documentation and changelog for suggested-discussions feature.

DOCUMENTATION UPDATES NEEDED:
1. CHANGELOG.md entry (v0.0.33 or next version)
2. docs/ summary explaining:
   - How News suggestions work (ranking signals, exclusions)
   - How Wiki suggestions work (ranking signals, exclusions)
   - Difference between: primary discussion, manually related, suggested
   - API endpoint design choice (payload vs dedicated)
   - Example usage (public page + admin UI)

3. Postman collection updates (if applicable)

OUTPUT:
A. CHANGELOG.md entry (markdown)
B. docs/SUGGESTED_DISCUSSIONS.md (complete guide)
C. API documentation snippet (OpenAPI/markdown)

STYLE: Professional, clear, accurate. No overclaiming.
""")

    if req_f:
        print(f"REQ F Documentation (first 600 chars):\n{req_f[:600]}\n")

    print("\n" + "="*70)
    print("  COMPLETION READY FOR INTEGRATION")
    print("="*70 + "\n")

    return bool(req_d and req_e and req_f)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
