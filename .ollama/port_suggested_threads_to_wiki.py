#!/usr/bin/env python3
"""
Port suggested threads functionality from manage_news.js to manage_wiki.js
"""

import ollama
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

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
    print("  PORT: Suggested Threads → manage_wiki.js")
    print("="*70 + "\n")

    # Read source and target files
    manage_news = (PROJECT_ROOT / "administration-tool/static/manage_news.js").read_text()
    manage_wiki = (PROJECT_ROOT / "administration-tool/static/manage_wiki.js").read_text()

    print("▶ ANALYZING manage_news.js suggested threads functions...")

    # Extract the relevant sections from manage_news.js
    news_start = manage_news.find("function renderSuggestedThreadsList")
    news_end = manage_news.find("function onRelatedThreadAdd", news_start) + 1000
    suggested_functions = manage_news[news_start:news_end]

    print(f"Found {len(suggested_functions)} chars of suggested threads code\n")

    # Use Ollama to adapt the code for wiki
    print("▶ ADAPTING code for Wiki management...")

    adapt_prompt = f"""You are a JavaScript expert. Port the suggested threads functionality from News to Wiki management.

SOURCE CODE (from manage_news.js):
```javascript
{suggested_functions[:2000]}
```

TARGET: Add this to manage_wiki.js

ADAPTATION RULES:
1. Change "manage-news-" IDs to "manage-wiki-"
2. Change "/api/v1/news/" to "/api/v1/wiki/"
3. Change "article_id" to "page_id"
4. Change "showFormSuccess/Error" to use wiki equivalents
5. Keep all logic and exclusions identical
6. Return COMPLETE JavaScript functions ready to paste into manage_wiki.js

FUNCTIONS TO PORT:
- renderSuggestedThreadsList() - displays suggestions with "Add as related" buttons
- fetchSuggestedThreads() - fetches from API endpoint
- onRelatedThreadAdd() modifications - already handles both news and wiki

OUTPUT:
Return JavaScript ready to add to manage_wiki.js (no explanations, just code).
"""

    adapted_code = ollama_call("qwen2.5-coder-32b:coding", adapt_prompt)

    if adapted_code:
        print("✓ CODE GENERATED")
        print("\nPORTED FUNCTIONS:")
        print("─" * 70)
        print(adapted_code[:1000])
        print("...\n")

        # Save to file
        output_file = PROJECT_ROOT / ".ollama/manage_wiki_suggested_threads.js"
        output_file.write_text(adapted_code)
        print(f"✓ Saved to: {output_file}\n")

        return True
    else:
        print("✗ Code generation failed\n")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
