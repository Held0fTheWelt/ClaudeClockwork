#!/usr/bin/env python3
"""
Cleanup Agent: Remove markdown code block wrappers from generated files.
"""

import subprocess
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

def clean_file(path: str) -> bool:
    """Remove markdown code block wrappers from file."""
    full_path = PROJECT_ROOT / path

    if not full_path.exists():
        return False

    content = full_path.read_text()

    # Check if wrapped in markdown
    if content.startswith("```"):
        lines = content.split('\n')

        # Remove opening markdown marker (e.g., ```python, ```markdown)
        if lines[0].startswith("```"):
            lines = lines[1:]

        # Remove closing markdown marker (last line if it's ```)
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        # Remove any trailing whitespace-only lines
        while lines and not lines[-1].strip():
            lines.pop()

        cleaned = '\n'.join(lines)
        full_path.write_text(cleaned)
        return True

    return False

print("\n" + "="*70)
print("  MARKDOWN WRAPPER CLEANUP AGENT")
print("="*70 + "\n")

files_to_fix = [
    "docs/ADR/ADR-004-ollama-first-routing-architecture.md",
    "backend/app/services/task_executor_service.py",
    "backend/app/api/v1/task_routes.py",
    "backend/tests/test_task_executor_fallback.py",
]

fixed = []
for file_path in files_to_fix:
    if clean_file(file_path):
        print(f"  ✓ Cleaned: {file_path}")
        fixed.append(file_path)
    else:
        print(f"  ⚠ Not wrapped or missing: {file_path}")

# Commit cleanup
if fixed:
    print("\n" + "─"*70)
    print("  Committing Cleanup")
    print("─"*70)

    try:
        subprocess.run(
            ["git", "add"] + fixed,
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

        print(f"  ✓ Amended: {result.stdout.strip()}\n")
    except Exception as e:
        print(f"  ✗ Commit failed: {str(e)}\n")

print("="*70 + "\n")
