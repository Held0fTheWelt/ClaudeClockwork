"""
Tests for Green Run Certificate Generator (Phase 66).

Tests:
1. Determinism: Re-running produces identical output (except timestamp)
2. Gate execution: All 7 gates run in correct order
3. Pass/Fail detection: Correctly identifies passing and failing gates
4. Certificate format: Output markdown is valid and well-formed
5. Synthetic failures: Detects gate failures properly
"""

import json
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from claudeclockwork.qa.reports.green_run import (
    GateResult,
    GreenRunResult,
    generate_green_run_certificate,
    run_all_gates,
    _generate_certificate_markdown,
    _read_version,
)


class TestGreenRunBasics:
    """Test basic green_run functionality."""

    def test_read_version_success(self, tmp_path: Path) -> None:
        """Test reading valid version file."""
        version_file = tmp_path / ".claude" / "VERSION"
        version_file.parent.mkdir(parents=True)
        version_file.write_text("17.7.319\n")

        version = _read_version(tmp_path)
        assert version == "17.7.319"

    def test_read_version_missing(self, tmp_path: Path) -> None:
        """Test reading missing version file."""
        version = _read_version(tmp_path)
        assert version is None

    def test_gate_result_creation(self) -> None:
        """Test GateResult namedtuple creation."""
        result = GateResult(
            gate_id="test_gate",
            gate_name="Test Gate",
            passed=True,
            errors=[],
            warnings=["test warning"],
            details={"key": "value"},
            phase=99,
        )

        assert result.gate_id == "test_gate"
        assert result.passed is True
        assert len(result.warnings) == 1
        assert result.phase == 99

    def test_green_run_result_creation(self) -> None:
        """Test GreenRunResult namedtuple creation."""
        gates = [
            GateResult(
                gate_id="gate1",
                gate_name="Gate 1",
                passed=True,
                errors=[],
                warnings=[],
                details={},
                phase=10,
            )
        ]

        result = GreenRunResult(
            timestamp="2026-03-08T12:00:00Z",
            canonical_version="17.7.319",
            gates=gates,
            overall_pass=True,
            pass_count=1,
            fail_count=0,
            warning_count=0,
            blockers=[],
            message="All pass",
        )

        assert result.overall_pass is True
        assert result.pass_count == 1
        assert len(result.gates) == 1


class TestCertificateGeneration:
    """Test certificate markdown generation."""

    def test_certificate_markdown_pass(self) -> None:
        """Test certificate markdown with all gates passing."""
        gates = [
            GateResult(
                gate_id="qa_gate",
                gate_name="QA Gate",
                passed=True,
                errors=[],
                warnings=[],
                details={"checks": 14},
                phase=10,
            ),
            GateResult(
                gate_id="planning_drift_scan",
                gate_name="Planning Drift",
                passed=True,
                errors=[],
                warnings=[],
                details={},
                phase=18,
            ),
        ]

        result = GreenRunResult(
            timestamp="2026-03-08T12:00:00Z",
            canonical_version="17.7.319",
            gates=gates,
            overall_pass=True,
            pass_count=2,
            fail_count=0,
            warning_count=0,
            blockers=[],
            message="All gates pass",
        )

        markdown = _generate_certificate_markdown(Path.cwd(), result)

        # Verify structure
        assert "# Green Run Release Candidate Certificate" in markdown
        assert "2026-03-08T12:00:00Z" in markdown
        assert "17.7.319" in markdown
        assert "CERTIFIED FOR RELEASE CANDIDATE" in markdown
        assert "GREEN RUN" in markdown
        assert "qa_gate" in markdown
        assert "planning_drift_scan" in markdown
        assert "✅ PASS" in markdown

    def test_certificate_markdown_fail(self) -> None:
        """Test certificate markdown with gates failing."""
        gates = [
            GateResult(
                gate_id="qa_gate",
                gate_name="QA Gate",
                passed=False,
                errors=["boot_check failed"],
                warnings=[],
                details={},
                phase=10,
            ),
        ]

        result = GreenRunResult(
            timestamp="2026-03-08T12:00:00Z",
            canonical_version="17.7.319",
            gates=gates,
            overall_pass=False,
            pass_count=0,
            fail_count=1,
            warning_count=0,
            blockers=["qa_gate: boot_check failed"],
            message="Gate failed",
        )

        markdown = _generate_certificate_markdown(Path.cwd(), result)

        # Verify failure state
        assert "NOT CERTIFIED" in markdown
        assert "❌ FAIL" in markdown
        assert "RED RUN" in markdown
        assert "boot_check failed" in markdown

    def test_certificate_markdown_format(self) -> None:
        """Test certificate markdown has required sections."""
        gates = [
            GateResult(
                gate_id="test",
                gate_name="Test Gate",
                passed=True,
                errors=[],
                warnings=[],
                details={},
                phase=10,
            )
        ]

        result = GreenRunResult(
            timestamp="2026-03-08T12:00:00Z",
            canonical_version="17.7.319",
            gates=gates,
            overall_pass=True,
            pass_count=1,
            fail_count=0,
            warning_count=0,
            blockers=[],
            message="Pass",
        )

        markdown = _generate_certificate_markdown(Path.cwd(), result)

        # Check required sections
        assert "# Green Run Release Candidate Certificate" in markdown
        assert "## Release Certification Status" in markdown
        assert "## Gate Verification Summary" in markdown
        assert "## Canonical Version" in markdown
        assert "## Release Readiness" in markdown
        assert "## Certificate Validation" in markdown


