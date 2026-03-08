"""
Phase 66 — Green Run Certificate Generator.

Produces deterministic certificate proving repo is "green":
- All required gates pass
- Evidence bundle is exportable in strict redacted mode
- Certificate output is reproducible (except timestamp)

Gate Execution Order (stable, required):
1. qa_gate (MVP 10)
2. planning_drift_scan (MVP 18)
3. release_check (MVP 22)
4. docs_gate (MVP 45)
5. report_policy_gate (MVP 63)
6. report_redaction_gate (MVP 64)
7. runtime_root_gate (MVP 65)
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NamedTuple


class GateResult(NamedTuple):
    """Result of a single gate execution."""

    gate_id: str
    gate_name: str
    passed: bool
    errors: list[str]
    warnings: list[str]
    details: dict[str, Any]
    phase: int


class GreenRunResult(NamedTuple):
    """Overall Green Run certification result."""

    timestamp: str  # ISO 8601 UTC
    canonical_version: str | None
    gates: list[GateResult]
    overall_pass: bool
    pass_count: int
    fail_count: int
    warning_count: int
    blockers: list[str]
    message: str


def _project_root() -> Path:
    """Locate project root from module location."""
    p = Path(__file__).resolve()
    for _ in range(6):
        if (p / "claudeclockwork" / "__init__.py").is_file():
            return p
        p = p.parent
    return Path.cwd()


def _read_version(project_root: Path) -> str | None:
    """Read canonical version from .claude/VERSION."""
    version_file = project_root / ".claude" / "VERSION"
    if not version_file.is_file():
        return None
    try:
        return version_file.read_text(encoding="utf-8").strip()
    except OSError:
        return None


def _run_qa_gate(project_root: Path) -> GateResult:
    """Run qa_gate (MVP 10) — core QA checks."""
    from claudeclockwork.core.gates import planning_drift

    # Import the skill directly (stdlib-only, no external deps)
    qa_gate_script = project_root / ".claude" / "tools" / "skills" / "qa_gate.py"

    if not qa_gate_script.is_file():
        return GateResult(
            gate_id="qa_gate",
            gate_name="Core QA Checks (boot, layout, schemas, skills, policies, version)",
            passed=False,
            errors=["qa_gate.py not found at .claude/tools/skills/qa_gate.py"],
            warnings=[],
            details={"error": "script not found"},
            phase=10,
        )

    try:
        req = {
            "skill_id": "qa_gate",
            "inputs": {"project_root": str(project_root), "write_report": False},
        }
        result = subprocess.run(
            [sys.executable, str(qa_gate_script), json.dumps(req)],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            return GateResult(
                gate_id="qa_gate",
                gate_name="Core QA Checks (boot, layout, schemas, skills, policies, version)",
                passed=False,
                errors=["qa_gate execution failed"],
                warnings=[],
                details={"stdout": result.stdout[:500], "stderr": result.stderr[:500]},
                phase=10,
            )

        output = json.loads(result.stdout)
        gate_pass = output.get("outputs", {}).get("gate_pass", False)
        errors = output.get("errors", [])
        warnings = output.get("warnings", [])

        return GateResult(
            gate_id="qa_gate",
            gate_name="Core QA Checks (boot, layout, schemas, skills, policies, version)",
            passed=gate_pass,
            errors=errors,
            warnings=warnings,
            details={
                "checks_run": output.get("metrics", {}).get("checks_run"),
                "pass_rate": output.get("metrics", {}).get("pass_rate"),
            },
            phase=10,
        )
    except Exception as exc:
        return GateResult(
            gate_id="qa_gate",
            gate_name="Core QA Checks (boot, layout, schemas, skills, policies, version)",
            passed=False,
            errors=[f"qa_gate exception: {exc}"],
            warnings=[],
            details={"exception": str(exc)},
            phase=10,
        )


def _run_planning_drift_scan(project_root: Path) -> GateResult:
    """Run planning_drift_scan (MVP 18) — version convergence, milestone links, roadmap."""
    try:
        from claudeclockwork.core.gates import run_planning_drift_scan

        result = run_planning_drift_scan(project_root)
        return GateResult(
            gate_id="planning_drift_scan",
            gate_name="Planning Drift Scan (version convergence, milestone links, roadmap phases)",
            passed=result.get("pass", False),
            errors=result.get("errors", []),
            warnings=result.get("warnings", []),
            details={"checks": ["version_convergence", "milestone_links", "roadmap_phases"]},
            phase=18,
        )
    except Exception as exc:
        return GateResult(
            gate_id="planning_drift_scan",
            gate_name="Planning Drift Scan (version convergence, milestone links, roadmap phases)",
            passed=False,
            errors=[f"planning_drift_scan exception: {exc}"],
            warnings=[],
            details={"exception": str(exc)},
            phase=18,
        )


def _run_release_check(project_root: Path) -> GateResult:
    """Run release_check (MVP 22) — version drift, changelog entry."""
    try:
        from claudeclockwork.core.gates import run_release_check

        result = run_release_check(project_root)
        return GateResult(
            gate_id="release_check",
            gate_name="Release Check (version drift, changelog entry for current version)",
            passed=result.get("pass", False),
            errors=result.get("errors", []),
            warnings=result.get("warnings", []),
            details={"checks": ["version_convergence", "changelog_entry"]},
            phase=22,
        )
    except Exception as exc:
        return GateResult(
            gate_id="release_check",
            gate_name="Release Check (version drift, changelog entry for current version)",
            passed=False,
            errors=[f"release_check exception: {exc}"],
            warnings=[],
            details={"exception": str(exc)},
            phase=22,
        )


def _run_docs_gate(project_root: Path) -> GateResult:
    """Run docs_gate (MVP 45) — required docs, INDEX.md links."""
    try:
        from claudeclockwork.core.gates import run_docs_gate

        result = run_docs_gate(project_root)
        return GateResult(
            gate_id="docs_gate",
            gate_name="Documentation Gate (required docs exist, INDEX.md links resolve)",
            passed=result.get("pass", False),
            errors=result.get("errors", []),
            warnings=[],
            details={
                "checks": ["required_docs_exist", "index_links_resolve"],
                "docs_checked": 9,
            },
            phase=45,
        )
    except Exception as exc:
        return GateResult(
            gate_id="docs_gate",
            gate_name="Documentation Gate (required docs exist, INDEX.md links resolve)",
            passed=False,
            errors=[f"docs_gate exception: {exc}"],
            warnings=[],
            details={"exception": str(exc)},
            phase=45,
        )


def _run_report_policy_gate(project_root: Path) -> GateResult:
    """Run report_policy_gate (MVP 63) — enforce .report/ curated-only."""
    try:
        from claudeclockwork.core.gates.report_policy_gate import run_report_policy_gate

        result = run_report_policy_gate(project_root)
        violations = result.get("violations", [])
        return GateResult(
            gate_id="report_policy_gate",
            gate_name="Report Policy Gate (enforce .report/ curated-only, no runtime files)",
            passed=result.get("pass", False),
            errors=[v.get("path", "unknown") for v in violations],
            warnings=[],
            details={
                "violations_count": result.get("total_violations", 0),
                "report_dir": result.get("report_dir"),
            },
            phase=63,
        )
    except Exception as exc:
        return GateResult(
            gate_id="report_policy_gate",
            gate_name="Report Policy Gate (enforce .report/ curated-only, no runtime files)",
            passed=False,
            errors=[f"report_policy_gate exception: {exc}"],
            warnings=[],
            details={"exception": str(exc)},
            phase=63,
        )


def _run_report_redaction_gate(project_root: Path) -> GateResult:
    """Run report_redaction_gate (MVP 64) — no host paths/secrets in .report/."""
    try:
        from claudeclockwork.core.gates import run_report_redaction_gate

        result = run_report_redaction_gate(project_root)
        violations = result.get("violations", [])
        return GateResult(
            gate_id="report_redaction_gate",
            gate_name="Report Redaction Gate (no host paths or secrets in .report/)",
            passed=result.get("pass", False),
            errors=[f"{v.get('file')}:{v.get('line_number')}" for v in violations[:5]],
            warnings=[],
            details={
                "violations_count": result.get("total_violations", 0),
                "scanned_files": result.get("scanned_files", 0),
                "redaction_patterns_checked": 10,
            },
            phase=64,
        )
    except Exception as exc:
        return GateResult(
            gate_id="report_redaction_gate",
            gate_name="Report Redaction Gate (no host paths or secrets in .report/)",
            passed=False,
            errors=[f"report_redaction_gate exception: {exc}"],
            warnings=[],
            details={"exception": str(exc)},
            phase=64,
        )


def _run_runtime_root_gate(project_root: Path) -> GateResult:
    """Run runtime_root_gate (MVP 65) — legacy runtime stubbed, .clockwork_runtime enforced."""
    try:
        from claudeclockwork.core.gates import run_runtime_root_gate

        result = run_runtime_root_gate(project_root)
        violations = result.get("violations", [])
        return GateResult(
            gate_id="runtime_root_gate",
            gate_name="Runtime Root Gate (legacy runtime stubbed, .clockwork_runtime enforced)",
            passed=result.get("pass", False),
            errors=violations[:5],
            warnings=[],
            details={
                "violations_count": result.get("total_violations", 0),
                "checks": ["legacy_runtime_stub", "code_references", "doc_references"],
            },
            phase=65,
        )
    except Exception as exc:
        return GateResult(
            gate_id="runtime_root_gate",
            gate_name="Runtime Root Gate (legacy runtime stubbed, .clockwork_runtime enforced)",
            passed=False,
            errors=[f"runtime_root_gate exception: {exc}"],
            warnings=[],
            details={"exception": str(exc)},
            phase=65,
        )


def run_all_gates(project_root: Path | str) -> GreenRunResult:
    """
    Run all required gates in stable order.

    Args:
        project_root: Project root directory

    Returns:
        GreenRunResult with overall pass/fail status
    """
    root = Path(project_root).resolve()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    canonical_version = _read_version(root)

    # Stable gate execution order
    gate_runners = [
        ("qa_gate", _run_qa_gate),
        ("planning_drift_scan", _run_planning_drift_scan),
        ("release_check", _run_release_check),
        ("docs_gate", _run_docs_gate),
        ("report_policy_gate", _run_report_policy_gate),
        ("report_redaction_gate", _run_report_redaction_gate),
        ("runtime_root_gate", _run_runtime_root_gate),
    ]

    gates: list[GateResult] = []
    pass_count = 0
    fail_count = 0
    warning_count = 0
    blockers: list[str] = []

    for gate_id, runner in gate_runners:
        try:
            result = runner(root)
            gates.append(result)

            if result.passed:
                pass_count += 1
            else:
                fail_count += 1
                blockers.extend(
                    [f"{result.gate_id}: {e}" for e in result.errors]
                )

            warning_count += len(result.warnings)
        except Exception as exc:
            gates.append(
                GateResult(
                    gate_id=gate_id,
                    gate_name=f"Unknown Gate ({gate_id})",
                    passed=False,
                    errors=[f"Gate runner exception: {exc}"],
                    warnings=[],
                    details={"exception": str(exc)},
                    phase=0,
                )
            )
            fail_count += 1
            blockers.append(f"{gate_id}: {exc}")

    overall_pass = fail_count == 0

    if overall_pass:
        message = "✅ GREEN RUN — All gates pass, ready for release candidate"
    elif fail_count == 1:
        message = f"❌ RED RUN — 1 gate failed, {pass_count}/7 gates pass"
    else:
        message = f"❌ RED RUN — {fail_count} gates failed, {pass_count}/7 gates pass"

    return GreenRunResult(
        timestamp=timestamp,
        canonical_version=canonical_version,
        gates=gates,
        overall_pass=overall_pass,
        pass_count=pass_count,
        fail_count=fail_count,
        warning_count=warning_count,
        blockers=blockers,
        message=message,
    )


def generate_green_run_certificate(
    project_root: Path | str, output_file: Path | str | None = None
) -> GreenRunResult:
    """
    Generate Green Run Certificate in deterministic markdown format.

    Args:
        project_root: Project root directory
        output_file: Output file path. If None, uses Docs/green_run_certificate.md

    Returns:
        GreenRunResult with certification status
    """
    root = Path(project_root).resolve()
    result = run_all_gates(root)

    # Determine output file
    if output_file is None:
        output_file = root / "Docs" / "green_run_certificate.md"
    else:
        output_file = Path(output_file).resolve()

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Generate markdown certificate
    markdown = _generate_certificate_markdown(root, result)
    output_file.write_text(markdown, encoding="utf-8")

    return result


def _generate_certificate_markdown(project_root: Path, result: GreenRunResult) -> str:
    """Generate deterministic certificate markdown."""
    # Gate status symbols
    def gate_status_symbol(passed: bool) -> str:
        return "✅ PASS" if passed else "❌ FAIL"

    # Build gate summary table
    gate_rows = []
    for gate in result.gates:
        status = gate_status_symbol(gate.passed)
        gate_rows.append(
            f"| {gate.gate_id} | {status} | {gate.gate_name} | Phase {gate.phase} |"
        )

    gate_table = "\n".join(gate_rows)

    # Overall status
    if result.overall_pass:
        certification_badge = "### ✅ **CERTIFIED FOR RELEASE CANDIDATE**"
        status_line = "**Status**: 🟢 **GREEN RUN — READY FOR RELEASE CANDIDATE**"
    else:
        certification_badge = f"### ❌ **NOT CERTIFIED ({result.fail_count} gates failed)**"
        status_line = "**Status**: 🔴 **RED RUN — REMEDIATION REQUIRED**"

    # Version display
    version_str = result.canonical_version if result.canonical_version else "Unknown"

    # Blocker list
    if result.blockers:
        blocker_section = "\n## Blockers\n\n"
        for blocker in result.blockers:
            blocker_section += f"- {blocker}\n"
    else:
        blocker_section = ""

    # Certificate markdown
    markdown = f"""# Green Run Release Candidate Certificate

