#!/usr/bin/env python3
"""Fix the regex error in news.js line 325."""

from pathlib import Path
import subprocess

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

print("\n" + "="*70)
print("  Fix news.js Regex Error (line 325)")
print("="*70 + "\n")

news_js = PROJECT_ROOT / "administration-tool/static/news.js"

with open(news_js) as f:
    content = f.read()

# Fix the malformed line
# Current: suggestedWrap.appendChildsuggestedWrap.appendChild(suggestedList);
# Should be: suggestedWrap.appendChild(suggestedList);

if "appendChildsuggestedWrap.appendChild" in content:
    content = content.replace(
        "suggestedWrap.appendChildsuggestedWrap.appendChild(suggestedList);",
        "suggestedWrap.appendChild(suggestedList);"
    )

    with open(news_js, 'w') as f:
        f.write(content)

    print("  ✓ Fixed malformed line 325")

    # Verify
    lines = content.split('\n')
    if 325 < len(lines):
        print(f"  Line 325: {lines[324]}")

    # Commit
    try:
        subprocess.run(
            ["git", "add", "administration-tool/static/news.js"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            check=True,
        )

        subprocess.run(
            ["git", "commit", "--amend", "--no-edit"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            check=True,
        )

        result = subprocess.run(
            ["git", "log", "-1", "--oneline"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
        )

        print(f"  ✓ Amended commit: {result.stdout.strip()}\n")
    except Exception as e:
        print(f"  ✗ Could not commit: {str(e)}\n")
else:
    print("  ✓ Line 325 already correct\n")

print("="*70 + "\n")
