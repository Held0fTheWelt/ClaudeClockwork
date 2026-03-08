"""
Phase 63 — Tests for report policy gate.

Validates that:
1. Gate passes when .report/ contains only curated markdown
2. Gate fails when runtime files (JSON, PNG, etc.) appear in .report/
3. Violations are properly reported with details
4. Synthetic violations are detected correctly
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.core.gates.report_policy_gate import (
    run_report_policy_gate,
    _is_allowed_file,
    _is_forbidden_file,
)


class TestReportPolicyGateBasics:
    """Test basic gate functionality."""

    def test_gate_passes_with_no_report_dir(self, tmp_path: Path) -> None:
        """Gate should pass gracefully if .report/ doesn't exist."""
        result = run_report_policy_gate(tmp_path)
        assert result["pass"] is True
        assert result["total_violations"] == 0
        assert "not found" in result.get("message", "").lower()

    def test_gate_passes_with_empty_report_dir(self, tmp_path: Path) -> None:
        """Gate should pass with empty .report/ directory."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()
        (report_dir / ".gitkeep").touch()

        result = run_report_policy_gate(tmp_path)
        assert result["pass"] is True
        assert result["total_violations"] == 0

    def test_gate_passes_with_curated_markdown(self, tmp_path: Path) -> None:
        """Gate should pass with curated markdown files in .report/."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()
        (report_dir / ".gitkeep").touch()
        (report_dir / "Report_Phase63_Summary.md").write_text("# Curated Report\n")
        (report_dir / "README.md").write_text("# Report Directory\n")

        result = run_report_policy_gate(tmp_path)
        assert result["pass"] is True
        assert result["total_violations"] == 0


