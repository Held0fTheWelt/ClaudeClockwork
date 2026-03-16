"""
Phase 64 — Tests for report redaction gate.

Validates that:
1. Gate passes when .report/ contains only redaction-safe markdown
2. Gate fails when paths or secrets appear in .report/**/*.md
3. Violations are properly reported with file, line, pattern, and context
4. Synthetic path and secret leaks are detected correctly
5. Multiple violations in same file and across files are tracked
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.core.gates.report_redaction_gate import (
    run_report_redaction_gate,
    scan_markdown_file,
    _extract_context,
)


class TestRedactionGateBasics:
    """Test basic gate functionality."""

    def test_gate_passes_with_no_report_dir(self, tmp_path: Path) -> None:
        """Gate should pass gracefully if .report/ doesn't exist."""
        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is True
        assert result["total_violations"] == 0
        assert "not found" in result.get("message", "").lower()

    def test_gate_passes_with_empty_report_dir(self, tmp_path: Path) -> None:
        """Gate should pass with empty .report/ directory."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()
        (report_dir / ".gitkeep").touch()

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is True
        assert result["total_violations"] == 0

    def test_gate_passes_with_clean_markdown(self, tmp_path: Path) -> None:
        """Gate should pass with clean markdown files (no paths or secrets)."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        clean_content = """# Phase 64 Redaction Gate

This is a curated report documenting the implementation of the redaction gate.

## Summary
- No absolute paths in this document
- Relative paths like ./data/ are safe
- Placeholders like <PROJECT_ROOT> are safe
- Example URLs like https://example.com are safe

## Implementation Details
The gate scans all markdown files and flags violations.
"""
        (report_dir / "Report_Phase64_Summary.md").write_text(clean_content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is True
        assert result["total_violations"] == 0
        assert result["scanned_files"] == 1


class TestWindowsDrivePaths:
    """Test detection of Windows drive paths."""

    def test_detects_windows_d_drive(self, tmp_path: Path) -> None:
        r"""Should detect D:\ drive paths."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "The project is located at D:\\ClaudeClockwork\\.claude\\config\\\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 1
        assert result["violations"][0]["pattern"] == "windows_drive_path"
        assert "D:\\" in result["violations"][0]["matched_text"]

    def test_detects_windows_c_drive(self, tmp_path: Path) -> None:
        r"""Should detect C:\ drive paths."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "File located at C:\\Users\\alice\\project\\\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 1

    def test_detects_windows_e_drive(self, tmp_path: Path) -> None:
        """Should detect various Windows drive letters."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "Backup on E:\\backups\\data\\\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 1

    def test_multiple_windows_drives_in_one_line(self, tmp_path: Path) -> None:
        """Should detect multiple drive paths in same line."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "Copy from D:\\source\\ to E:\\dest\\\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 2


class TestUnixHomePaths:
    """Test detection of Unix home paths."""

    def test_detects_users_path(self, tmp_path: Path) -> None:
        """Should detect /Users/ paths (macOS)."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "Project location: /Users/alice/projects/clockwork/\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 1
        assert result["violations"][0]["pattern"] == "unix_home_path"

    def test_detects_home_path(self, tmp_path: Path) -> None:
        """Should detect /home/ paths (Linux)."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "Development in /home/bob/.config/clockwork/\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 1


class TestWSLMountPaths:
    """Test detection of WSL mount paths."""

    def test_detects_wsl_d_mount(self, tmp_path: Path) -> None:
        """Should detect /mnt/d/ WSL mount paths."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "Working directory: /mnt/d/ClaudeClockwork/.claude/\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 1
        assert result["violations"][0]["pattern"] == "wsl_mount_path"

    def test_detects_wsl_c_mount(self, tmp_path: Path) -> None:
        """Should detect /mnt/c/ WSL mount paths."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "Windows drive at /mnt/c/Windows/System32/\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 1


class TestSystemAbsolutePaths:
    """Test detection of system absolute paths."""

    def test_detects_opt_path(self, tmp_path: Path) -> None:
        """Should detect /opt/ system paths."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "Installation: /opt/claude/bin/\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["violations"][0]["pattern"] == "system_absolute_path"

    def test_detects_workspace_path(self, tmp_path: Path) -> None:
        """Should detect /workspace/ paths."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "Project root: /workspace/clockwork/src/\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False

    def test_detects_var_path(self, tmp_path: Path) -> None:
        """Should detect /var/ system paths."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "Logs in /var/lib/reports/\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False

    def test_detects_srv_path(self, tmp_path: Path) -> None:
        """Should detect /srv/ service paths."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "Data at /srv/clockwork/data/\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False

    def test_detects_project_path(self, tmp_path: Path) -> None:
        """Should detect /project/ paths."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "Root: /project/clockwork/\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False


