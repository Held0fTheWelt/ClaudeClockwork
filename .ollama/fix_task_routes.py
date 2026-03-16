#!/usr/bin/env python3
"""
Fix task_routes.py import and routing issues.
"""

from pathlib import Path
import subprocess

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

routes_file = PROJECT_ROOT / "backend/app/api/v1/task_routes.py"

if routes_file.exists():
    content = routes_file.read_text()

    # Fix imports
    fixed = content.replace(
        "from task_executor_service import execute_task",
        "from ..services.task_executor_service import TaskExecutorService"
    )

    # Fix missing imports
    if "from flask_jwt_extended import jwt_required" not in fixed:
        fixed = fixed.replace(
            "from flask import Blueprint, request, jsonify",
            "from flask import Blueprint, request, jsonify\nfrom flask_jwt_extended import jwt_required"
        )

    # Fix limiter import
    fixed = fixed.replace(
        "from . import limiter",
        "from ...extensions import limiter"
    )

    # Fix blueprint and route decorator
    fixed = fixed.replace(
        "task_routes = Blueprint('tasks', __name__)",
        "task_routes_bp = Blueprint('tasks', __name__)"
    )

    # Fix route paths (remove /api/v1 since blueprint is mounted at /api/v1/)
    fixed = fixed.replace(
        "@task_routes.route('/api/v1/tasks', methods=['POST'])",
        "@task_routes_bp.route('/tasks', methods=['POST'])"
    )

    fixed = fixed.replace(
        "@task_routes.route('/api/v1/tasks/health', methods=['GET'])",
        "@task_routes_bp.route('/tasks/health', methods=['GET'])"
    )

    # Fix execute_task call - should instantiate service
    fixed = fixed.replace(
        "        result = execute_task(",
        "        service = TaskExecutorService()\n        result = service.execute_task("
    )

    routes_file.write_text(fixed)
    print("✓ Fixed task_routes.py")

    # Test compile
    try:
        import py_compile
        py_compile.compile(str(routes_file), doraise=True)
        print("✓ Routes file compiles successfully")

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
        print(f"✗ Error: {str(e)}")
else:
    print("✗ Routes file not found")
