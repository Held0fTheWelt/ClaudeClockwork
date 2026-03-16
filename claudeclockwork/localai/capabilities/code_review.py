"""Phase 23 — code.review capability: static code analysis and quality checks."""
from __future__ import annotations

import ast
import re
from typing import Any


class CodeReviewCapability:
    """Perform static code analysis and quality checks on generated Python code."""

    def review(self, code: str, archetype: str) -> dict[str, Any]:
        """
        Review code for quality issues using static analysis (no LLM).

        Args:
            code: Python source code to review
            archetype: Code archetype (scanner|validator|reporter|transformer|registry_helper)

        Returns:
            review_result dict with:
            - approved: bool (true if no critical issues)
            - issues: list of {file, line, severity, message}
            - suggestions: list of improvement suggestions
        """
        issues = []

        # Parse code to AST if possible
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            # If code has syntax errors, that's critical
            issues.append(
                {
                    "file": "<input>",
                    "line": e.lineno or 1,
                    "severity": "error",
                    "message": f"Syntax error: {e.msg}",
                }
            )
            tree = None

        # Run all checks
        if tree:
            issues.extend(self._check_docstrings(code, tree))
            issues.extend(self._check_error_handling(code, tree))
            issues.extend(self._check_naming(code, tree))

        issues.extend(self._check_style(code))

        # Determine approval based on critical issues
        critical_issues = [
            i for i in issues if i["severity"] in ("error", "warning")
        ]
        approved = len(critical_issues) == 0

        # Generate suggestions if not approved
        suggestions = []
        if not approved:
            suggestions = self._generate_suggestions(issues, code)

        return {
            "approved": approved,
            "issues": issues,
            "suggestions": suggestions,
        }

    def _check_docstrings(self, code: str, tree: ast.AST) -> list[dict[str, Any]]:
        """
        Check that all functions have docstrings.

        Returns:
            List of issues with severity='warning'
        """
        issues = []
        lines = code.split("\n")

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                if not docstring:
                    line_num = node.lineno
                    func_name = node.name
                    issues.append(
                        {
                            "file": "<input>",
                            "line": line_num,
                            "severity": "warning",
                            "message": f"Function {func_name}() missing docstring",
                        }
                    )

        return issues

    def _check_error_handling(self, code: str, tree: ast.AST) -> list[dict[str, Any]]:
        """
        Check for bare except clauses (must specify exception type).

        Returns:
            List of issues with severity='warning'
        """
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    if handler.type is None:
                        # Bare except clause
                        issues.append(
                            {
                                "file": "<input>",
                                "line": handler.lineno,
                                "severity": "warning",
                                "message": "Bare except clause - specify exception type",
                            }
                        )

        return issues

    def _check_style(self, code: str) -> list[dict[str, Any]]:
        """
        Check for style issues like inconsistent spacing.

        Returns:
            List of issues with severity='info'
        """
        issues = []
        lines = code.split("\n")

        # Check for inconsistent spacing around =
        # Pattern: multiple spaces before =
        for i, line in enumerate(lines, 1):
            # Skip lines that are comments or empty
            if line.strip().startswith("#") or not line.strip():
                continue

            # Check for multiple spaces before = (but not ==, !=, etc.)
            if re.search(r"\s\s+(?![=!<>])\w*\s*=(?!=)", line):
                issues.append(
                    {
                        "file": "<input>",
                        "line": i,
                        "severity": "info",
                        "message": "Inconsistent spacing around assignment operator",
                    }
                )

        return issues

    def _check_naming(self, code: str, tree: ast.AST) -> list[dict[str, Any]]:
        """
        Check that function names follow snake_case convention.

        Returns:
            List of issues with severity='info'
        """
        issues = []
        snake_case_pattern = re.compile(r"^[a-z_][a-z0-9_]*$")

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                # Skip dunder functions and internal functions
                if func_name.startswith("_"):
                    continue

                if not snake_case_pattern.match(func_name):
                    issues.append(
                        {
                            "file": "<input>",
                            "line": node.lineno,
                            "severity": "info",
                            "message": f"Function {func_name} should use snake_case",
                        }
                    )

        return issues

    def _generate_suggestions(
        self, issues: list[dict[str, Any]], code: str
    ) -> list[str]:
        """
        Generate improvement suggestions based on issues found.

        Returns:
            List of suggestion strings
        """
        suggestions = []
        seen = set()

        for issue in issues:
            msg = issue["message"]
            severity = issue["severity"]

            # Avoid duplicate suggestions
            if msg in seen:
                continue
            seen.add(msg)

            if "docstring" in msg.lower():
                if "docstring" not in str(suggestions):
                    suggestions.append(
                        "Add docstrings to all functions explaining their purpose, args, and return values"
                    )

            elif "except" in msg.lower():
                if "except" not in str(suggestions):
                    suggestions.append(
                        "Specify exception types in except clauses (e.g., except ValueError:) instead of bare except"
                    )

            elif "spacing" in msg.lower():
                if "spacing" not in str(suggestions):
                    suggestions.append(
                        "Fix inconsistent spacing around operators for better readability"
                    )

            elif "snake_case" in msg.lower():
                if "snake_case" not in str(suggestions):
                    suggestions.append(
                        "Rename functions to follow snake_case convention (lowercase with underscores)"
                    )

        # Add general suggestion if issues exist
        if not suggestions and issues:
            suggestions.append("Review code quality and address all flagged issues")

        return suggestions
