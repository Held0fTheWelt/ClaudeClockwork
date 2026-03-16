"""Tests for code.validate capability with deterministic safety gates."""
from __future__ import annotations

import json
import pytest

from claudeclockwork.localai.capabilities.code_validate import (
    CodeValidateCapability,
    ValidationGate,
)


class TestSyntaxGate:
    """Tests for syntax validation gate."""

    def test_syntax_gate_accepts_valid_python(self):
        """Syntax gate should accept valid Python code."""
        code = """
def hello_world():
    print("Hello, World!")
    return 42
"""
        gate = ValidationGate("syntax")
        result = gate.check(code)
        assert result["ok"] is True
        assert "error" not in result

    def test_syntax_gate_rejects_invalid_python(self):
        """Syntax gate should reject invalid Python syntax."""
        code = """
def broken_function(
    # missing closing paren
    pass
"""
        gate = ValidationGate("syntax")
        result = gate.check(code)
        assert result["ok"] is False
        assert "error" in result
        assert result["error"]  # Should have error message


class TestImportsGate:
    """Tests for forbidden imports gate."""

    def test_imports_gate_forbids_socket(self):
        """Imports gate should reject socket imports."""
        code = """
import socket
s = socket.socket()
"""
        gate = ValidationGate("imports")
        result = gate.check(code)
        assert result["ok"] is False
        assert "error" in result
        assert "socket" in result["error"]

    def test_imports_gate_forbids_requests(self):
        """Imports gate should reject requests imports."""
        code = """
import requests
response = requests.get('http://example.com')
"""
        gate = ValidationGate("imports")
        result = gate.check(code)
        assert result["ok"] is False
        assert "error" in result
        assert "requests" in result["error"]

    def test_imports_gate_forbids_urllib(self):
        """Imports gate should reject urllib imports."""
        code = """
from urllib import request
"""
        gate = ValidationGate("imports")
        result = gate.check(code)
        assert result["ok"] is False
        assert "error" in result
        assert "urllib" in result["error"]

    def test_imports_gate_allows_safe_imports(self):
        """Imports gate should allow safe standard library imports."""
        code = """
import json
import os
from pathlib import Path
"""
        gate = ValidationGate("imports")
        result = gate.check(code)
        assert result["ok"] is True
        assert "error" not in result


class TestForbiddenPatternsGate:
    """Tests for forbidden patterns gate."""

    def test_forbidden_patterns_rejects_shell_true(self):
        """Forbidden patterns gate should reject shell=True."""
        code = """
import subprocess
subprocess.run(['ls', '-l'], shell=True)
"""
        gate = ValidationGate("forbidden_patterns")
        result = gate.check(code)
        assert result["ok"] is False
        assert "error" in result
        assert "shell=True" in result["error"]

    def test_forbidden_patterns_rejects_os_system(self):
        """Forbidden patterns gate should reject os.system."""
        code = """
import os
os.system('rm -rf /')
"""
        gate = ValidationGate("forbidden_patterns")
        result = gate.check(code)
        assert result["ok"] is False
        assert "error" in result
        assert "os.system" in result["error"]

    def test_forbidden_patterns_rejects_eval(self):
        """Forbidden patterns gate should reject eval."""
        code = """
user_input = "1 + 1"
result = eval(user_input)
"""
        gate = ValidationGate("forbidden_patterns")
        result = gate.check(code)
        assert result["ok"] is False
        assert "error" in result
        assert "eval" in result["error"]

    def test_forbidden_patterns_rejects_exec(self):
        """Forbidden patterns gate should reject exec."""
        code = """
code_string = "print('dangerous')"
exec(code_string)
"""
        gate = ValidationGate("forbidden_patterns")
        result = gate.check(code)
        assert result["ok"] is False
        assert "error" in result
        assert "exec" in result["error"]

    def test_forbidden_patterns_allows_safe_code(self):
        """Forbidden patterns gate should allow safe code."""
        code = """
def safe_function(x, y):
    return x + y
"""
        gate = ValidationGate("forbidden_patterns")
        result = gate.check(code)
        assert result["ok"] is True
        assert "error" not in result


class TestAllowedRootsGate:
    """Tests for allowed write roots gate."""

    def test_allowed_roots_enforces_write_paths(self):
        """Allowed roots gate should reject writes outside allowed paths."""
        code = """
with open('/etc/passwd', 'w') as f:
    f.write('dangerous')
"""
        gate = ValidationGate("allowed_roots", allowed_roots=["/tmp"])
        result = gate.check(code)
        assert result["ok"] is False
        assert "error" in result

    def test_allowed_roots_allows_safe_writes(self):
        """Allowed roots gate should allow writes in allowed paths."""
        code = """
with open('/tmp/output.txt', 'w') as f:
    f.write('safe data')
"""
        gate = ValidationGate("allowed_roots", allowed_roots=["/tmp"])
        result = gate.check(code)
        assert result["ok"] is True
        assert "error" not in result

    def test_allowed_roots_read_only_if_empty(self):
        """Allowed roots gate should be read-only if allowed_roots is empty."""
        code = """
with open('/tmp/output.txt', 'w') as f:
    f.write('safe data')
"""
        gate = ValidationGate("allowed_roots", allowed_roots=[])
        result = gate.check(code)
        assert result["ok"] is False
        assert "error" in result


