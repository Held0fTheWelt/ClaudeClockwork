#!/usr/bin/env python3
"""
Fix API v1 route registration.
"""

from pathlib import Path
import subprocess

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

# Fix backend/app/api/v1/__init__.py
v1_init = PROJECT_ROOT / "backend/app/api/v1/__init__.py"

if v1_init.exists():
    content = v1_init.read_text()

    # Add task_routes import if not present
    if "task_routes" not in content:
        # Add it after the other imports
        lines = content.split('\n')

        # Find the last import line
        last_import_idx = -1
        for i, line in enumerate(lines):
            if line.startswith("from app.api.v1 import"):
                last_import_idx = i

        if last_import_idx >= 0:
            lines.insert(last_import_idx + 1, "from app.api.v1 import task_routes  # noqa: F401, E402")
            content = '\n'.join(lines)
            v1_init.write_text(content)
            print("✓ Added task_routes import to v1/__init__.py")

# Fix backend/app/api/__init__.py
api_init = PROJECT_ROOT / "backend/app/api/__init__.py"

if api_init.exists():
    content = api_init.read_text()

    # The current registration is wrong - task_routes_bp is not imported at that level
    # We should remove the incorrect registration since task_routes is already imported
    # in the v1 blueprint init which registers it properly

    if "task_routes_bp" in content:
        # Remove the incorrect line
        lines = content.split('\n')
        fixed_lines = [line for line in lines if "task_routes_bp" not in line]
        content = '\n'.join(fixed_lines)
        api_init.write_text(content)
        print("✓ Removed incorrect task_routes_bp registration from api/__init__.py")

# Commit changes
try:
    subprocess.run(
        ["git", "add", "backend/app/api/__init__.py", "backend/app/api/v1/__init__.py"],
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

    print(f"✓ Amended: {result.stdout.strip()}")
except Exception as e:
    print(f"✗ Error: {str(e)}")