class TestReportPolicyGateViolations:
    """Test violation detection."""

    def test_gate_fails_with_json_runtime_file(self, tmp_path: Path) -> None:
        """Gate should fail when .json runtime file appears in .report/."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()
        (report_dir / "budget_budget_run-unknown_20260307T113732Z.json").write_text("{}")

        result = run_report_policy_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 1
        assert len(result["violations"]) == 1

        v = result["violations"][0]
        assert "budget_budget_run-unknown" in v["path"]
        assert v["file_type"] == "JSON runtime metric/report"
        assert ".clockwork_runtime" in v["reason"]

    def test_gate_fails_with_png_chart_file(self, tmp_path: Path) -> None:
        """Gate should fail when .png chart file appears in .report/."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()
        (report_dir / "budget_run-unknown_20260307T113732Z_cost_by_model.png").write_text("fake")

        result = run_report_policy_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 1

        v = result["violations"][0]
        assert "cost_by_model.png" in v["path"]
        assert v["file_type"] == "PNG/image generated chart"

    def test_gate_fails_with_multiple_runtime_files(self, tmp_path: Path) -> None:
        """Gate should detect multiple violations."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()
        (report_dir / "file1.json").write_text("{}")
        (report_dir / "file2.json").write_text("{}")
        (report_dir / "chart.png").write_text("fake")

        result = run_report_policy_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 3
        assert len(result["violations"]) == 3

    def test_gate_detects_routing_outcome_files(self, tmp_path: Path) -> None:
        """Gate should detect model_routing_outcome_*.json files."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()
        (report_dir / "model_routing_outcome_20260307-220832.json").write_text("{}")

        result = run_report_policy_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 1
        assert "model_routing_outcome" in result["violations"][0]["path"]

    def test_gate_detects_qa_gate_files(self, tmp_path: Path) -> None:
        """Gate should detect qa_gate_*.json files."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()
        (report_dir / "qa_gate_20260307T224351Z.json").write_text("{}")

        result = run_report_policy_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 1
        assert "qa_gate" in result["violations"][0]["path"]


class TestReportPolicyGateDirectoryStructure:
    """Test behavior with nested directories."""

    def test_gate_scans_nested_directories(self, tmp_path: Path) -> None:
        """Gate should recursively scan nested directories in .report/."""
        report_dir = tmp_path / ".report"
        perf_dir = report_dir / "performance" / "run-unknown"
        perf_dir.mkdir(parents=True)

        (perf_dir / "budget_budget_run-unknown_20260307T113732Z.json").write_text("{}")
        (perf_dir / "curated_report.md").write_text("# OK\n")

        result = run_report_policy_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 1
        assert "performance/run-unknown" in result["violations"][0]["path"]

    def test_gate_handles_nested_charts(self, tmp_path: Path) -> None:
        """Gate should detect PNG charts in nested chart subdirectories."""
        report_dir = tmp_path / ".report"
        charts_dir = report_dir / "performance" / "run-unknown" / "charts"
        charts_dir.mkdir(parents=True)

        (charts_dir / "budget_run-unknown_20260307T113732Z_cost_by_model.png").write_text("fake")

        result = run_report_policy_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 1
        assert "charts" in result["violations"][0]["path"]


class TestAllowedFilePatterns:
    """Test file pattern matching for allowed files."""

    def test_curated_markdown_files_are_allowed(self) -> None:
        """Curated markdown files (Report_* pattern) should be allowed."""
        assert _is_allowed_file(Path("Report_Phase63.md")) is True
        assert _is_allowed_file(Path("Report_Summary.md")) is True

    def test_readme_markdown_is_allowed(self) -> None:
        """README.md should be allowed."""
        assert _is_allowed_file(Path("README.md")) is True

    def test_auto_generated_markdown_not_allowed(self) -> None:
        """Auto-generated markdown with timestamps should not be allowed."""
        assert _is_allowed_file(Path("budget_budget_run-unknown_report_20260307T113732Z.md")) is False
        assert _is_allowed_file(Path("report_20260308.md")) is False

    def test_gitkeep_is_allowed(self) -> None:
        """Git placeholder files should be allowed."""
        assert _is_allowed_file(Path(".gitkeep")) is True

    def test_other_files_not_allowed_by_is_allowed_file(self) -> None:
        """Non-curated files return False from is_allowed_file."""
        assert _is_allowed_file(Path("data.json")) is False
        assert _is_allowed_file(Path("chart.png")) is False
        assert _is_allowed_file(Path("report.md")) is False  # Plain .md not matching curated pattern


class TestForbiddenFilePatterns:
    """Test file pattern matching for forbidden files."""

    def test_json_files_are_forbidden(self) -> None:
        """JSON files should be detected as forbidden."""
        assert _is_forbidden_file(Path("budget_budget_run-unknown_20260307T113732Z.json")) is True
        assert _is_forbidden_file(Path("model_routing_outcome_20260307.json")) is True
        assert _is_forbidden_file(Path("qa_gate_20260307T224351Z.json")) is True

    def test_png_files_are_forbidden(self) -> None:
        """PNG chart files should be detected as forbidden."""
        assert _is_forbidden_file(Path("budget_run-unknown_20260307T113732Z_cost_by_model.png")) is True
        assert _is_forbidden_file(Path("chart.png")) is True

    def test_image_files_are_forbidden(self) -> None:
        """Various image formats should be forbidden."""
        assert _is_forbidden_file(Path("image.jpg")) is True
        assert _is_forbidden_file(Path("image.jpeg")) is True
        assert _is_forbidden_file(Path("image.gif")) is True

    def test_csv_files_are_forbidden(self) -> None:
        """CSV/TSV files should be forbidden."""
        assert _is_forbidden_file(Path("data.csv")) is True
        assert _is_forbidden_file(Path("data.tsv")) is True

    def test_curated_markdown_not_forbidden(self) -> None:
        """Curated markdown files should not be forbidden."""
        assert _is_forbidden_file(Path("Report_Summary.md")) is False
        assert _is_forbidden_file(Path("README.md")) is False

    def test_auto_generated_markdown_is_forbidden(self) -> None:
        """Auto-generated markdown with timestamp patterns is forbidden."""
        assert _is_forbidden_file(Path("budget_budget_run-unknown_report_20260307T113732Z.md")) is True
        assert _is_forbidden_file(Path("model_routing_report_20260308.md")) is True


class TestSyntheticRuntimeScenarios:
    """Test realistic runtime contamination scenarios."""

    def test_synthetic_performance_reports_scenario(self, tmp_path: Path) -> None:
        """Simulate a real-world scenario with performance report contamination."""
        report_dir = tmp_path / ".report"
        perf_dir = report_dir / "performance" / "run-unknown"
        perf_dir.mkdir(parents=True)

        # Realistic files that should be migrated
        (perf_dir / "budget_budget_run-unknown_report.md").write_text("# Report\n")
        (perf_dir / "budget_budget_run-unknown_report_20260307T113732Z.md").write_text("# Report\n")
        (perf_dir / "budget_budget_run-unknown_20260307T113732Z.json").write_text("{}")
        (perf_dir / "budget_budget_run-unknown_report_20260307T113732Z.md").write_text("# Report\n")

        charts_dir = perf_dir / "charts"
        charts_dir.mkdir()
        (charts_dir / "budget_run-unknown_20260307T113732Z_cost_by_model.png").write_bytes(b"PNG")
        (charts_dir / "budget_run-unknown_20260307T113732Z_cost_by_role.png").write_bytes(b"PNG")

        result = run_report_policy_gate(tmp_path)
        assert result["pass"] is False

        # Should detect JSON and PNG files
        json_violations = [v for v in result["violations"] if v["file_type"] == "JSON runtime metric/report"]
        png_violations = [v for v in result["violations"] if v["file_type"] == "PNG/image generated chart"]

        assert len(json_violations) >= 1
        assert len(png_violations) >= 2

    def test_synthetic_routing_scenario(self, tmp_path: Path) -> None:
        """Simulate routing metrics contamination."""
        report_dir = tmp_path / ".report"
        routing_dir = report_dir / "routing" / "run-unknown"
        routing_dir.mkdir(parents=True)

        # Realistic routing files
        (routing_dir / "model_routing_outcome_20260307-220832.json").write_text("{}")
        (routing_dir / "model_routing_report_20260307-220832.json").write_text("{}")

        result = run_report_policy_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 2

    def test_synthetic_qa_contamination(self, tmp_path: Path) -> None:
        """Simulate QA gate logs contamination."""
        report_dir = tmp_path / ".report"
        qa_dir = report_dir / "qa"
        qa_dir.mkdir(parents=True)

        # QA gate logs that should be moved
        (qa_dir / "qa_gate_20260307T224351Z.json").write_text("{}")
        (qa_dir / "qa_gate_20260307T224401Z.json").write_text("{}")

        result = run_report_policy_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 2


class TestMixedScenarios:
    """Test scenarios with both curated and runtime content."""

    def test_mixed_curated_and_runtime_files(self, tmp_path: Path) -> None:
        """Gate should allow curated markdown but reject runtime files in same directory."""
        report_dir = tmp_path / ".report"
        report_dir.mkdir()

        # Curated content
        (report_dir / "Report_Phase63_Summary.md").write_text("# Curated\n")

        # Runtime files (contamination)
        (report_dir / "runtime_metrics.json").write_text("{}")

        result = run_report_policy_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] == 1

        # Curated file not in violations
        curated_files = [v["path"] for v in result["violations"]]
        assert "Report_Phase63_Summary.md" not in curated_files
        assert "runtime_metrics.json" in curated_files


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
