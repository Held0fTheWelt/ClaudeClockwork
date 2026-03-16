"""Phase 24 — code.validate capability: safety gate validation for generated code."""
from __future__ import annotations

import re
from typing import Any


class CodeValidateCapability:
    """Validate generated code against safety gates and security checks."""

    def validate(self, code: str, archetype: str) -> dict[str, Any]:
        """
        Validate code against safety gates.

        Args:
            code: Python source code to validate
            archetype: Code archetype (scanner|validator|reporter|transformer|registry_helper)

        Returns:
            validation_result dict with:
            - valid: bool (true if all checks pass)
            - checks: dict of check_name: bool (all must be true)
            - errors: list of error messages
        """
        checks = {}
        errors = []

        # Run all validation checks
        checks["no_forbidden_imports"] = self._check_forbidden_imports(code, errors)
        checks["no_dangerous_functions"] = self._check_dangerous_functions(code, errors)
        checks["no_eval_exec"] = self._check_eval_exec(code, errors)
        checks["no_os_system"] = self._check_os_system(code, errors)
        checks["no_subprocess"] = self._check_subprocess(code, errors)
        checks["has_main_function"] = self._check_has_main(code, archetype, errors)

        # All checks must pass
        valid = all(checks.values())

        return {
            "valid": valid,
            "checks": checks,
            "errors": errors,
        }

    def _check_forbidden_imports(self, code: str, errors: list[str]) -> bool:
        """Check that code doesn't import forbidden modules."""
        forbidden = ["pickle", "__import__", "importlib"]
        for module in forbidden:
            if re.search(rf"import\s+{module}\b", code):
                errors.append(f"Forbidden import: {module}")
                return False
        return True

    def _check_dangerous_functions(self, code: str, errors: list[str]) -> bool:
        """Check for dangerous function calls."""
        dangerous = [
            ("compile", r"compile\s*\("),
            ("globals", r"globals\s*\("),
            ("locals", r"locals\s*\("),
            ("vars", r"vars\s*\("),
            ("dir", r"dir\s*\("),
        ]
        for name, pattern in dangerous:
            if re.search(pattern, code):
                errors.append(f"Dangerous function call: {name}")
                return False
        return True

    def _check_eval_exec(self, code: str, errors: list[str]) -> bool:
        """Check for eval() and exec() calls."""
        if re.search(r"eval\s*\(", code):
            errors.append("Code contains eval() — disallowed for safety")
            return False
        if re.search(r"exec\s*\(", code):
            errors.append("Code contains exec() — disallowed for safety")
            return False
        return True

    def _check_os_system(self, code: str, errors: list[str]) -> bool:
        """Check for os.system() calls."""
        if re.search(r"os\.system\s*\(", code):
            errors.append("Code contains os.system() — disallowed for safety")
            return False
        return True

    def _check_subprocess(self, code: str, errors: list[str]) -> bool:
        """Check for subprocess module usage."""
        if re.search(r"subprocess\.", code):
            errors.append("Code uses subprocess module — disallowed for safety")
            return False
        if re.search(r"from\s+subprocess\s+import", code):
            errors.append("Code imports from subprocess — disallowed for safety")
            return False
        return True

    def _check_has_main(
        self, code: str, archetype: str, errors: list[str]
    ) -> bool:
        """Check that code has main function or entry point function.

        For validators: validate()
        For scanners: scan()
        For reporters: report()
        For transformers: transform()
        For registry_helpers: registry_op()

        Note: This check is lenient for schema/init files that may not have entry points.
        """
        entry_functions = {
            "validator": "validate",
            "scanner": "scan",
            "reporter": "report",
            "transformer": "transform",
            "registry_helper": "registry_op",
        }

        entry_func = entry_functions.get(archetype, "main")

        # Check for entry point function OR main function
        entry_pattern = rf"def\s+{entry_func}\s*\("
        main_pattern = r"def\s+main\s*\("

        has_entry = re.search(entry_pattern, code)
        has_main = re.search(main_pattern, code)

        # For schema.py and __init__.py, they don't need entry points
        # Only main.py must have the entry function
        # We pass validation if the code has either the entry function or main()
        if not (has_entry or has_main):
            # For non-main files, this is less critical
            # Allow pass if code looks like a schema/config file (dict definitions)
            if "INPUT_SCHEMA" in code or "OUTPUT_SCHEMA" in code:
                return True
            if "__version__" in code and "__all__" in code:
                return True

            errors.append(
                f"Code should have entry point function: {entry_func}()"
            )
            return False
        return True
