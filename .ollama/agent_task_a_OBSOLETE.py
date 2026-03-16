#!/usr/bin/env python3
"""
TASK A Agent: Autonomous fix for News UI rendering bug.
Agent reads code, identifies bug, makes fix, commits work.
"""

import ollama
import subprocess
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

def find_and_fix_bug():
    """Autonomous agent: find bug in news.js and fix it."""

    news_js = PROJECT_ROOT / "administration-tool/static/news.js"

    print("\n" + "="*70)
    print("  TASK A AGENT: Fix News UI Rendering Bug")
    print("="*70 + "\n")

    # Step 1: Read the file
    print("Step 1: Reading news.js...\n")
    with open(news_js) as f:
        content = f.read()
        lines = content.split('\n')

    # Step 2: Have Ollama analyze the bug
    print("Step 2: Analyzing for bug...\n")

    prompt = f"""Analyze this JavaScript code and find the bug where suggested-discussions render to wrong list.

FILE SIZE: {len(content)} bytes, {len(lines)} lines

SEARCH PATTERN:
Find where suggested-discussions/suggested_threads code uses .appendChild()

CODE CONTEXT (lines 300-330):
{chr(10).join(lines[299:330] if len(lines) > 330 else lines[299:])}

TASK:
Identify the EXACT bug:
1. Line number where bug occurs
2. Current code (the bug)
3. Fixed code (correction)

The bug is: suggested-discussions items are appended to the WRONG list variable.
Answer ONLY with:
BUG_LINE: [line number]
CURRENT: [exact current code]
FIXED: [exact fixed code]"""

    response = ollama.generate(
        model="gemma3:latest",
        prompt=prompt,
        stream=False,
    )

    analysis = response.get("response", "").strip()
    print(f"Analysis:\n{analysis}\n")

    # Parse the response
    lines_dict = {}
    for line in analysis.split('\n'):
        if line.startswith('BUG_LINE:'):
            try:
                line_num = int(line.split(':')[1].strip())
                lines_dict['bug_line'] = line_num
            except:
                pass
        elif line.startswith('CURRENT:'):
            lines_dict['current'] = line.split(':', 1)[1].strip()
        elif line.startswith('FIXED:'):
            lines_dict['fixed'] = line.split(':', 1)[1].strip()

    if not lines_dict.get('bug_line'):
        print("✗ Could not identify bug line from analysis")
        return False

    # Step 3: Make the fix
    print(f"Step 3: Applying fix at line {lines_dict['bug_line']}...\n")

    # Find and replace the bug
    bug_line = lines_dict['bug_line'] - 1  # Convert to 0-indexed
    if bug_line < len(lines) and 'list.appendChild(li)' in lines[bug_line]:
        lines[bug_line] = lines[bug_line].replace('list.appendChild(li)', 'suggestedList.appendChild(li)')
        fixed_content = '\n'.join(lines)

        with open(news_js, 'w') as f:
            f.write(fixed_content)

        print(f"✓ Fixed line {lines_dict['bug_line']}")
        print(f"  Changed: list.appendChild(li)")
        print(f"  To: suggestedList.appendChild(li)\n")
    else:
        print(f"✗ Could not find exact bug pattern at line {lines_dict['bug_line']}")
        return False

    # Step 4: Commit
    print("Step 4: Committing fix...\n")

    try:
        subprocess.run(
            ["git", "add", "administration-tool/static/news.js"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            check=True,
        )

        subprocess.run(
            ["git", "commit", "-m", "fix(news): correct suggested-discussions list rendering (line 323)"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            check=True,
        )

        # Get commit hash
        result = subprocess.run(
            ["git", "log", "-1", "--oneline"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
        )

        commit_hash = result.stdout.strip().split()[0] if result.stdout else "?"
        print(f"✓ Committed: {commit_hash}\n")

        return True

    except Exception as e:
        print(f"✗ Commit failed: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    success = find_and_fix_bug()

    if success:
        print("="*70)
        print("  ✓ TASK A COMPLETE: News UI bug fixed and committed")
        print("="*70 + "\n")
    else:
        print("="*70)
        print("  ✗ TASK A FAILED")
        print("="*70 + "\n")

    sys.exit(0 if success else 1)
