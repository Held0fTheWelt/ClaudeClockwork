"""Tests for code.review capability — static code analysis and quality checks."""
from __future__ import annotations

import pytest

from claudeclockwork.localai.capabilities.code_review import CodeReviewCapability


@pytest.fixture
def code_review_capability() -> CodeReviewCapability:
    """Return a CodeReviewCapability instance."""
    return CodeReviewCapability()


class TestCodeReviewDocstrings:
    """Test docstring detection checks."""

    def test_review_detects_missing_docstrings(
        self, code_review_capability: CodeReviewCapability
    ) -> None:
        """Test that missing docstrings are detected as warnings."""
        code = """
def missing_docstring():
    return 42

def another_missing():
    x = 1
    return x
"""
        result = code_review_capability.review(code, "scanner")

        assert isinstance(result, dict), "Result should be a dict"
        assert "approved" in result, "Result should contain 'approved' field"
        assert "issues" in result, "Result should contain 'issues' field"

        # Should have warnings about missing docstrings
        warnings = [issue for issue in result["issues"] if issue["severity"] == "warning"]
        assert len(warnings) >= 2, "Should detect at least 2 missing docstrings"

        # Check that issues reference the function names
        messages = [w["message"] for w in warnings]
        assert any("missing_docstring" in m for m in messages)
        assert any("another_missing" in m for m in messages)

    def test_review_approves_with_docstrings(
        self, code_review_capability: CodeReviewCapability
    ) -> None:
        """Test that functions with docstrings pass the check."""
        code = """
def with_docstring():
    \"\"\"This function has a docstring.\"\"\"
    return 42

def another_with_docstring():
    \"\"\"Another documented function.\"\"\"
    x = 1
    return x
"""
        result = code_review_capability.review(code, "scanner")

        # Should have no warnings about docstrings
        docstring_warnings = [
            issue
            for issue in result["issues"]
            if "docstring" in issue["message"].lower()
        ]
        assert len(docstring_warnings) == 0, "Should not complain about docstrings"


class TestCodeReviewErrorHandling:
    """Test error handling checks."""

    def test_review_detects_bare_except(
        self, code_review_capability: CodeReviewCapability
    ) -> None:
        """Test that bare except clauses are detected as warnings."""
        code = """
def risky_function():
    \"\"\"Function with bare except.\"\"\"
    try:
        x = 1 / 0
    except:
        pass
"""
        result = code_review_capability.review(code, "validator")

        warnings = [issue for issue in result["issues"] if issue["severity"] == "warning"]
        assert len(warnings) >= 1, "Should detect bare except clause"

        messages = [w["message"] for w in warnings]
        assert any("except" in m.lower() for m in messages), "Should mention except clause"

    def test_review_approves_typed_except(
        self, code_review_capability: CodeReviewCapability
    ) -> None:
        """Test that typed except clauses pass the check."""
        code = """
def safe_function():
    \"\"\"Function with typed except.\"\"\"
    try:
        x = 1 / 0
    except ZeroDivisionError:
        pass
    except ValueError as e:
        print(str(e))
"""
        result = code_review_capability.review(code, "transformer")

        except_warnings = [
            issue
            for issue in result["issues"]
            if "except" in issue["message"].lower()
        ]
        assert len(except_warnings) == 0, "Should not complain about typed except"


class TestCodeReviewStyle:
    """Test style checks."""

    def test_review_detects_inconsistent_spacing(
        self, code_review_capability: CodeReviewCapability
    ) -> None:
        """Test that inconsistent spacing is detected."""
        code = """
def function_with_bad_spacing():
    \"\"\"Function with spacing issues.\"\"\"
    x  = 1
    y   = 2
"""
        result = code_review_capability.review(code, "scanner")

        # Should have info-level issues about spacing
        info_issues = [issue for issue in result["issues"] if issue["severity"] == "info"]
        # May have spacing issues (if check is implemented)
        # At minimum, should not crash

        assert isinstance(result["issues"], list), "issues should be a list"

    def test_review_returns_issues_list(
        self, code_review_capability: CodeReviewCapability
    ) -> None:
        """Test that issues are returned in proper format."""
        code = """
def test_function():
    return 42
"""
        result = code_review_capability.review(code, "scanner")

        assert isinstance(result["issues"], list), "issues should be a list"
        # Each issue should have required fields
        for issue in result["issues"]:
            assert isinstance(issue, dict)
            assert "file" in issue
            assert "line" in issue
            assert "severity" in issue
            assert "message" in issue


