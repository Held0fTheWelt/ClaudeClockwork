#!/usr/bin/env python3
"""
TASK A: Fix News UI Rendering Bug
Analyze where suggested-discussions are being rendered in news.js
"""

import ollama
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

def analyze_news_js():
    """Analyze news.js to find the rendering bug."""

    news_js = PROJECT_ROOT / "administration-tool/static/news.js"

    if not news_js.exists():
        print("✗ news.js not found")
        return False

    with open(news_js) as f:
        content = f.read()

    print("\n" + "="*70)
    print("  TASK A: Analyze News UI Rendering")
    print("="*70 + "\n")

    prompt = f"""Analyze this news.js code and identify EXACTLY where suggested-discussions are being rendered.

FILE: {news_js}
SIZE: {len(content)} bytes

TASK:
1. Find where suggested-discussions list items are being appended
2. Identify which DOM container/element they're appended to
3. Verify if that's the correct container or wrong container
4. If wrong, identify what the correct container should be

Look for:
- Element IDs like 'suggested-list', 'related-list', 'news-list', etc.
- Append/innerHTML operations
- The difference between "related" and "suggested" sections

CODE SAMPLE (first 5000 chars):
{content[:5000]}

ANALYSIS:
1. Where is suggested-discussions being appended? (exact line/element ID)
2. Is this correct or wrong?
3. If wrong, what should it be?
4. Provide the exact fix (1-2 lines of code change)"""

    print("Analyzing news.js structure...\n")

    try:
        response = ollama.generate(
            model="gemma3:latest",
            prompt=prompt,
            stream=False,
        )
        analysis = response.get("response", "").strip()
        print(analysis)
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    success = analyze_news_js()
    sys.exit(0 if success else 1)
