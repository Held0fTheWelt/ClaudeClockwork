"""Tests for Phase 69 — perf_artifact_gate."""

import pytest
from pathlib import Path
from claudeclockwork.core.gates.perf_artifact_gate import run_perf_artifact_gate


class TestPerfArtifactGatePasses:
    def test_passes_with_no_perf_dir(self, tmp_path):
        result = run_perf_artifact_gate(tmp_path)
        assert result["pass"] is True

    def test_passes_with_curated_only(self, tmp_path):
        perf = tmp_path / ".claude-performance"
        perf.mkdir()
        (perf / "README.md").write_text("# Performance\n")
        (perf / "reviews").mkdir()
        (perf / "reviews" / "run-EXAMPLE.json").write_text("{}")
        (perf / "charts").mkdir()
        (perf / "charts" / ".gitkeep").write_text("")
        result = run_perf_artifact_gate(tmp_path)
        assert result["pass"] is True, result["errors"]

    def test_passes_with_readme_only(self, tmp_path):
        perf = tmp_path / ".claude-performance"
        perf.mkdir()
        (perf / "README.md").write_text("# Curated\n")
        result = run_perf_artifact_gate(tmp_path)
        assert result["pass"] is True


class TestPerfArtifactGateBlocksReports:
    def test_blocks_file_in_reports_dir(self, tmp_path):
        perf = tmp_path / ".claude-performance"
        (perf / "reports").mkdir(parents=True)
        (perf / "reports" / "budget_run-unknown_report.md").write_text("# Report")
        result = run_perf_artifact_gate(tmp_path)
        assert result["pass"] is False
        assert any("reports" in e for e in result["errors"])

    def test_blocks_json_in_reports_dir(self, tmp_path):
        perf = tmp_path / ".claude-performance"
        (perf / "reports").mkdir(parents=True)
        (perf / "reports" / "budget_run-unknown_report.json").write_text("{}")
        result = run_perf_artifact_gate(tmp_path)
        assert result["pass"] is False

    def test_blocks_timestamped_report(self, tmp_path):
        perf = tmp_path / ".claude-performance"
        (perf / "reports").mkdir(parents=True)
        (perf / "reports" / "budget_run-unknown_report_20260308T095730Z.json").write_text("{}")
        result = run_perf_artifact_gate(tmp_path)
        assert result["pass"] is False


class TestPerfArtifactGateBlocksEvents:
    def test_blocks_file_in_events_dir(self, tmp_path):
        perf = tmp_path / ".claude-performance"
        (perf / "events").mkdir(parents=True)
        (perf / "events" / "run-unknown.jsonl").write_text("")
        result = run_perf_artifact_gate(tmp_path)
        assert result["pass"] is False
        assert any("events" in e for e in result["errors"])


class TestPerfArtifactGateMachinePatterns:
    def test_blocks_run_unknown_pattern(self, tmp_path):
        perf = tmp_path / ".claude-performance"
        perf.mkdir()
        (perf / "run-unknown-output.json").write_text("{}")
        result = run_perf_artifact_gate(tmp_path)
        assert result["pass"] is False

    def test_blocks_timestamp_pattern(self, tmp_path):
        perf = tmp_path / ".claude-performance"
        perf.mkdir()
        (perf / "budget_report_20260308T110000Z.json").write_text("{}")
        result = run_perf_artifact_gate(tmp_path)
        assert result["pass"] is False

    def test_blocks_performance_toggle(self, tmp_path):
        perf = tmp_path / ".claude-performance"
        perf.mkdir()
        (perf / "performance_toggle_20260308T110000Z.json").write_text("{}")
        result = run_perf_artifact_gate(tmp_path)
        assert result["pass"] is False
