"""Code validation capability with deterministic safety gates."""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4


class ValidationGate:
    """Deterministic validation gate for Python code safety."""

    # Forbidden module imports (no network access)
    FORBIDDEN_IMPORTS = {"socket", "requests", "urllib"}

    # Forbidden patterns (no code execution, no shell escaping)
    DEFAULT_FORBIDDEN_PATTERNS = [
        r"shell\s*=\s*True",  # subprocess.run(..., shell=True)
        r"os\.system\s*\(",   # os.system(...)
        r"\beval\s*\(",       # eval(...)
        r"\bexec\s*\(",       # exec(...)
    ]

    def __init__(self, gate_type: str, **options):
        """
        Initialize a validation gate.

        Args:
            gate_type: Type of gate (syntax, imports, forbidden_patterns, allowed_roots, schema_presence, smoke_test)
            **options: Gate-specific options (allowed_roots, forbidden_patterns, etc.)
        """
        self.gate_type = gate_type
        self.options = options

    def check(self, code: str) -> Dict[str, Any]:
        """
        Check code against the gate (no execution).

        Returns:
            Dict with keys: ok (bool), error (optional str)
        """
        if self.gate_type == "syntax":
            return self._check_syntax(code)
        elif self.gate_type == "imports":
            return self._check_imports(code)
        elif self.gate_type == "forbidden_patterns":
            return self._check_forbidden_patterns(code)
        elif self.gate_type == "allowed_roots":
            return self._check_allowed_roots(code)
        elif self.gate_type == "schema_presence":
            return self._check_schema_presence(code)
        else:
            return {"ok": False, "error": f"Unknown gate type: {self.gate_type}"}

    def execute(self, code: str, sample_input: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """
        Execute code and check results (smoke test).

        Args:
            code: Python source code
            sample_input: Sample input dict to pass as JSON argument
            timeout: Timeout in seconds

        Returns:
            Dict with keys: ok (bool), output (optional str), error (optional str)
        """
        if self.gate_type != "smoke_test":
            return {"ok": False, "error": f"execute() only works with smoke_test gate"}

        return self._smoke_test(code, sample_input, timeout)

    def _check_syntax(self, code: str) -> Dict[str, Any]:
        """Syntax gate: parse code with ast.parse()."""
        try:
            ast.parse(code)
            return {"ok": True}
        except SyntaxError as e:
            return {"ok": False, "error": f"Syntax error: {e.msg} at line {e.lineno}"}
        except Exception as e:
            return {"ok": False, "error": f"Parse error: {str(e)}"}

    def _check_imports(self, code: str) -> Dict[str, Any]:
        """Imports gate: forbid socket, requests, urllib."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            # If syntax is bad, imports gate passes (syntax gate catches it)
            return {"ok": True}

        forbidden_found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.FORBIDDEN_IMPORTS:
                        forbidden_found.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module in self.FORBIDDEN_IMPORTS:
                    forbidden_found.append(node.module)
                # Also check urllib.* imports
                if node.module and node.module.startswith("urllib"):
                    forbidden_found.append(node.module)

        if forbidden_found:
            return {
                "ok": False,
                "error": f"Forbidden imports found: {', '.join(set(forbidden_found))}",
            }
        return {"ok": True}

    def _check_forbidden_patterns(self, code: str) -> Dict[str, Any]:
        """Forbidden patterns gate: reject shell=True, os.system, eval, exec."""
        provided_patterns = self.options.get("forbidden_patterns")
        # Always include default forbidden patterns
        patterns = list(self.DEFAULT_FORBIDDEN_PATTERNS)
        # Add any user-provided patterns if any
        if provided_patterns:
            patterns.extend(provided_patterns)

        found_patterns = []
        for pattern in patterns:
            if re.search(pattern, code, re.DOTALL):
                found_patterns.append(pattern)

        if found_patterns:
            # Return a user-friendly error message
            matches = []
            for pattern in found_patterns:
                if r"shell\s*=\s*True" in pattern:
                    matches.append("shell=True")
                elif r"os\.system" in pattern:
                    matches.append("os.system")
                elif r"\beval\s*\(" in pattern:
                    matches.append("eval")
                elif r"\bexec\s*\(" in pattern:
                    matches.append("exec")
            return {
                "ok": False,
                "error": f"Forbidden patterns found: {', '.join(matches)}",
            }
        return {"ok": True}

    def _check_allowed_roots(self, code: str) -> Dict[str, Any]:
        """Allowed roots gate: file writes must be in allowed_roots."""
        allowed_roots = self.options.get("allowed_roots", [])

        # If allowed_roots is empty, no writes allowed (read-only)
        if not allowed_roots:
            # Check if code tries to open() with 'w' mode
            if re.search(r"open\s*\(\s*['\"][^'\"]*['\"]\s*,\s*['\"]w", code):
                return {
                    "ok": False,
                    "error": "File writes not allowed (empty allowed_roots)",
                }
            return {"ok": True}

        # Check if writes go outside allowed roots
        # Look for open(..., 'w') patterns
        write_pattern = r"open\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]w"
        matches = re.finditer(write_pattern, code)

        for match in matches:
            path = match.group(1)
            allowed = False
            for root in allowed_roots:
                if path.startswith(root):
                    allowed = True
                    break
            if not allowed:
                return {
                    "ok": False,
                    "error": f"File write outside allowed roots: {path}",
                }

        return {"ok": True}

    def _check_schema_presence(self, code: str) -> Dict[str, Any]:
        """Schema presence gate: placeholder (always pass for now)."""
        return {"ok": True}

    def _smoke_test(
        self, code: str, sample_input: Dict[str, Any], timeout: int
    ) -> Dict[str, Any]:
        """Execute code with sample input and verify output is valid JSON."""
        try:
            # Convert sample_input to JSON string
            sample_json = json.dumps(sample_input)

            # Write code to temp file and execute
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as f:
                f.write(code)
                temp_file = f.name

            try:
                # Run code with sample input as JSON argument
                result = subprocess.run(
                    [sys.executable, temp_file, sample_json],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )

                # Check exit code
                if result.returncode != 0:
                    return {
                        "ok": False,
                        "error": f"Exit code {result.returncode}: {result.stderr}",
                    }

                # Check output is valid JSON
                output = result.stdout.strip()
                try:
                    json.loads(output)
                except json.JSONDecodeError:
                    return {
                        "ok": False,
                        "error": f"Output is not valid JSON: {output}",
                    }

                return {"ok": True, "output": output}

            finally:
                Path(temp_file).unlink(missing_ok=True)

        except subprocess.TimeoutExpired:
            return {"ok": False, "error": f"Execution timeout after {timeout}s"}
        except Exception as e:
            return {"ok": False, "error": f"Execution error: {str(e)}"}


class CodeValidateCapability:
    """Code validation capability with all deterministic gates."""

    def validate(
        self, code: str, constraints: Dict[str, Any], timeout: int = 5
    ) -> Dict[str, Any]:
        """
        Validate code against all gates.

        Args:
            code: Python source code
            constraints: Dict with keys:
                - allowed_write_roots: list of paths where writes are allowed
                - forbidden_patterns: list of additional regex patterns to forbid
                - example_input: dict to use for smoke test
            timeout: Timeout for smoke test in seconds

        Returns:
            Dict with keys:
                - task_id: str
                - passed: bool (all gates must pass)
                - checks: dict of gate results
                - timestamp: ISO timestamp
        """
        task_id = str(uuid4())
        checks = {}

        # Gate 1: Syntax
        syntax_gate = ValidationGate("syntax")
        checks["syntax"] = syntax_gate.check(code)

        # If syntax fails, skip other parse-dependent gates but continue
        if not checks["syntax"]["ok"]:
            # Still run all other gates for comprehensive report
            checks["imports"] = ValidationGate("imports").check(code)
            checks["forbidden_patterns"] = ValidationGate(
                "forbidden_patterns",
                forbidden_patterns=constraints.get("forbidden_patterns") or [],
            ).check(code)
            checks["allowed_roots"] = ValidationGate(
                "allowed_roots",
                allowed_roots=constraints.get("allowed_write_roots", []),
            ).check(code)
            checks["schema_presence"] = ValidationGate("schema_presence").check(code)
            checks["smoke_test"] = {"ok": False, "error": "Skipped due to syntax error"}

            passed = False
        else:
            # Gate 2: Imports
            imports_gate = ValidationGate("imports")
            checks["imports"] = imports_gate.check(code)

            # Gate 3: Forbidden Patterns
            forbidden_gate = ValidationGate(
                "forbidden_patterns",
                forbidden_patterns=constraints.get("forbidden_patterns") or [],
            )
            checks["forbidden_patterns"] = forbidden_gate.check(code)

            # Gate 4: Allowed Roots
            roots_gate = ValidationGate(
                "allowed_roots",
                allowed_roots=constraints.get("allowed_write_roots", []),
            )
            checks["allowed_roots"] = roots_gate.check(code)

            # Gate 5: Schema Presence
            schema_gate = ValidationGate("schema_presence")
            checks["schema_presence"] = schema_gate.check(code)

            # Gate 6: Smoke Test
            smoke_gate = ValidationGate("smoke_test")
            example_input = constraints.get("example_input", {})
            checks["smoke_test"] = smoke_gate.execute(code, example_input, timeout)

            # All gates must pass
            passed = all(check["ok"] for check in checks.values())

        timestamp = datetime.now(timezone.utc).isoformat()

        return {
            "task_id": task_id,
            "passed": passed,
            "checks": checks,
            "timestamp": timestamp,
        }
