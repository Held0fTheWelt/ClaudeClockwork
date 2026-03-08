"""
Phase 65 — Runtime root gate tests.

Validates that:
1. Gate passes when .llama_runtime is stubbed (README.md + .gitkeep only)
2. Gate fails when non-stub files appear in .llama_runtime
3. Gate fails when code references .llama_runtime
4. Gate fails when docs reference .llama_runtime (non-deprecation)
5. Synthetic violations are detected deterministically
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.core.gates.runtime_root_gate import (
    run_runtime_root_gate,
    _check_llama_runtime_stub,
    _check_code_references,
    _check_doc_references,
)


ROOT = Path(__file__).resolve().parents[1]


class TestRuntimeRootGateBasics:
    """Test basic gate functionality."""

    def test_gate_passes_with_proper_stub(self) -> None:
        """Gate should pass when .llama_runtime has only README.md + .gitkeep."""
        result = run_runtime_root_gate(ROOT)
        assert result["pass"] is True, f"Gate failed unexpectedly: {result['violations']}"
        assert result["total_violations"] == 0
        assert "passed" in result["message"].lower()

    def test_gate_structure_returns_required_fields(self) -> None:
        """Gate result must contain pass, violations, message, total_violations."""
        result = run_runtime_root_gate(ROOT)
        assert "pass" in result
        assert "violations" in result
        assert "message" in result
        assert "total_violations" in result
        assert isinstance(result["pass"], bool)
        assert isinstance(result["violations"], list)
        assert isinstance(result["total_violations"], int)


class TestLlamaRuntimeStubViolations:
    """Test .llama_runtime stub validation."""

    def test_stub_check_passes_with_readme_and_gitkeep(self, tmp_path: Path) -> None:
        """Stub check passes with README.md + .gitkeep."""
        llama_rt = tmp_path / ".llama_runtime"
        llama_rt.mkdir()
        (llama_rt / ".gitkeep").touch()
        (llama_rt / "README.md").write_text("# DEPRECATED\nThis is a stub.")

        violations = _check_llama_runtime_stub(tmp_path)
        assert violations == []

    def test_stub_check_fails_with_extra_files(self, tmp_path: Path) -> None:
        """Stub check fails when .llama_runtime has non-stub files."""
        llama_rt = tmp_path / ".llama_runtime"
        llama_rt.mkdir()
        (llama_rt / ".gitkeep").touch()
        (llama_rt / "README.md").write_text("# DEPRECATED")
        (llama_rt / "extra_file.txt").write_text("This should not be here")

        violations = _check_llama_runtime_stub(tmp_path)
        assert len(violations) > 0
        assert any("extra_file.txt" in v for v in violations)

    def test_stub_check_fails_with_extra_directory(self, tmp_path: Path) -> None:
        """Stub check fails when .llama_runtime has non-stub subdirectories."""
        llama_rt = tmp_path / ".llama_runtime"
        llama_rt.mkdir()
        (llama_rt / ".gitkeep").touch()
        (llama_rt / "README.md").write_text("# DEPRECATED")
        (llama_rt / "eval").mkdir()
        (llama_rt / "eval" / "results.json").write_text("{}")

        violations = _check_llama_runtime_stub(tmp_path)
        assert len(violations) > 0
        assert any("eval" in v for v in violations)

    def test_stub_check_fails_with_missing_deprecation_notice(self, tmp_path: Path) -> None:
        """Stub check fails if README.md lacks deprecation notice."""
        llama_rt = tmp_path / ".llama_runtime"
        llama_rt.mkdir()
        (llama_rt / ".gitkeep").touch()
        (llama_rt / "README.md").write_text("# Old Runtime\nNo deprecation marker here.")

        violations = _check_llama_runtime_stub(tmp_path)
        assert len(violations) > 0
        assert any("deprecation" in v.lower() for v in violations)

    def test_gate_fails_with_non_stub_llama_runtime(self, tmp_path: Path) -> None:
        """Full gate fails when .llama_runtime contains non-stub files."""
        llama_rt = tmp_path / ".llama_runtime"
        llama_rt.mkdir()
        (llama_rt / ".gitkeep").touch()
        (llama_rt / "README.md").write_text("# DEPRECATED")
        (llama_rt / "brain").mkdir()
        (llama_rt / "brain" / "stats.json").write_text("{}")

        # Create minimal .claude/ structure to pass as project root
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "__init__.py").touch()

        result = run_runtime_root_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] > 0


class TestCodeReferencesDetection:
    """Test detection of .llama_runtime in code."""

    def test_code_check_passes_with_no_references(self, tmp_path: Path) -> None:
        """Code check passes when no .llama_runtime references exist."""
        claudeclockwork = tmp_path / "claudeclockwork"
        claudeclockwork.mkdir()
        (claudeclockwork / "__init__.py").write_text("# Clean code")
        (claudeclockwork / "core").mkdir()
        (claudeclockwork / "core" / "module.py").write_text(
            "def foo():\n    path = '.clockwork_runtime'\n    return path"
        )

        violations = _check_code_references(tmp_path)
        assert violations == []

    def test_code_check_detects_reference_in_python(self, tmp_path: Path) -> None:
        """Code check detects .llama_runtime in Python files."""
        claudeclockwork = tmp_path / "claudeclockwork"
        claudeclockwork.mkdir()
        (claudeclockwork / "__init__.py").touch()
        (claudeclockwork / "bad_module.py").write_text(
            'runtime_path = ".llama_runtime"\npath = runtime_path + "/data"'
        )

        violations = _check_code_references(tmp_path)
        assert len(violations) > 0
        assert any("bad_module.py" in v for v in violations)
        assert any(".llama_runtime" in v for v in violations)

    def test_code_check_allows_legacy_scripts(self, tmp_path: Path) -> None:
        """Code check ignores migrate_runtime_root.py (legacy script)."""
        scripts = tmp_path / "scripts"
        scripts.mkdir()
        (scripts / "migrate_runtime_root.py").write_text(
            'src = ".llama_runtime"\ndst = ".clockwork_runtime"'
        )

        violations = _check_code_references(tmp_path)
        assert violations == []  # Legacy script excluded

    def test_code_check_allows_mvp_phase19_docs(self, tmp_path: Path) -> None:
        """Code check ignores MVP Phase 19 (historical context)."""
        mvps = tmp_path / "mvps"
        mvps.mkdir()
        (mvps / "MVP_Phase19_RuntimeRootNormalization.md").write_text(
            "# Phase 19\nMigrate from .llama_runtime to .clockwork_runtime"
        )

        # Note: _check_code_references only scans .py files, so .md is ignored anyway
        violations = _check_code_references(tmp_path)
        assert violations == []


class TestDocReferencesDetection:
    """Test detection of .llama_runtime in documentation."""

    def test_doc_check_passes_with_no_references(self, tmp_path: Path) -> None:
        """Doc check passes when no .llama_runtime references exist."""
        docs = tmp_path / ".project" / "Docs"
        docs.mkdir(parents=True)
        (docs / "Guide.md").write_text("# Guide\nUse .clockwork_runtime for state.")

        violations = _check_doc_references(tmp_path)
        assert violations == []

    def test_doc_check_detects_reference_in_markdown(self, tmp_path: Path) -> None:
        """Doc check detects .llama_runtime in markdown files."""
        docs = tmp_path / ".project" / "Docs"
        docs.mkdir(parents=True)
        (docs / "BadDoc.md").write_text("# Old Design\nStore data in .llama_runtime\n")

        violations = _check_doc_references(tmp_path)
        assert len(violations) > 0
        assert any("BadDoc.md" in v for v in violations)

    def test_doc_check_allows_deprecation_context(self, tmp_path: Path) -> None:
        """Doc check allows .llama_runtime when mentioned in deprecation context."""
        docs = tmp_path / ".project" / "Docs"
        docs.mkdir(parents=True)
        (docs / "Note.md").write_text(
            "# Deprecation\nThe legacy .llama_runtime directory is now deprecated."
        )

        violations = _check_doc_references(tmp_path)
        assert violations == []  # "deprecated" in text triggers allow

    def test_doc_check_skips_migration_docs(self, tmp_path: Path) -> None:
        """Doc check skips Ref_RuntimeMigrationLlamaToClockwork.md."""
        refs = tmp_path / ".project" / "Docs" / "References"
        refs.mkdir(parents=True)
        (refs / "Ref_RuntimeMigrationLlamaToClockwork.md").write_text(
            "# Migration\nFrom .llama_runtime to .clockwork_runtime\n"
            "Inventory of .llama_runtime: ...\n"
        )

        violations = _check_doc_references(tmp_path)
        assert violations == []

    def test_doc_check_skips_phase65_docs(self, tmp_path: Path) -> None:
        """Doc check skips MVP_Phase65 documents."""
        mvps = tmp_path / "mvps"
        mvps.mkdir()
        (mvps / "MVP_Phase65_RuntimeRootCleanup_AntiCoupling.md").write_text(
            "# Phase 65\n.llama_runtime was the old root.\n"
        )

        violations = _check_doc_references(tmp_path)
        assert violations == []


class TestSyntheticViolations:
    """Test that gate detects synthetic reintroduction scenarios."""

    def test_synthetic_stub_violation_detected(self, tmp_path: Path) -> None:
        """Gate detects when someone adds files to .llama_runtime stub."""
        # Setup clean stub
        llama_rt = tmp_path / ".llama_runtime"
        llama_rt.mkdir()
        (llama_rt / ".gitkeep").touch()
        (llama_rt / "README.md").write_text("# DEPRECATED\nStub only.")

        # Synthesize violation: someone adds old eval data
        (llama_rt / "eval").mkdir()
        (llama_rt / "eval" / "results.json").write_text('{"results": []}')

        result = run_runtime_root_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] > 0
        assert any("eval" in v for v in result["violations"])

    def test_synthetic_code_reference_detected(self, tmp_path: Path) -> None:
        """Gate detects when someone adds .llama_runtime reference back to code."""
        # Setup minimal structure
        (tmp_path / ".llama_runtime").mkdir()
        (tmp_path / ".llama_runtime" / ".gitkeep").touch()
        (tmp_path / ".llama_runtime" / "README.md").write_text("# DEPRECATED")

        claudeclockwork = tmp_path / "claudeclockwork"
        claudeclockwork.mkdir()
        (claudeclockwork / "__init__.py").touch()

        # Synthesize violation: new code references .llama_runtime
        (claudeclockwork / "new_feature.py").write_text(
            "def get_runtime_path():\n"
            '    return ".llama_runtime" + "/data"\n'
        )

        result = run_runtime_root_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] > 0
        assert any("new_feature.py" in v for v in result["violations"])

    def test_synthetic_doc_reference_detected(self, tmp_path: Path) -> None:
        """Gate detects when someone adds .llama_runtime reference to active docs."""
        # Setup minimal structure
        (tmp_path / ".llama_runtime").mkdir()
        (tmp_path / ".llama_runtime" / ".gitkeep").touch()
        (tmp_path / ".llama_runtime" / "README.md").write_text("# DEPRECATED")

        docs = tmp_path / ".project" / "Docs" / "Plans"
        docs.mkdir(parents=True)

        # Synthesize violation: new plan doc references .llama_runtime inappropriately
        (docs / "Plan_NewFeature.md").write_text(
            "# New Feature\n"
            "Store telemetry in .llama_runtime for persistence.\n"
        )

        result = run_runtime_root_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] > 0
        assert any("Plan_NewFeature.md" in v for v in result["violations"])

    def test_synthetic_multi_violation_scenario(self, tmp_path: Path) -> None:
        """Gate detects multiple simultaneous violations."""
        # Violate stub constraint
        llama_rt = tmp_path / ".llama_runtime"
        llama_rt.mkdir()
        (llama_rt / "README.md").write_text("# Old")
        (llama_rt / "knowledge").mkdir()
        (llama_rt / "knowledge" / "ledger.jsonl").write_text("")

        # Violate code constraint
        claudeclockwork = tmp_path / "claudeclockwork"
        claudeclockwork.mkdir()
        (claudeclockwork / "__init__.py").touch()
        (claudeclockwork / "runtime_mgr.py").write_text(
            'rt = ".llama_runtime" + "/writes"'
        )

        # Violate docs constraint
        docs = tmp_path / ".project" / "Docs" / "Review"
        docs.mkdir(parents=True)
        (docs / "Review_Feature.md").write_text(
            "Implement .llama_runtime sync feature"
        )

        result = run_runtime_root_gate(tmp_path)
        assert result["pass"] is False
        assert result["total_violations"] >= 3  # At least 3 violations


class TestGateCLI:
    """Test CLI entry point."""

    def test_gate_cli_returns_0_on_pass(self) -> None:
        """CLI returns 0 when gate passes."""
        from claudeclockwork.core.gates.runtime_root_gate import main

        # On the actual repo, gate should pass
        exit_code = main()
        assert exit_code == 0