class TestGateExecution:
    """Test gate execution and ordering."""

    @mock.patch("claudeclockwork.qa.reports.green_run._run_qa_gate")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_planning_drift_scan")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_release_check")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_docs_gate")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_report_policy_gate")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_report_redaction_gate")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_runtime_root_gate")
    def test_gate_execution_order(
        self,
        mock_runtime,
        mock_redaction,
        mock_policy,
        mock_docs,
        mock_release,
        mock_drift,
        mock_qa,
        tmp_path: Path,
    ) -> None:
        """Test gates execute in correct stable order."""
        # Mock all gates to pass
        def make_gate(name: str, phase: int) -> GateResult:
            return GateResult(
                gate_id=name,
                gate_name=name,
                passed=True,
                errors=[],
                warnings=[],
                details={},
                phase=phase,
            )

        mock_qa.return_value = make_gate("qa_gate", 10)
        mock_drift.return_value = make_gate("planning_drift_scan", 18)
        mock_release.return_value = make_gate("release_check", 22)
        mock_docs.return_value = make_gate("docs_gate", 45)
        mock_policy.return_value = make_gate("report_policy_gate", 63)
        mock_redaction.return_value = make_gate("report_redaction_gate", 64)
        mock_runtime.return_value = make_gate("runtime_root_gate", 65)

        result = run_all_gates(tmp_path)

        # Verify all gates were called
        assert mock_qa.called
        assert mock_drift.called
        assert mock_release.called
        assert mock_docs.called
        assert mock_policy.called
        assert mock_redaction.called
        assert mock_runtime.called

        # Verify execution order by checking call order
        calls = [
            mock_qa.call_args,
            mock_drift.call_args,
            mock_release.call_args,
            mock_docs.call_args,
            mock_policy.call_args,
            mock_redaction.call_args,
            mock_runtime.call_args,
        ]
        assert all(c is not None for c in calls), "All gates should be called"

        # Verify result has all gates
        assert len(result.gates) == 7
        gate_ids = [g.gate_id for g in result.gates]
        assert gate_ids == [
            "qa_gate",
            "planning_drift_scan",
            "release_check",
            "docs_gate",
            "report_policy_gate",
            "report_redaction_gate",
            "runtime_root_gate",
        ]

    @mock.patch("claudeclockwork.qa.reports.green_run._run_qa_gate")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_planning_drift_scan")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_release_check")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_docs_gate")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_report_policy_gate")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_report_redaction_gate")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_runtime_root_gate")
    def test_gate_failure_detection(
        self,
        mock_runtime,
        mock_redaction,
        mock_policy,
        mock_docs,
        mock_release,
        mock_drift,
        mock_qa,
        tmp_path: Path,
    ) -> None:
        """Test failure detection across multiple gates."""
        def make_gate(name: str, phase: int, passed: bool) -> GateResult:
            return GateResult(
                gate_id=name,
                gate_name=name,
                passed=passed,
                errors=[] if passed else [f"{name} failed"],
                warnings=[],
                details={},
                phase=phase,
            )

        # Setup: qa_gate pass, planning_drift fail, others pass
        mock_qa.return_value = make_gate("qa_gate", 10, True)
        mock_drift.return_value = make_gate("planning_drift_scan", 18, False)
        mock_release.return_value = make_gate("release_check", 22, True)
        mock_docs.return_value = make_gate("docs_gate", 45, True)
        mock_policy.return_value = make_gate("report_policy_gate", 63, True)
        mock_redaction.return_value = make_gate("report_redaction_gate", 64, True)
        mock_runtime.return_value = make_gate("runtime_root_gate", 65, True)

        result = run_all_gates(tmp_path)

        # Verify counts
        assert result.pass_count == 6
        assert result.fail_count == 1
        assert result.overall_pass is False
        assert len(result.blockers) > 0
        assert "planning_drift_scan" in result.blockers[0]