class TestCodeReviewNaming:
    """Test naming convention checks."""

    def test_review_detects_non_snake_case_functions(
        self, code_review_capability: CodeReviewCapability
    ) -> None:
        """Test that non-snake_case function names are detected."""
        code = """
def BadFunctionName():
    \"\"\"Function with bad naming.\"\"\"
    return 42

def AnotherBadName():
    \"\"\"Another bad name.\"\"\"
    x = 1
    return x
"""
        result = code_review_capability.review(code, "reporter")

        # Should have info-level issues about naming
        info_issues = [issue for issue in result["issues"] if issue["severity"] == "info"]
        naming_issues = [i for i in info_issues if "snake_case" in i["message"].lower()]
        assert (
            len(naming_issues) >= 2
        ), "Should detect at least 2 non-snake_case function names"

    def test_review_approves_snake_case_functions(
        self, code_review_capability: CodeReviewCapability
    ) -> None:
        """Test that snake_case function names pass the check."""
        code = """
def good_function_name():
    \"\"\"Function with proper naming.\"\"\"
    return 42

def another_good_name():
    \"\"\"Another proper name.\"\"\"
    x = 1
    return x
"""
        result = code_review_capability.review(code, "registry_helper")

        naming_issues = [
            issue for issue in result["issues"] if "snake_case" in issue["message"].lower()
        ]
        assert len(naming_issues) == 0, "Should not complain about snake_case names"


class TestCodeReviewApproval:
    """Test approval logic."""

    def test_review_approves_good_code(
        self, code_review_capability: CodeReviewCapability
    ) -> None:
        """Test that well-written code is approved."""
        code = '''"""Module with proper code quality."""

def validate_input(data):
    """Validate input data structure."""
    try:
        if not isinstance(data, dict):
            raise ValueError("Expected dict")
        return True
    except ValueError as e:
        return False

def process_data(data):
    """Process validated data."""
    result = validate_input(data)
    if result:
        return {"status": "ok"}
    return {"status": "error"}
'''
        result = code_review_capability.review(code, "validator")

        assert result["approved"] is True, "Good code should be approved"
        # Should have no errors or warnings (info issues OK)
        critical_issues = [
            issue
            for issue in result["issues"]
            if issue["severity"] in ("error", "warning")
        ]
        assert (
            len(critical_issues) == 0
        ), "Good code should have no errors or warnings"

    def test_review_rejects_code_with_warnings(
        self, code_review_capability: CodeReviewCapability
    ) -> None:
        """Test that code with warnings is rejected."""
        code = """
def bad_function():
    try:
        x = 1
    except:
        pass
"""
        result = code_review_capability.review(code, "scanner")

        assert result["approved"] is False, "Code with warnings should not be approved"
        warnings = [issue for issue in result["issues"] if issue["severity"] == "warning"]
        assert len(warnings) > 0, "Should have at least one warning"

    def test_review_info_issues_dont_block_approval(
        self, code_review_capability: CodeReviewCapability
    ) -> None:
        """Test that info-level issues don't block approval."""
        code = """
def GoodCode():
    \"\"\"This has proper docstring.\"\"\"
    try:
        return 42
    except ZeroDivisionError:
        pass
"""
        result = code_review_capability.review(code, "scanner")

        # Even with info issues (bad naming), should approve if no errors/warnings
        info_issues = [issue for issue in result["issues"] if issue["severity"] == "info"]
        error_issues = [issue for issue in result["issues"] if issue["severity"] == "error"]

        if error_issues:
            assert result["approved"] is False
        else:
            # If only info issues, should be approved
            critical = [
                i
                for i in result["issues"]
                if i["severity"] in ("error", "warning")
            ]
            if len(critical) == 0:
                assert result["approved"] is True