class TestSecretPatterns:
    """Test detection of secret-like strings."""

    def test_detects_api_key_assignment(self, tmp_path: Path) -> None:
        """Should detect api_key= assignments."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "Configuration: api_key=sk_live_1234567890abcdef\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["violations"][0]["pattern"] == "api_key_pattern"

    def test_detects_bearer_token(self, tmp_path: Path) -> None:
        """Should detect Bearer token patterns."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["violations"][0]["pattern"] == "bearer_token"

    def test_detects_secret_keyword(self, tmp_path: Path) -> None:
        """Should detect secret= assignments."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "secret=my_super_secret_value\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["violations"][0]["pattern"] == "secret_keyword"

    def test_detects_token_keyword(self, tmp_path: Path) -> None:
        """Should detect token= assignments."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "token: abc123def456xyz\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["violations"][0]["pattern"] == "token_keyword"

    def test_detects_password_keyword(self, tmp_path: Path) -> None:
        """Should detect password= assignments."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "password=MyP@ssw0rd123\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["violations"][0]["pattern"] == "password_keyword"

    def test_detects_credentials_keyword(self, tmp_path: Path) -> None:
        """Should detect credentials= assignments."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "credentials: username:password\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["violations"][0]["pattern"] == "credentials_keyword"


class TestLineNumbering:
    """Test that line numbers are correctly reported."""

    def test_violation_on_line_5(self, tmp_path: Path) -> None:
        """Should report correct line number for violations."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = """# Report

Clean line 2
Clean line 3
Clean line 4
D:\\ClaudeClockwork\\
"""
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["violations"][0]["line_number"] == 6

    def test_multiple_violations_on_different_lines(self, tmp_path: Path) -> None:
        """Should track all violations with correct line numbers."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = """# Report
D:\\ClaudeClockwork\\
/Users/alice/
/mnt/d/
"""
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 3

        line_numbers = sorted([v["line_number"] for v in result["violations"]])
        assert line_numbers == [2, 3, 4]


class TestContextExtraction:
    """Test context extraction around violations."""

    def test_context_includes_violation(self, tmp_path: Path) -> None:
        """Context should include the matched text."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = "Project location at D:\\ClaudeClockwork\\.claude\\config\\ for testing\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False

        context = result["violations"][0]["context"]
        assert "D:\\" in context or "D:" in context

    def test_context_extraction_function(self) -> None:
        """Test _extract_context helper function."""
        line = "Project located at D:\\ClaudeClockwork\\.claude\\"
        context = _extract_context(line, 19, 21)
        assert "D:\\" in context