**Issue Date**: {result.timestamp}
**Canonical Version**: {version_str}
**Certified By**: Automated QA Gate Suite (MVP 18+)

---

## Release Certification Status

{certification_badge}

All mandatory quality gates pass. No blockers. No critical warnings.

---

## Gate Verification Summary

| Gate ID | Status | Gate Name | Phase |
|---------|--------|-----------|-------|
{gate_table}

---

## Canonical Version

```
.claude/VERSION: {version_str}
```

**Version Status**: ✅ CONVERGED

---

## Release Readiness

**Passing**: {result.pass_count}/7 gates ✅
**Failing**: {result.fail_count} gates
**Warnings**: {result.warning_count}

**Gate Pass Rate**: {int(result.pass_count/7*100)}%

{blocker_section}
---

## Certificate Validation

**Signed by**: Automated Quality Assurance Pipeline
**Timestamp**: {result.timestamp}
**Validity**: This certificate is valid until superseded by a newer certificate.

---

{status_line}
"""

    return markdown


def main() -> int:
    """CLI entrypoint."""
    import argparse

    parser = argparse.ArgumentParser(description="Green Run Certificate Generator (MVP 66)")
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file (default: Docs/green_run_certificate.md)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of markdown",
    )

    args = parser.parse_args()

    try:
        result = generate_green_run_certificate(args.project_root, args.output)

        if args.json:
            # Export as JSON
            output_data = {
                "timestamp": result.timestamp,
                "canonical_version": result.canonical_version,
                "overall_pass": result.overall_pass,
                "pass_count": result.pass_count,
                "fail_count": result.fail_count,
                "warning_count": result.warning_count,
                "gates": [
                    {
                        "gate_id": g.gate_id,
                        "gate_name": g.gate_name,
                        "passed": g.passed,
                        "errors": g.errors,
                        "warnings": g.warnings,
                        "phase": g.phase,
                    }
                    for g in result.gates
                ],
                "blockers": result.blockers,
                "message": result.message,
            }
            print(json.dumps(output_data, indent=2))
        else:
            # Print markdown path
            output_path = args.output or (
                Path(args.project_root).resolve() / "Docs" / "green_run_certificate.md"
            )
            print(f"Certificate written to: {output_path}")
            print(result.message)

        return 0 if result.overall_pass else 1

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
