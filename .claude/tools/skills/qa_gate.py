#!/usr/bin/env python3
from __future__ import annotations

"""QA Gate skill — CCW-MVP10.

Runs deterministic, PR-blocking quality checks.
stdlib only: json, pathlib, subprocess, re, collections.

Usage (CLI):
    python3 qa_gate.py '{"skill_id":"qa_gate","inputs":{"project_root":".","write_report":false}}'

Usage (skill runner):
    run({"skill_id": "qa_gate", "inputs": {"project_root": ".", "write_report": false}}) -> dict
"""

import json
import re
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

CheckResult = namedtuple("CheckResult", ["check_id", "status", "message", "blocker"])

# ---------------------------------------------------------------------------
# Check implementations
# ---------------------------------------------------------------------------

def check_boot(project_root: Path) -> CheckResult:
    """Run boot_check.py and report pass/fail."""
    boot_script = project_root / ".claude" / "tools" / "boot_check.py"
    if not boot_script.is_file():
        return CheckResult(
            "BOOT_001", "fail",
            f"boot_check.py not found at {boot_script}", True
        )
    try:
        result = subprocess.run(
            [sys.executable, str(boot_script)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return CheckResult("BOOT_001", "pass", "boot_check passes", False)
        msg = (result.stdout + result.stderr).strip()
        return CheckResult("BOOT_001", "fail", f"boot_check failed: {msg[:200]}", True)
    except Exception as exc:
        return CheckResult("BOOT_001", "fail", f"boot_check error: {exc}", True)


def check_layout(project_root: Path) -> CheckResult:
    """Verify required dirs/files exist."""
    required = [
        ".claude/INDEX.md",
        ".claude/SYSTEM.md",
        ".claude/skills/",
        ".claude/contracts/schemas/",
        ".claude/contracts/examples/",
        ".claude/governance/",
        ".claude/agents/",
        ".claude/tools/",
        ".report/",
        "scripts/",
    ]
    missing = []
    for rel in required:
        target = project_root / rel
        if rel.endswith("/"):
            if not target.is_dir():
                missing.append(rel)
        else:
            if not target.is_file():
                missing.append(rel)
    if not missing:
        return CheckResult("LAYOUT_001", "pass", f"all {len(required)} required paths exist", False)
    return CheckResult(
        "LAYOUT_001", "fail",
        f"missing required paths: {', '.join(missing)}", True
    )


def check_schemas(project_root: Path) -> CheckResult:
    """All contracts/examples parse as valid JSON."""
    examples_dir = project_root / ".claude" / "contracts" / "examples"
    schemas_dir = project_root / ".claude" / "contracts" / "schemas"
    invalid = []
    checked = 0
    for json_file in list(examples_dir.glob("*.json")) + list(schemas_dir.glob("*.json")):
        checked += 1
        try:
            with open(json_file, "r", encoding="utf-8") as fh:
                json.load(fh)
        except Exception as exc:
            invalid.append(f"{json_file.name}: {exc}")
    if not invalid:
        return CheckResult("SCHEMA_001", "pass", f"all {checked} JSON contract files parse cleanly", False)
    return CheckResult(
        "SCHEMA_001", "fail",
        f"{len(invalid)} invalid JSON file(s): {'; '.join(invalid[:3])}", True
    )


def check_skill_coverage(project_root: Path) -> CheckResult:
    """registry.md skill count matches .py count (warn if <95%)."""
    skills_dir = project_root / ".claude" / "tools" / "skills"
    registry_file = project_root / ".claude" / "skills" / "registry.md"

    # Count .py skill files (exclude dunders, private helpers starting with _)
    py_files = [
        f for f in skills_dir.glob("*.py")
        if not f.name.startswith("_") and f.name != "__init__.py"
    ]
    py_count = len(py_files)

    if not registry_file.is_file():
        return CheckResult(
            "SKILL_001", "fail",
            f"registry.md not found at {registry_file}", True
        )

    registry_text = registry_file.read_text(encoding="utf-8")
    # Count numbered skill entries like "### 27) qa_gate"
    numbered_entries = re.findall(r"^###\s+\d+\)", registry_text, re.MULTILINE)
    registry_count = len(numbered_entries)

    if py_count == 0:
        return CheckResult("SKILL_001", "warn", "no skill .py files found", False)

    coverage = registry_count / py_count if py_count > 0 else 0.0
    pct = int(coverage * 100)

    if coverage >= 0.95:
        return CheckResult(
            "SKILL_001", "pass",
            f"skill coverage {pct}% ({registry_count} registry / {py_count} py files)", False
        )
    return CheckResult(
        "SKILL_001", "warn",
        f"skill coverage {pct}% ({registry_count} registry / {py_count} py files) — below 95%", False
    )


def check_policies(project_root: Path) -> CheckResult:
    """hardlines.yaml is valid YAML (basic structural check, no PyYAML needed)."""
    hardlines = project_root / ".claude" / "policies" / "hardlines.yaml"
    if not hardlines.is_file():
        return CheckResult(
            "POLICY_001", "fail",
            f"hardlines.yaml not found at {hardlines}", True
        )
    # Basic structural validation without PyYAML: check for non-empty and no obvious BOM/encoding issues
    try:
        text = hardlines.read_text(encoding="utf-8")
    except Exception as exc:
        return CheckResult("POLICY_001", "fail", f"cannot read hardlines.yaml: {exc}", True)

    text = text.strip()
    if not text:
        return CheckResult("POLICY_001", "fail", "hardlines.yaml is empty", True)

    # Detect common YAML fatal errors: tab-as-indent at start of line is the most common.
    tab_lines = [
        i + 1 for i, line in enumerate(text.splitlines())
        if line.startswith("\t")
    ]
    if tab_lines:
        return CheckResult(
            "POLICY_001", "warn",
            f"hardlines.yaml has tab-indented lines (may be invalid YAML): lines {tab_lines[:5]}", False
        )

    return CheckResult("POLICY_001", "pass", f"hardlines.yaml present and readable ({len(text)} chars)", False)


def check_report_structure(project_root: Path) -> CheckResult:
    """`.report/` structure exists with README."""
    report_dir = project_root / ".report"
    readme = report_dir / "README.md"

    missing = []
    if not report_dir.is_dir():
        missing.append(".report/")
    if not readme.is_file():
        missing.append(".report/README.md")

    if missing:
        return CheckResult(
            "REPORT_001", "fail",
            f"missing: {', '.join(missing)}", True
        )
    return CheckResult("REPORT_001", "pass", ".report/ exists with README.md", False)


def check_pointers(project_root: Path) -> CheckResult:
    """ARCHITECTURE.md, ROADMAP.md, MODEL_POLICY.md targets exist."""
    targets = [
        ".claude/ARCHITECTURE.md",
        ".claude/ROADMAP.md",
        ".claude/MODEL_POLICY.md",
    ]
    missing = [t for t in targets if not (project_root / t).is_file()]
    if not missing:
        return CheckResult("POINTER_001", "pass", f"all {len(targets)} pointer targets exist", False)
    return CheckResult(
        "POINTER_001", "fail",
        f"missing pointer targets: {', '.join(missing)}", True
    )


def check_version(project_root: Path) -> CheckResult:
    """.claude/VERSION file exists and is semver."""
    version_file = project_root / ".claude" / "VERSION"
    if not version_file.is_file():
        # Also accept top-level VERSION
        version_file = project_root / "VERSION"
        if not version_file.is_file():
            return CheckResult(
                "VERSION_001", "fail",
                "VERSION file not found (checked .claude/VERSION and VERSION)", True
            )
    try:
        version_text = version_file.read_text(encoding="utf-8").strip()
    except Exception as exc:
        return CheckResult("VERSION_001", "fail", f"cannot read VERSION: {exc}", True)

    # Semver pattern: MAJOR.MINOR.PATCH (with optional pre-release/build metadata)
    semver_re = re.compile(
        r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$"
    )
    if semver_re.match(version_text):
        return CheckResult(
            "VERSION_001", "pass",
            f"VERSION={version_text} is valid semver (at {version_file.relative_to(project_root)})", False
        )
    return CheckResult(
        "VERSION_001", "warn",
        f"VERSION={version_text!r} does not match semver pattern", False
    )


def check_pointer_targets(project_root: Path) -> CheckResult:
    """POINTER_002: validate that paths referenced inside pointer files exist."""
    pointer_files = [
        ".claude/ARCHITECTURE.md",
        ".claude/ROADMAP.md",
        ".claude/MODEL_POLICY.md",
    ]
    # Pattern: lines containing → or 'see ' followed by a path-like token
    ref_re = re.compile(
        r"(?:→\s*|see\s+|→\s*\[)"   # prefix: arrow or 'see'
        r"([./a-zA-Z0-9_\-]+(?:\.[a-zA-Z]{1,10})?)"  # path token
    )
    missing_refs: list[str] = []
    checked_files = 0

    for rel in pointer_files:
        pf = project_root / rel
        if not pf.is_file():
            continue
        checked_files += 1
        try:
            text = pf.read_text(encoding="utf-8")
        except Exception:
            continue
        for line in text.splitlines():
            for m in ref_re.finditer(line):
                candidate = m.group(1).strip()
                # Skip obvious non-paths (short tokens, no slash or dot, URLs)
                if len(candidate) < 3 or candidate.startswith("http"):
                    continue
                if "/" not in candidate and "." not in candidate:
                    continue
                # Resolve relative to project root
                target = project_root / candidate
                if not target.exists():
                    entry = f"{rel} → {candidate}"
                    if entry not in missing_refs:
                        missing_refs.append(entry)

    if checked_files == 0:
        return CheckResult(
            "POINTER_002", "skip",
            "no pointer files found to check", False
        )
    if missing_refs:
        sample = ", ".join(missing_refs[:5])
        return CheckResult(
            "POINTER_002", "warn",
            f"{len(missing_refs)} pointer-file reference(s) target missing path(s): {sample}", False
        )
    return CheckResult(
        "POINTER_002", "pass",
        f"all pointer-file references resolve (checked {checked_files} pointer files)", False
    )


def check_skill_dispatch_coverage(project_root: Path) -> CheckResult:
    """COVERAGE_001: skill_runner.py dispatch coverage vs .py files in tools/skills/."""
    skills_dir = project_root / ".claude" / "tools" / "skills"
    runner_file = skills_dir / "skill_runner.py"
    registry_file = project_root / ".claude" / "skills" / "registry.md"

    if not runner_file.is_file():
        return CheckResult(
            "COVERAGE_001", "fail",
            f"skill_runner.py not found at {runner_file}", True
        )

    # Extract SKILLS dict keys from skill_runner.py
    runner_text = runner_file.read_text(encoding="utf-8")
    skills_keys = set(re.findall(r'^\s+"([a-zA-Z0-9_]+)"\s*:', runner_text, re.MULTILINE))

    # Count .py skill files (exclude __init__.py, skill_runner.py, _*.py)
    py_files = [
        f for f in skills_dir.glob("*.py")
        if not f.name.startswith("_")
        and f.name not in ("__init__.py", "skill_runner.py")
    ]
    py_count = len(py_files)

    if py_count == 0:
        return CheckResult("COVERAGE_001", "warn", "no skill .py files found", False)

    coverage = len(skills_keys) / py_count
    pct = int(coverage * 100)

    # Strict check: skills in registry.md marked as "not stub" must have dispatch entry
    strict_fails: list[str] = []
    if registry_file.is_file():
        registry_text = registry_file.read_text(encoding="utf-8")
        # Find skill names from numbered entries: "### N) skill_name"
        registry_names = re.findall(r"^###\s+\d+\)\s+(\S+)", registry_text, re.MULTILINE)
        for name in registry_names:
            # Determine if it is a stub: look for ghost-skill marker near that entry
            # We search a small window around the entry for 'ghost-skill' or 'stub'
            idx = registry_text.find(f") {name}")
            if idx == -1:
                continue
            window = registry_text[idx: idx + 400]
            is_stub = bool(re.search(r"ghost.skill|stub", window, re.IGNORECASE))
            if not is_stub and name not in skills_keys:
                strict_fails.append(name)

    if strict_fails:
        return CheckResult(
            "COVERAGE_001", "fail",
            f"non-stub skill(s) in registry.md have no dispatch entry in skill_runner.py: "
            f"{', '.join(strict_fails[:10])}", True
        )

    if coverage < 0.90:
        return CheckResult(
            "COVERAGE_001", "warn",
            f"skill dispatch coverage {pct}% ({len(skills_keys)} dispatched / {py_count} .py files) — below 90%", False
        )
    return CheckResult(
        "COVERAGE_001", "pass",
        f"skill dispatch coverage {pct}% ({len(skills_keys)} dispatched / {py_count} .py files)", False
    )


def check_addon_completeness(project_root: Path) -> CheckResult:
    """ADDON_001: every skill listed in addons/map.yaml has a .py implementation."""
    map_file = project_root / ".claude" / "addons" / "map.yaml"
    skills_dir = project_root / ".claude" / "tools" / "skills"

    if not map_file.is_file():
        return CheckResult(
            "ADDON_001", "warn",
            f"addons/map.yaml not found at {map_file} — skipping addon completeness check", False
        )

    try:
        raw = map_file.read_text(encoding="utf-8")
    except Exception as exc:
        return CheckResult("ADDON_001", "fail", f"cannot read addons/map.yaml: {exc}", True)

    # map.yaml is actually JSON in this repo — try JSON first, fall back to minimal YAML parse
    addon_skills: list[str] = []
    try:
        data = json.loads(raw)
        addons_block = data.get("addons", {})
        for pack_name, skill_list in addons_block.items():
            if isinstance(skill_list, list):
                addon_skills.extend(skill_list)
    except json.JSONDecodeError:
        # Minimal YAML-line parse: extract bare string list items (lines starting with "    - ")
        for line in raw.splitlines():
            m = re.match(r"^\s+-\s+([a-zA-Z0-9_]+)\s*$", line)
            if m:
                addon_skills.append(m.group(1))

    if not addon_skills:
        return CheckResult("ADDON_001", "skip", "no addon skills found in map.yaml", False)

    missing: list[str] = []
    for skill_name in addon_skills:
        py_path = skills_dir / f"{skill_name}.py"
        if not py_path.is_file():
            missing.append(skill_name)

    if missing:
        return CheckResult(
            "ADDON_001", "fail",
            f"{len(missing)} addon skill(s) have no .py implementation: {', '.join(missing)}", True
        )
    return CheckResult(
        "ADDON_001", "pass",
        f"all {len(addon_skills)} addon skill(s) have .py implementations", False
    )


def check_agent_registry_consistency(project_root: Path) -> CheckResult:
    """AGENT_001: ratio of .md agent files to registry.json entries is not extreme."""
    agents_dir = project_root / ".claude" / "agents"
    registry_file = project_root / ".claude" / "agents" / "registry.json"

    if not registry_file.is_file():
        return CheckResult(
            "AGENT_001", "skip",
            ".claude/agents/registry.json not found — skipping agent registry consistency check", False
        )

    # Count .md files recursively under .claude/agents/
    md_count = len(list(agents_dir.rglob("*.md"))) if agents_dir.is_dir() else 0

    try:
        data = json.loads(registry_file.read_text(encoding="utf-8"))
    except Exception as exc:
        return CheckResult("AGENT_001", "warn", f"cannot parse registry.json: {exc}", False)

    if isinstance(data, list):
        registry_count = len(data)
    elif isinstance(data, dict):
        # agents array inside a wrapper object
        registry_count = len(data.get("agents", data))
    else:
        registry_count = 0

    if registry_count == 0:
        return CheckResult(
            "AGENT_001", "warn",
            f"registry.json has 0 agent entries (methodology has {md_count} .md files)", False
        )

    ratio = md_count / registry_count
    if ratio > 5:
        return CheckResult(
            "AGENT_001", "warn",
            f"agent methodology far ahead of implementation: "
            f"{md_count} .md files vs {registry_count} registry entries (ratio {ratio:.1f}:1 > 5:1)", False
        )
    return CheckResult(
        "AGENT_001", "pass",
        f"agent registry ratio ok: {md_count} .md files / {registry_count} registry entries "
        f"(ratio {ratio:.1f}:1)", False
    )


# ---------------------------------------------------------------------------
# Check registry
# ---------------------------------------------------------------------------

CHECKS = [
    ("BOOT_001",    "boot_check passes",                                           check_boot),
    ("LAYOUT_001",  "required dirs exist",                                         check_layout),
    ("SCHEMA_001",  "all contracts/examples parse as valid JSON",                  check_schemas),
    ("SKILL_001",   "registry.md skill count matches .py count (warn if <95%)",    check_skill_coverage),
    ("POLICY_001",  "hardlines.yaml is valid YAML",                                check_policies),
    ("REPORT_001",  ".report/ structure exists with README",                       check_report_structure),
    ("POINTER_001", "ARCHITECTURE.md, ROADMAP.md, MODEL_POLICY.md targets exist",  check_pointers),
    ("VERSION_001", ".claude/VERSION file exists and is semver",                   check_version),
    ("POINTER_002", "pointer-file referenced paths exist in project",              check_pointer_targets),
    ("COVERAGE_001","skill_runner.py dispatch coverage vs .py files",              check_skill_dispatch_coverage),
    ("ADDON_001",   "addon pack skills have .py implementations",                  check_addon_completeness),
    ("AGENT_001",   "agent registry not far behind methodology .md count",         check_agent_registry_consistency),
]

ALL_CHECK_IDS = [c[0] for c in CHECKS]

# ---------------------------------------------------------------------------
# Skill entry point
# ---------------------------------------------------------------------------

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    project_root = Path(inputs.get("project_root", ".")).resolve()
    requested_ids = inputs.get("checks", ALL_CHECK_IDS)
    output_dir = inputs.get("output_dir", ".report/qa/")
    write_report = bool(inputs.get("write_report", False))

    # Filter to requested checks
    checks_to_run = [c for c in CHECKS if c[0] in requested_ids]

    results = []
    blockers = []
    warnings_list = []
    pass_count = 0
    warn_count = 0
    fail_count = 0

    for check_id, description, fn in checks_to_run:
        try:
            result = fn(project_root)
        except Exception as exc:
            result = CheckResult(check_id, "fail", f"check raised exception: {exc}", True)

        results.append({
            "check_id": result.check_id,
            "status": result.status,
            "message": result.message,
            "blocker": result.blocker,
        })
        if result.status == "pass":
            pass_count += 1
        elif result.status == "warn":
            warn_count += 1
            warnings_list.append(f"{result.check_id}: {result.message}")
        elif result.status == "fail":
            fail_count += 1
            if result.blocker:
                blockers.append(f"{result.check_id}: {result.message}")

    gate_pass = (fail_count == 0)
    checks_run = len(results)
    pass_rate = round(pass_count / checks_run, 3) if checks_run > 0 else 0.0

    if fail_count > 0:
        overall_status = "fail"
    elif warn_count > 0:
        overall_status = "partial"
    else:
        overall_status = "ok"

    outputs = {
        "results": results,
        "blockers": blockers,
        "warnings": warnings_list,
        "pass_count": pass_count,
        "warn_count": warn_count,
        "fail_count": fail_count,
        "gate_pass": gate_pass,
    }

    skill_result = {
        "type": "skill_result_spec",
        "skill_id": req.get("skill_id", "qa_gate"),
        "status": overall_status,
        "outputs": outputs,
        "errors": blockers[:],
        "warnings": warnings_list[:],
        "metrics": {"checks_run": checks_run, "pass_rate": pass_rate},
    }

    if write_report:
        _write_report(project_root, output_dir, skill_result)

    return skill_result


def _write_report(project_root: Path, output_dir: str, result: dict) -> None:
    """Write JSON report to output_dir."""
    import datetime

    out_path = project_root / output_dir
    out_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    report_file = out_path / f"qa_gate_{timestamp}.json"
    with open(report_file, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        req_in = {"skill_id": "qa_gate", "inputs": {"project_root": ".", "write_report": False}}
    else:
        try:
            req_in = json.loads(sys.argv[1])
        except json.JSONDecodeError as exc:
            print(json.dumps({"error": f"invalid JSON input: {exc}"}))
            sys.exit(1)

    out = run(req_in)
    print(json.dumps(out, indent=2))
    sys.exit(0 if out.get("outputs", {}).get("gate_pass", False) else 1)