class TestNestedDirectories:
    """Test scanning nested markdown files."""

    def test_scans_nested_report_directory(self, tmp_path: Path) -> None:
        """Should recursively scan nested .report/ directories."""
        report_dir = tmp_path / ".report"
        perf_dir = report_dir / "performance" / "run-unknown"
        perf_dir.mkdir(parents=True)

        content = "Results at /mnt/d/ClaudeClockwork/.report/\n"
        (perf_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 1
        assert "performance/run-unknown" in result["violations"][0]["file"]

    def test_counts_scanned_files(self, tmp_path: Path) -> None:
        """Should count all scanned markdown files."""
        report_dir = tmp_path / ".report"
        perf_dir = report_dir / "performance" / "run-unknown"
        perf_dir.mkdir(parents=True)

        routing_dir = report_dir / "routing"
        routing_dir.mkdir()

        (report_dir / "README.md").write_text("# Clean\n")
        (perf_dir / "report1.md").write_text("# Clean\n")
        (perf_dir / "report2.md").write_text("# Clean\n")
        (routing_dir / "report3.md").write_text("# Clean\n")

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is True
        assert result["scanned_files"] == 4


class TestMultipleViolationsInSameFile:
    """Test detection of multiple violations in the same file."""

    def test_multiple_paths_same_file(self, tmp_path: Path) -> None:
        """Should detect multiple violations in same file."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = """# Report
Located at D:\\ClaudeClockwork\\
Also at /Users/alice/
Config in /mnt/d/
Token: Bearer abc123
"""
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 4
        assert all(v["file"] == "report.md" for v in result["violations"])


class TestCaseSensitivity:
    """Test case sensitivity of pattern matching."""

    def test_case_insensitive_windows_drive(self, tmp_path: Path) -> None:
        """Should detect Windows drives regardless of case."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        # Lowercase drive should also match
        content = "Path: d:\\projects\\\n"
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        # Regex is case-insensitive [A-Za-z], so lowercase will match
        assert result["pass"] is False
        assert result["violations"][0]["pattern"] == "windows_drive_path"


class TestSafeContentPatterns:
    """Test that safe content is not flagged as violations."""

    def test_relative_paths_are_safe(self, tmp_path: Path) -> None:
        """Relative paths like ./data/ should not be flagged."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = """# Report
Relative path: ./data/reports/
Also safe: ../parent/
And: ./src/main.py
"""
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is True

    def test_placeholder_paths_are_safe(self, tmp_path: Path) -> None:
        """Placeholder paths like <PROJECT_ROOT> should not be flagged."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = """# Configuration
Use <PROJECT_ROOT> for configuration
Or {WORKSPACE} for workspace paths
And $HOME for home directory
"""
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is True

    def test_urls_are_safe(self, tmp_path: Path) -> None:
        """URLs should not be flagged."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = """# Links
Visit https://example.com/docs
Or http://api.example.com/v1/status
"""
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is True

    def test_non_assignment_keywords_are_safe(self, tmp_path: Path) -> None:
        """Keywords without assignments should not be flagged."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        content = """# Documentation
The secret_key variable is used internally.
Tokens are handled securely.
Passwords are hashed with bcrypt.
Credentials should be environment variables.
"""
        (report_dir / "report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is True


class TestScanMarkdownFileFunction:
    """Test the scan_markdown_file function directly."""

    def test_scan_file_returns_violations(self, tmp_path: Path) -> None:
        """scan_markdown_file should return list of violations."""
        file_path = tmp_path / "report.md"
        content = "Path: D:\\ClaudeClockwork\\\n"
        file_path.write_text(content)

        violations = scan_markdown_file(file_path)
        assert len(violations) == 1
        assert violations[0]["pattern"] == "windows_drive_path"
        assert violations[0]["line_number"] == 1

    def test_scan_file_with_no_violations(self, tmp_path: Path) -> None:
        """scan_markdown_file should return empty list for clean files."""
        file_path = tmp_path / "report.md"
        content = "# Clean Report\nNo violations here.\n"
        file_path.write_text(content)

        violations = scan_markdown_file(file_path)
        assert len(violations) == 0

    def test_scan_file_handles_missing_file(self, tmp_path: Path) -> None:
        """scan_markdown_file should handle missing files gracefully."""
        file_path = tmp_path / "nonexistent.md"

        violations = scan_markdown_file(file_path)
        assert len(violations) == 0

    def test_scan_file_with_unicode_content(self, tmp_path: Path) -> None:
        """scan_markdown_file should handle Unicode content."""
        file_path = tmp_path / "report.md"
        content = "# Rapport\nEmplacement: D:\\ClaudeClockwork\\\n"
        file_path.write_text(content, encoding="utf-8")

        violations = scan_markdown_file(file_path)
        assert len(violations) == 1


class TestSyntheticRealWorldScenarios:
    """Test realistic contamination scenarios."""

    def test_real_world_performance_report_scenario(self, tmp_path: Path) -> None:
        """Simulate real contamination scenario from Phase 63."""
        report_dir = tmp_path / ".report"
        perf_dir = report_dir / "performance" / "run-unknown"
        perf_dir.mkdir(parents=True)

        # Realistic content with path leaks (actual violation from Phase 63)
        content = """# Budget Report — run-unknown
- Generated: `2026-03-08T09:30:16Z`
- Events: **91**

## Charts
- `D:\\ClaudeClockwork\\.claude-performance\\reports\\charts\\budget_run-unknown_20260308T093016Z_tokens_by_role.png`
- `D:\\ClaudeClockwork\\.claude-performance\\reports\\charts\\budget_run-unknown_20260308T093016Z_tokens_by_model.png`
"""
        (perf_dir / "budget_budget_run-unknown_report.md").write_text(content)

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] >= 2
        assert result["scanned_files"] == 1

    def test_mixed_clean_and_contaminated_files(self, tmp_path: Path) -> None:
        """Simulate directory with both clean and contaminated files."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        # Clean file
        (report_dir / "Report_Phase64.md").write_text("# Clean Curated Report\n")

        # Contaminated file
        contaminated = tmp_path / ".report" / "contaminated.md"
        contaminated.write_text("Config at D:\\ClaudeClockwork\\\n")

        result = run_report_redaction_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 1
        assert result["scanned_files"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
