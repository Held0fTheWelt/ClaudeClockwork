#!/usr/bin/env python3
"""
Master TaskExecutor Integration Validation and Fixing Agent
Uses Ollama intelligence to diagnose and resolve integration issues autonomously.
"""

import ollama
import subprocess
from pathlib import Path
import traceback

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

class TaskExecutorValidationAgent:
    """Master agent for validating and fixing TaskExecutor integration."""

    def __init__(self):
        self.results = {}
        self.files_modified = []

    def log(self, msg: str):
        print(f"  {msg}")

    def section(self, title: str):
        print(f"\n{'─'*70}")
        print(f"  {title}")
        print(f"{'─'*70}")

    def read_file(self, path: str) -> str:
        """Read file content."""
        full_path = PROJECT_ROOT / path
        return full_path.read_text() if full_path.exists() else ""

    def write_file(self, path: str, content: str) -> bool:
        """Write file content."""
        full_path = PROJECT_ROOT / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        self.files_modified.append(path)
        return True

    def run_ollama(self, prompt: str) -> str:
        """Call Ollama for intelligent analysis and fixes."""
        try:
            response = ollama.generate(
                model="gemma3:latest",
                prompt=prompt,
                stream=False,
            )
            return response.get("response", "").strip()
        except Exception as e:
            return f"[ERROR: {str(e)[:100]}]"

    def test_imports(self):
        """Test if backend imports work."""
        self.section("Testing Backend Imports")

        try:
            result = subprocess.run(
                ["python", "-c", "from app.api.v1 import api_v1_bp; print('OK')"],
                cwd=str(PROJECT_ROOT / "backend"),
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0 and "OK" in result.stdout:
                self.log("✓ Backend imports successfully")
                self.results['imports'] = "✓ Imports working"
                return True
            else:
                error = result.stderr if result.stderr else "Unknown error"
                self.log(f"✗ Import failed: {error[:100]}")
                return False
        except Exception as e:
            self.log(f"✗ Test error: {str(e)[:50]}")
            return False

    def analyze_and_fix_imports(self):
        """Use Ollama to analyze and fix import errors."""
        self.section("Analyzing Import Errors")

        # Try to get the actual error
        result = subprocess.run(
            ["python", "-c", "from app.api.v1 import api_v1_bp"],
            cwd=str(PROJECT_ROOT / "backend"),
            capture_output=True,
            text=True,
            timeout=5,
        )

        error_msg = result.stderr if result.stderr else "Import test passed"

        # Read the problematic files
        task_routes = self.read_file("backend/app/api/v1/task_routes.py")
        task_service = self.read_file("backend/app/services/task_executor_service.py")

        prompt = f"""Analyze and fix import/module errors in the TaskExecutor integration.

ERROR ENCOUNTERED:
{error_msg[:500]}

FILE: backend/app/api/v1/task_routes.py (first 30 lines):
{chr(10).join(task_routes.split(chr(10))[:30])}

FILE: backend/app/services/task_executor_service.py (first 20 lines):
{chr(10).join(task_service.split(chr(10))[:20])}

TASK:
1. Identify the root cause of the import error
2. Provide corrected versions of the affected files
3. Ensure all imports use correct relative paths for Flask structure: app/api/v1/task_routes.py -> app.services, app.extensions
4. Make sure TaskExecutorService is instantiated correctly

Output ONLY the corrected file content with proper imports and structure.
Format output as:
===== FILE: path/to/file.py =====
[complete corrected code]"""

        analysis = self.run_ollama(prompt)

        if "FILE:" in analysis:
            self.log("✓ Ollama analysis received, extracting corrected files")
            self._apply_ollama_fixes(analysis)
            return True
        else:
            self.log("✗ Could not get analysis from Ollama")
            return False

    def _apply_ollama_fixes(self, analysis: str):
        """Parse Ollama response and apply fixes."""
        files = {}
        current_file = None
        current_content = []

        for line in analysis.split('\n'):
            if line.startswith("===== FILE:"):
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content)
                # Extract filename
                current_file = line.split("===== FILE:")[1].strip().rstrip(" =====").strip()
                current_content = []
            elif current_file:
                current_content.append(line)

        # Add last file
        if current_file and current_content:
            files[current_file] = '\n'.join(current_content)

        # Apply fixes
        for path, content in files.items():
            if content.strip() and len(content) > 50:
                self.write_file(path, content)
                self.log(f"✓ Fixed: {path}")

    def verify_routes_registered(self):
        """Verify routes are properly registered."""
        self.section("Verifying Routes Registration")

        v1_init = self.read_file("backend/app/api/v1/__init__.py")

        if "task_routes" in v1_init:
            self.log("✓ task_routes imported in v1/__init__.py")
            return True
        else:
            self.log("✗ task_routes not imported in v1/__init__.py")
            return False

    def test_compilation(self):
        """Test Python compilation of generated files."""
        self.section("Testing Python Compilation")

        files_to_test = [
            "backend/app/services/task_executor_service.py",
            "backend/app/api/v1/task_routes.py",
            "backend/tests/test_task_executor_fallback.py",
        ]

        all_pass = True
        for file_path in files_to_test:
            try:
                result = subprocess.run(
                    ["python", "-m", "py_compile", file_path],
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    timeout=5,
                )

                if result.returncode == 0:
                    self.log(f"✓ {file_path}")
                else:
                    self.log(f"✗ {file_path}: {result.stderr[:80]}")
                    all_pass = False
            except Exception as e:
                self.log(f"✗ {file_path}: {str(e)[:50]}")
                all_pass = False

        return all_pass

    def generate_fix_summary(self):
        """Generate comprehensive fix summary using Ollama."""
        self.section("Generating Fix Summary")

        prompt = """Summarize the TaskExecutor Flask integration implementation.

What was done:
1. ADR-004: Created Ollama-First Routing Architecture document
2. task_executor_service.py: Created Flask integration service adapter
3. task_routes.py: Created /api/v1/tasks REST endpoints
4. test_task_executor_fallback.py: Created comprehensive fallback tests
5. Env vars: Added to .env.example
6. Registration: Integrated routes into API blueprint

Key patterns:
- Thin service adapter wrapping claudeclockwork.TaskExecutor
- Lazy import with graceful ImportError handling
- Normalized response format (target_worker, model, output, cost, tokens_used, latency_ms)
- Rate limiting on task endpoints (10 per minute)
- JWT authentication required
- Escalation matrix: L0-L2 Ollama, L3-L4 Claude, L5 stop/ask

Output a brief summary suitable for documentation."""

        summary = self.run_ollama(prompt)
        print("\n" + "="*70)
        print("INTEGRATION SUMMARY")
        print("="*70)
        print(summary)

    def commit_all(self):
        """Commit all changes."""
        self.section("Committing Integration")

        if not self.files_modified:
            self.log("No files modified")
            return False

        try:
            subprocess.run(
                ["git", "add"] + self.files_modified,
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

            self.log(f"✓ Committed: {result.stdout.strip()}")
            return True
        except Exception as e:
            self.log(f"✗ Commit error: {str(e)[:50]}")
            return False

    def run(self):
        """Execute validation and fix workflow."""
        print("\n" + "="*70)
        print("  MASTER TASKEXECUTOR VALIDATION & FIX AGENT")
        print("="*70)

        # Phase 1: Test current state
        imports_ok = self.test_imports()

        # Phase 2: If imports fail, analyze and fix
        if not imports_ok:
            self.log("\nImports failed, attempting Ollama-based fix...")
            fixed = self.analyze_and_fix_imports()
            if fixed:
                # Re-test after fixes
                imports_ok = self.test_imports()

        # Phase 3: Verify registration
        routes_ok = self.verify_routes_registered()

        # Phase 4: Test compilation
        compile_ok = self.test_compilation()

        # Phase 5: Commit if any changes
        if self.files_modified:
            self.commit_all()

        # Phase 6: Generate summary
        self.generate_fix_summary()

        # Final status
        print("\n" + "="*70)
        success = imports_ok and routes_ok and compile_ok
        print(f"  Status: {'✓✓✓ ALL CHECKS PASSED' if success else '⚠ ISSUES DETECTED'}")
        print("="*70 + "\n")

        return success


if __name__ == "__main__":
    import sys
    agent = TaskExecutorValidationAgent()
    success = agent.run()
    sys.exit(0 if success else 1)