class TestDeterminism:
    """Test certificate determinism."""

    @mock.patch("claudeclockwork.qa.reports.green_run.run_all_gates")
    def test_certificate_determinism(self, mock_run_all, tmp_path: Path) -> None:
        """Test that re-running produces identical output (except timestamp)."""
        # Mock run_all_gates to return consistent results
        gates = [
            GateResult(
                gate_id="qa_gate",
                gate_name="QA Gate",
                passed=True,
                errors=[],
                warnings=[],
                details={},
                phase=10,
            ),
            GateResult(
                gate_id="planning_drift_scan",
                gate_name="Planning Drift",
                passed=True,
                errors=[],
                warnings=[],
                details={},
                phase=18,
            ),
        ]

        # Return fixed timestamp for first call
        mock_run_all.return_value = GreenRunResult(
            timestamp="2026-03-08T12:00:00Z",
            canonical_version="17.7.319",
            gates=gates,
            overall_pass=True,
            pass_count=2,
            fail_count=0,
            warning_count=0,
            blockers=[],
            message="All pass",
        )

        # Generate certificate
        cert1 = generate_green_run_certificate(tmp_path)
        cert1_file = tmp_path / "Docs" / "green_run_certificate.md"
        cert1_content = cert1_file.read_text()

        # Mock returns different timestamp for second call
        mock_run_all.return_value = GreenRunResult(
            timestamp="2026-03-08T12:00:01Z",  # 1 second later
            canonical_version="17.7.319",
            gates=gates,
            overall_pass=True,
            pass_count=2,
            fail_count=0,
            warning_count=0,
            blockers=[],
            message="All pass",
        )

        # Generate again
        cert2 = generate_green_run_certificate(tmp_path)
        cert2_content = cert1_file.read_text()

        # Remove timestamp lines for comparison
        cert1_no_ts = "\n".join(
            [l for l in cert1_content.split("\n") if "2026-03-08T12:00:00Z" not in l]
        )
        cert2_no_ts = "\n".join(
            [l for l in cert2_content.split("\n") if "2026-03-08T12:00:01Z" not in l]
        )

        # Everything except timestamp should be identical
        assert cert1_no_ts == cert2_no_ts
        # But timestamps should differ
        assert "2026-03-08T12:00:00Z" in cert1_content
        assert "2026-03-08T12:00:01Z" in cert2_content


