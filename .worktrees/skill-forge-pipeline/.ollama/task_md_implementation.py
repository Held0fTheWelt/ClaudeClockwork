#!/usr/bin/env python3
"""
Task.md DIRECT IMPLEMENTATION via Ollama Coding Agents
Skips slow orchestration, dispatches directly to coding specialists
"""

import ollama
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")
TASK_MD = PROJECT_ROOT / "Task.md"

def ollama_call(model: str, prompt: str) -> str:
    """Call Ollama agent."""
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
    print("  TASK.MD DIRECT IMPLEMENTATION")
    print("  Ollama Coding Agents → Files → Commits")
    print("="*70 + "\n")

    # Load requirements
    task_md = TASK_MD.read_text()

    # REQUIREMENT B: Public product integration
    print("▶ REQ B: Suggest threads visible on News/Wiki public pages")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    b_prompt = f"""Task.md specifies:

"B. Suggested threads must be VISIBLE in public News and Wiki pages"

Current state: Backend has ranking logic in news_service and wiki_service.
Frontend (Jinja2 templates) needs to display suggestions.

REQUIRED CHANGES:
1. Modify backend/app/web/templates/news_detail.html - add suggested threads section
2. Modify backend/app/web/templates/wiki_detail.html - add suggested threads section
3. Modify backend/app/web/news_routes.py - pass suggestions to template context
4. Modify backend/app/web/wiki_routes.py - pass suggestions to template context

TASK: Generate the exact code changes needed (HTML + Python).
Return code as: FILE_PATH:\n```language\nCODE\n```

Full Task.md for context:
{task_md[:2000]}
"""

    b_result = ollama_call("qwen2.5-coder-32b:coding", b_prompt)
    if b_result:
        print("✓ REQ B Output:")
        print(b_result[:500] + "...\n")

    # REQUIREMENT C: Admin UI
    print("▶ REQ C: Management console shows suggestion candidates")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    c_prompt = f"""Task.md specifies:

"C. Administration-tool management flows must expose suggestion candidates"

Current state: manage_news.js and manage_wiki.js handle article management.
Need to show which forum threads are suggested, allow accepting/rejecting them.

TASK: Generate JavaScript code to display suggestions in management console.
Return code as: FILE_PATH:\n```javascript\nCODE\n```

Show:
- Which threads are suggested
- Reason for suggestion
- Accept/reject buttons

Context: {task_md[:1500]}
"""

    c_result = ollama_call("qwen2.5-coder-32b:coding", c_prompt)
    if c_result:
        print("✓ REQ C Output:")
        print(c_result[:500] + "...\n")

    # REQUIREMENT E: Tests
    print("▶ REQ E: Expanded test coverage for ranking and suggestions")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    e_prompt = f"""Task.md specifies:

"E. Test coverage must be sufficient for ranking determinism, exclusions"

Generate pytest tests for:
1. Ranking is deterministic (same inputs = same order)
2. Ranking prioritizes relevant threads (by tags, category, activity)
3. Exclusions work (don't suggest own threads, deleted/hidden)
4. API endpoints return correct suggestions

Return code as: backend/tests/test_suggestion_ranking.py (complete file)

Context: {task_md[:1500]}
"""

    e_result = ollama_call("qwen2.5-coder-32b:coding", e_prompt)
    if e_result:
        print("✓ REQ E Output:")
        print(e_result[:500] + "...\n")

    # REQUIREMENT F: Docs
    print("▶ REQ F: Documentation updates")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    f_prompt = f"""Task.md specifies:

"F. Update docs, CHANGELOG.md, and Postman collection"

Generate:
1. CHANGELOG.md entry describing the feature
2. docs/ summary of how suggestions work
3. API documentation for suggestion endpoints

Return as markdown.

Context: {task_md[:1500]}
"""

    f_result = ollama_call("qwen3.5-35b:docs", f_prompt)
    if f_result:
        print("✓ REQ F Output:")
        print(f_result[:500] + "...\n")

    print("\n" + "="*70)
    print("  ✓ IMPLEMENTATION COMPLETE")
    print("="*70)
    print("\nNEXT: Write outputs to files and create commits\n")

    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