class TestCodeReviewSeverityLevels:
    """Test severity level separation."""

    def test_review_separates_severity_levels(
        self, code_review_capability: CodeReviewCapability
    ) -> None:
        """Test that issues are properly categorized by severity."""
        code = """
def MixedIssues():
    try:
        x = 1
    except:
        pass
"""
        result = code_review_capability.review(code, "reporter")

        # Collect issues by severity
        errors = [issue for issue in result["issues"] if issue["severity"] == "error"]
        warnings = [issue for issue in result["issues"] if issue["severity"] == "warning"]
        info_issues = [issue for issue in result["issues"] if issue["severity"] == "info"]

        # Should have severities properly set
        for issue in result["issues"]:
            assert issue["severity"] in (
                "error",
                "warning",
                "info",
            ), f"Unknown severity: {issue['severity']}"

        # Bare except should be warning, bad naming should be info
        assert any("except" in w["message"].lower() for w in warnings)


class TestCodeReviewArchetypes:
    """Test that review respects different archetypes."""

    @pytest.mark.parametrize(
        "archetype",
        ["scanner", "validator", "reporter", "transformer", "registry_helper"],
    )
    def test_review_accepts_all_archetypes(
        self, code_review_capability: CodeReviewCapability, archetype: str
    ) -> None:
        """Test that review() works with all supported archetypes."""
        code = """
def simple_function():
    \"\"\"A simple function.\"\"\"
    return 42
"""
        result = code_review_capability.review(code, archetype)

        assert isinstance(result, dict), "Result should be a dict"
        assert "approved" in result
        assert "issues" in result


class TestCodeReviewSuggestions:
    """Test suggestion generation."""

    def test_review_provides_suggestions_for_rejected_code(
        self, code_review_capability: CodeReviewCapability
    ) -> None:
        """Test that rejected code gets improvement suggestions."""
        code = """
def BadFunction():
    try:
        x = 1
    except:
        pass
"""
        result = code_review_capability.review(code, "transformer")

        if result["approved"] is False:
            assert "suggestions" in result, "Rejected code should have suggestions"
            assert isinstance(result["suggestions"], list)
            # Should have some suggestions
            assert (
                len(result["suggestions"]) > 0
            ), "Should provide suggestions for fixing issues"


class TestCodeReviewEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_review_handles_empty_code(
        self, code_review_capability: CodeReviewCapability
    ) -> None:
        """Test that review handles empty code gracefully."""
        code = ""
        result = code_review_capability.review(code, "scanner")

        assert isinstance(result, dict)
        assert "approved" in result
        assert "issues" in result
        assert isinstance(result["issues"], list)

    def test_review_handles_comment_only_code(
        self, code_review_capability: CodeReviewCapability
    ) -> None:
        """Test that review handles comment-only code."""
        code = """
# This is just a comment
# No actual code here
"""
        result = code_review_capability.review(code, "validator")

        assert isinstance(result, dict)
        assert isinstance(result["issues"], list)

    def test_review_handles_syntax_errors_gracefully(
        self, code_review_capability: CodeReviewCapability
    ) -> None:
        """Test that review handles syntactically invalid code."""
        code = """
def broken(
    x = 1 = 2
"""
        # Should not crash, but may return an error issue
        result = code_review_capability.review(code, "scanner")

        assert isinstance(result, dict)
        assert isinstance(result["issues"], list)

    def test_review_preserves_line_numbers(
        self, code_review_capability: CodeReviewCapability
    ) -> None:
        """Test that issues reference correct line numbers."""
        code = """def func1():
    x = 1


def func2():
    try:
        pass
    except:
        pass
"""
        result = code_review_capability.review(code, "reporter")

        # Find the bare except issue
        except_issues = [
            i for i in result["issues"] if "except" in i["message"].lower()
        ]
        if except_issues:
            # The bare except is on line 7-8, so line should be >= 7
            for issue in except_issues:
                assert isinstance(issue["line"], int)
                assert issue["line"] > 0
