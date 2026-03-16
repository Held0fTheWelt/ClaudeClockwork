#!/usr/bin/env python3
"""
Fix test file by removing preamble and markdown wrappers.
"""

from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

test_file = PROJECT_ROOT / "backend/tests/test_task_executor_fallback.py"

if test_file.exists():
    content = test_file.read_text()
    lines = content.split('\n')

    # Remove preamble (lines before first ```python)
    start_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("```python"):
            start_idx = i + 1
            break

    # Remove closing ```
    end_idx = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "```":
            end_idx = i
            break

    # Extract clean lines
    clean_lines = lines[start_idx:end_idx]

    # Remove trailing whitespace
    while clean_lines and not clean_lines[-1].strip():
        clean_lines.pop()

    cleaned = '\n'.join(clean_lines)
    test_file.write_text(cleaned)
    print("✓ Fixed test file")
else:
    print("✗ Test file not found")
