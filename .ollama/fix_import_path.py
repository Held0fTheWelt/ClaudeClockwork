#!/usr/bin/env python3
"""
Fix import path in task_routes.py
"""

from pathlib import Path
import subprocess

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

routes_file = PROJECT_ROOT / "backend/app/api/v1/task_routes.py"

if routes_file.exists():
    content = routes_file.read_text()

    # Fix the import - from ..services should be from ...services (up to app, then to services)
    fixed = content.replace(
        "from ..services.task_executor_service import TaskExecutorService",
        "from app.services.task_executor_service import TaskExecutorService"
    )

    # Also fix limiter import
    fixed = fixed.replace(
        "from ...extensions import limiter",
        "from app.extensions import limiter"
    )

    routes_file.write_text(fixed)
    print("✓ Fixed import paths in task_routes.py")

    # Test compile
    try:
        import py_compile
        py_compile.compile(str(routes_file), doraise=True)
        print("✓ Routes file compiles")

        # Commit
        subprocess.run(
            ["git", "add", "backend/app/api/v1/task_routes.py"],
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
        print(f"✗ Compile error: {str(e)}")
else:
    print("✗ Routes file not found")