class TestSmokeTestGate:
    """Tests for smoke test gate."""

    def test_smoke_test_executes_with_sample_input(self):
        """Smoke test gate should execute code with sample input."""
        code = """
import json
import sys

data = json.loads(sys.argv[1])
result = {"success": True, "value": data.get("x", 0) + data.get("y", 0)}
print(json.dumps(result))
"""
        gate = ValidationGate("smoke_test")
        sample_input = {"x": 5, "y": 3}
        result = gate.execute(code, sample_input, timeout=5)
        assert result["ok"] is True
        assert "output" in result
        # Output should be valid JSON
        output = json.loads(result["output"])
        assert output["success"] is True
        assert output["value"] == 8

    def test_smoke_test_detects_non_zero_exit(self):
        """Smoke test gate should detect non-zero exit codes."""
        code = """
import sys
sys.exit(1)
"""
        gate = ValidationGate("smoke_test")
        result = gate.execute(code, {}, timeout=5)
        assert result["ok"] is False
        assert "error" in result

    def test_smoke_test_detects_invalid_json_output(self):
        """Smoke test gate should reject non-JSON output."""
        code = """
print("not json")
"""
        gate = ValidationGate("smoke_test")
        result = gate.execute(code, {}, timeout=5)
        assert result["ok"] is False
        assert "error" in result

    def test_smoke_test_respects_timeout(self):
        """Smoke test gate should respect timeout."""
        code = """
import time
time.sleep(10)
"""
        gate = ValidationGate("smoke_test")
        result = gate.execute(code, {}, timeout=1)
        assert result["ok"] is False
        assert "error" in result


class TestValidatePipeline:
    """Tests for the full validation pipeline."""

    def test_validate_pipeline_all_gates_pass(self):
        """All gates passing should result in successful validation."""
        code = """
import json
import sys

data = json.loads(sys.argv[1])
result = {"value": data.get("x", 0) + 1}
print(json.dumps(result))
"""
        capability = CodeValidateCapability()
        constraints = {
            "allowed_write_roots": [],
            "forbidden_patterns": [],
            "example_input": {"x": 5},
        }
        result = capability.validate(code, constraints, timeout=5)

        assert result["passed"] is True
        assert result["checks"]["syntax"]["ok"] is True
        assert result["checks"]["imports"]["ok"] is True
        assert result["checks"]["forbidden_patterns"]["ok"] is True
        assert result["checks"]["allowed_roots"]["ok"] is True
        assert result["checks"]["schema_presence"]["ok"] is True
        assert result["checks"]["smoke_test"]["ok"] is True
        assert "timestamp" in result
        assert "task_id" in result

    def test_validate_pipeline_fails_on_any_gate_failure(self):
        """Pipeline should fail if any gate fails."""
        code = """
import socket
import json

s = socket.socket()
"""
        capability = CodeValidateCapability()
        constraints = {
            "allowed_write_roots": [],
            "forbidden_patterns": [],
            "example_input": {},
        }
        result = capability.validate(code, constraints, timeout=5)

        assert result["passed"] is False
        assert result["checks"]["imports"]["ok"] is False
        assert "socket" in result["checks"]["imports"]["error"]

    def test_validate_pipeline_fails_on_syntax_error(self):
        """Pipeline should fail on syntax errors."""
        code = """
def broken(:
    pass
"""
        capability = CodeValidateCapability()
        constraints = {
            "allowed_write_roots": [],
            "forbidden_patterns": [],
            "example_input": {},
        }
        result = capability.validate(code, constraints, timeout=5)

        assert result["passed"] is False
        assert result["checks"]["syntax"]["ok"] is False
        assert "error" in result["checks"]["syntax"]

    def test_validate_pipeline_fails_on_forbidden_pattern(self):
        """Pipeline should fail on forbidden patterns."""
        code = """
import subprocess
subprocess.run(['ls'], shell=True)
"""
        capability = CodeValidateCapability()
        constraints = {
            "allowed_write_roots": [],
            "forbidden_patterns": [],
            "example_input": {},
        }
        result = capability.validate(code, constraints, timeout=5)

        assert result["passed"] is False
        assert result["checks"]["forbidden_patterns"]["ok"] is False
        assert "shell=True" in result["checks"]["forbidden_patterns"]["error"]

    def test_validate_pipeline_returns_proper_schema(self):
        """Validation result should match expected schema."""
        code = """
import json
import sys
print(json.dumps({"ok": True}))
"""
        capability = CodeValidateCapability()
        constraints = {
            "allowed_write_roots": [],
            "forbidden_patterns": [],
            "example_input": {},
        }
        result = capability.validate(code, constraints, timeout=5)

        # Check schema
        assert isinstance(result, dict)
        assert "task_id" in result
        assert "passed" in result
        assert "checks" in result
        assert "timestamp" in result

        # Check checks substructure
        assert "syntax" in result["checks"]
        assert "imports" in result["checks"]
        assert "forbidden_patterns" in result["checks"]
        assert "allowed_roots" in result["checks"]
        assert "schema_presence" in result["checks"]
        assert "smoke_test" in result["checks"]

        # Each check should have ok and optional error
        for check_name, check_result in result["checks"].items():
            assert "ok" in check_result
            assert isinstance(check_result["ok"], bool)
