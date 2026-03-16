#!/usr/bin/env python3
"""
Audit Task.md implementation against current codebase
Uses Ollama agents to validate requirements A-F
"""

import ollama
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")
TASK_MD = PROJECT_ROOT / "Task.md"

def ollama_call(model: str, prompt: str) -> str:
    """Call Ollama agent."""
    try:
        print(f"  Querying {model}...", flush=True)
        response = ollama.generate(model=model, prompt=prompt, stream=False)
        result = response.get("response", "").strip()
        print(f"    ✓ ({len(result)} chars)\n")
        return result
    except Exception as e:
        print(f"    ✗ {str(e)[:80]}\n")
        return ""

def main():
    print("\n" + "="*70)
    print("  TASK.MD AUDIT — Current Implementation vs Requirements")
    print("="*70 + "\n")

    task_md = TASK_MD.read_text()

    # Audit REQ A: Ranking Logic
    print("▶ AUDITING REQ A: Ranking must be deterministic, contextual, truthful")
    print("━"*70)

    audit_a = ollama_call("phi4-14b:reviewer", f"""Audit the ranking implementation in:
- backend/app/services/news_service.py::get_suggested_threads_for_article()
- backend/app/services/wiki_service.py::get_suggested_threads_for_wiki_page()

AUDIT CHECKLIST:
✓ Is ranking deterministic (same inputs → same order)?
✓ Does it use only allowed signals: tags, category, activity, exclusions?
✓ Does it exclude: primary discussion, manual links, hidden/deleted threads?
✓ Does it include grounded reason labels?
✓ Are reason labels actually truthful (match ranking logic)?

REPORT FINDINGS:
1. What ranking signals are actually used?
2. Are all mandatory exclusions implemented?
3. Is ordering truly deterministic?
4. Are reason labels grounded or fake?

Task.md excerpt:
{task_md[task_md.find('A. Ranking'):task_md.find('B. Public')]}
""")

    if audit_a:
        print(f"REQ A AUDIT:\n{audit_a[:600]}\n")

    # Audit REQ B: Public Visibility
    print("▶ AUDITING REQ B: Public product integration must be visible")
    print("━"*70)

    audit_b = ollama_call("phi4-14b:reviewer", f"""Audit public rendering in:
- administration-tool/templates/news_detail.html
- administration-tool/templates/wiki_public.html
- administration-tool/static/news.js
- administration-tool/static/wiki.js (if exists)

AUDIT CHECKLIST:
✓ Are suggested_threads rendered on public pages?
✓ Are the three groups distinct: discussion / related / suggested?
✓ Is metadata shown: title, category, tags, activity?
✓ Are reason labels shown if available?
✓ Is the page clean (no duplication)?

REPORT FINDINGS:
1. Which pages render suggested threads?
2. Are all three groups present and distinct?
3. What metadata is shown?
4. Any UI issues or missing pieces?

Task.md excerpt:
{task_md[task_md.find('B. Public'):task_md.find('C. Management')]}
""")

    if audit_b:
        print(f"REQ B AUDIT:\n{audit_b[:600]}\n")

    # Audit REQ C: Admin Management
    print("▶ AUDITING REQ C: Management flows must expose candidates")
    print("━"*70)

    audit_c = ollama_call("phi4-14b:reviewer", f"""Audit admin UI in:
- administration-tool/static/manage_news.js
- administration-tool/static/manage_wiki.js
- administration-tool/templates/manage/news.html
- administration-tool/templates/manage/wiki.html

AUDIT CHECKLIST:
✓ Do management pages show suggested thread candidates?
✓ Can suggestions be promoted to manual related threads?
✓ Is there a working control/button for promotion?
✓ Is the flow clean and intuitive?
✓ Do promotion requests work with existing API?

REPORT FINDINGS:
1. Is suggested thread UI present in manage pages?
2. Is there a working promotion mechanism?
3. Which endpoints are called?
4. Any broken or missing features?

Task.md excerpt:
{task_md[task_md.find('C. Management'):task_md.find('D. Wiki')]}
""")

    if audit_c:
        print(f"REQ C AUDIT:\n{audit_c[:600]}\n")

    # Audit REQ E: Test Coverage
    print("▶ AUDITING REQ E: Tests must be specific and sufficient")
    print("━"*70)

    audit_e = ollama_call("phi4-14b:reviewer", f"""Audit test coverage in backend/tests/:
- Find tests for: ranking, exclusions, API behavior

AUDIT CHECKLIST:
✓ Test: News suggestion ranking
✓ Test: Wiki suggestion ranking
✓ Test: Primary discussion excluded
✓ Test: Manual related threads excluded
✓ Test: Hidden/inaccessible threads excluded
✓ Test: Deterministic ordering
✓ Test: Reason labels are truthful
✓ Test: Discussion vs related vs suggested distinction
✓ Test: API endpoints return correct data

REPORT FINDINGS:
1. How many suggestion-related tests exist?
2. Which requirement #1-10 tests are missing?
3. Are tests shallow (status code only) or deep (payload validation)?
4. What test failures/gaps were found?

Task.md excerpt:
{task_md[task_md.find('E. Tests'):task_md.find('F. Docs')]}
""")

    if audit_e:
        print(f"REQ E AUDIT:\n{audit_e[:600]}\n")

    print("\n" + "="*70)
    print("  AUDIT COMPLETE")
    print("="*70)
    print("\nNext: Review findings and identify implementation gaps\n")

    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
