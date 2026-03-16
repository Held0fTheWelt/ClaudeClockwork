"""Tests for Phase 70 — doc_path_leak_gate."""

import pytest
from pathlib import Path
from claudeclockwork.core.gates.doc_path_leak_gate import run_doc_path_leak_gate


def _make_doc(tmp_path, subdir, filename, content):
    d = tmp_path / subdir
    d.mkdir(parents=True, exist_ok=True)
    (d / filename).write_text(content, encoding="utf-8")


class TestDocPathLeakGatePasses:
    def test_passes_with_empty_repo(self, tmp_path):
        result = run_doc_path_leak_gate(tmp_path)
        assert result["pass"] is True

    def test_passes_with_clean_markdown(self, tmp_path):
        _make_doc(tmp_path, "Docs", "clean.md", "# Title\n\nNo paths here.\n")
        result = run_doc_path_leak_gate(tmp_path)
        assert result["pass"] is True

    def test_passes_with_placeholder(self, tmp_path):
        _make_doc(tmp_path, "Docs", "ok.md", "Path: `<PROJECT_ROOT>/some/file.md`\n")
        result = run_doc_path_leak_gate(tmp_path)
        assert result["pass"] is True

    def test_passes_with_username_placeholder(self, tmp_path):
        _make_doc(tmp_path, "mvps", "ok.md", "e.g. `/Users/<username>/projects/`\n")
        result = run_doc_path_leak_gate(tmp_path)
        assert result["pass"] is True


class TestDocPathLeakGateDetectsWindows:
    def test_detects_d_drive(self, tmp_path):
        _make_doc(tmp_path, "Docs", "leak.md", "Path: `D:\\ClaudeClockwork\\file.py`\n")
        result = run_doc_path_leak_gate(tmp_path)
        assert result["pass"] is False
        assert any("D:\\" in e or "D:" in e for e in result["errors"])

    def test_detects_c_drive(self, tmp_path):
        _make_doc(tmp_path, "mvps", "leak.md", "Installed at `C:\\Program Files\\tool`\n")
        result = run_doc_path_leak_gate(tmp_path)
        assert result["pass"] is False

    def test_detects_e_drive(self, tmp_path):
        _make_doc(tmp_path, ".project/Docs", "leak.md", "Data: `E:\\data\\reports`\n")
        result = run_doc_path_leak_gate(tmp_path)
        assert result["pass"] is False


class TestDocPathLeakGateDetectsUnix:
    def test_detects_home_path(self, tmp_path):
        _make_doc(tmp_path, "Docs", "leak.md", "Output: `/home/alice/project/`\n")
        result = run_doc_path_leak_gate(tmp_path)
        assert result["pass"] is False

    def test_detects_users_path(self, tmp_path):
        _make_doc(tmp_path, ".claude/governance", "leak.md", "Run: `/Users/bob/work/file.py`\n")
        result = run_doc_path_leak_gate(tmp_path)
        assert result["pass"] is False

    def test_detects_wsl_mnt_path(self, tmp_path):
        _make_doc(tmp_path, ".claude/agents", "leak.md", "Located at `/mnt/d/ClaudeClockwork/`\n")
        result = run_doc_path_leak_gate(tmp_path)
        assert result["pass"] is False


class TestDocPathLeakGateScoping:
    def test_only_scans_curated_dirs(self, tmp_path):
        # File outside curated dirs — not scanned
        outside = tmp_path / "scripts"
        outside.mkdir()
        (outside / "leak.md").write_text("Path: `/home/user/data`\n")
        result = run_doc_path_leak_gate(tmp_path)
        assert result["pass"] is True

    def test_reports_file_and_line_number(self, tmp_path):
        _make_doc(tmp_path, "Docs", "report.md", "# Title\n\nPath: `D:\\leak.txt`\n")
        result = run_doc_path_leak_gate(tmp_path)
        assert result["pass"] is False
        assert any(":3:" in e for e in result["errors"])