class TestSyntheticGateFailures:
    """Test detection of synthetic gate failures."""

    @mock.patch("claudeclockwork.qa.reports.green_run._run_qa_gate")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_planning_drift_scan")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_release_check")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_docs_gate")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_report_policy_gate")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_report_redaction_gate")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_runtime_root_gate")
    def test_synthetic_qa_gate_failure(
        self,
        mock_runtime,
        mock_redaction,
        mock_policy,
        mock_docs,
        mock_release,
        mock_drift,
        mock_qa,
        tmp_path: Path,
    ) -> None:
        """Test detection of synthetic QA gate failure."""
        def make_gate(name: str, phase: int) -> GateResult:
            return GateResult(
                gate_id=name,
                gate_name=name,
                passed=True,
                errors=[],
                warnings=[],
                details={},
                phase=phase,
            )

        # QA gate fails
        mock_qa.return_value = GateResult(
            gate_id="qa_gate",
            gate_name="QA Gate",
            passed=False,
            errors=["boot_check: cannot find boot_check.py"],
            warnings=[],
            details={},
            phase=10,
        )
        mock_drift.return_value = make_gate("planning_drift_scan", 18)
        mock_release.return_value = make_gate("release_check", 22)
        mock_docs.return_value = make_gate("docs_gate", 45)
        mock_policy.return_value = make_gate("report_policy_gate", 63)
        mock_redaction.return_value = make_gate("report_redaction_gate", 64)
        mock_runtime.return_value = make_gate("runtime_root_gate", 65)

        result = run_all_gates(tmp_path)

        assert result.overall_pass is False
        assert result.fail_count == 1
        assert result.pass_count == 6
        assert "qa_gate" in [g.gate_id for g in result.gates if not g.passed]

    @mock.patch("claudeclockwork.qa.reports.green_run._run_qa_gate")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_planning_drift_scan")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_release_check")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_docs_gate")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_report_policy_gate")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_report_redaction_gate")
    @mock.patch("claudeclockwork.qa.reports.green_run._run_runtime_root_gate")
    def test_synthetic_redaction_gate_failure(
        self,
        mock_runtime,
        mock_redaction,
        mock_policy,
        mock_docs,
        mock_release,
        mock_drift,
        mock_qa,
        tmp_path: Path,
    ) -> None:
        """Test detection of synthetic redaction gate failure."""
        def make_gate(name: str, phase: int) -> GateResult:
            return GateResult(
                gate_id=name,
                gate_name=name,
                passed=True,
                errors=[],
                warnings=[],
                details={},
                phase=phase,
            )

        mock_qa.return_value = make_gate("qa_gate", 10)
        mock_drift.return_value = make_gate("planning_drift_scan", 18)
        mock_release.return_value = make_gate("release_check", 22)
        mock_docs.return_value = make_gate("docs_gate", 45)
        mock_policy.return_value = make_gate("report_policy_gate", 63)
        # Redaction gate fails
        mock_redaction.return_value = GateResult(
            gate_id="report_redaction_gate",
            gate_name="Redaction Gate",
            passed=False,
            errors=["green_run_certificate.md:5: windows_drive_path D:\\project"],
            warnings=[],
            details={"violations_count": 1},
            phase=64,
        )
        mock_runtime.return_value = make_gate("runtime_root_gate", 65)

        result = run_all_gates(tmp_path)

        assert result.overall_pass is False
        assert result.fail_count == 1
        assert result.pass_count == 6
        failed_gates = [g.gate_id for g in result.gates if not g.passed]
        assert "report_redaction_gate" in failed_gates


class TestCertificateFileGeneration:
    """Test certificate file generation."""

    @mock.patch("claudeclockwork.qa.reports.green_run.run_all_gates")
    def test_certificate_file_created(self, mock_run_all, tmp_path: Path) -> None:
        """Test that certificate file is created at correct location."""
        gates = [
            GateResult(
                gate_id="test",
                gate_name="Test",
                passed=True,
                errors=[],
                warnings=[],
                details={},
                phase=10,
            )
        ]

        mock_run_all.return_value = GreenRunResult(
            timestamp="2026-03-08T12:00:00Z",
            canonical_version="17.7.319",
            gates=gates,
            overall_pass=True,
            pass_count=1,
            fail_count=0,
            warning_count=0,
            blockers=[],
            message="Pass",
        )

        output_path = tmp_path / "Docs" / "green_run_certificate.md"
        result = generate_green_run_certificate(tmp_path, output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "Green Run Release Candidate Certificate" in content
        assert "17.7.319" in content

    @mock.patch("claudeclockwork.qa.reports.green_run.run_all_gates")
    def test_certificate_custom_output(self, mock_run_all, tmp_path: Path) -> None:
        """Test certificate generation to custom output file."""
        gates = [
            GateResult(
                gate_id="test",
                gate_name="Test",
                passed=True,
                errors=[],
                warnings=[],
                details={},
                phase=10,
            )
        ]

        mock_run_all.return_value = GreenRunResult(
            timestamp="2026-03-08T12:00:00Z",
            canonical_version="17.7.319",
            gates=gates,
            overall_pass=True,
            pass_count=1,
            fail_count=0,
            warning_count=0,
            blockers=[],
            message="Pass",
        )

        custom_output = tmp_path / "custom_cert.md"
        result = generate_green_run_certificate(tmp_path, custom_output)

        assert custom_output.exists()
        content = custom_output.read_text()
        assert "Green Run Release Candidate Certificate" in content
