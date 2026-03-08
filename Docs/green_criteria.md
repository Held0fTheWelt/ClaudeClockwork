# Green Run Criteria (MVP 18+)

**Phase**: MVP 66 — Re-Audit "Green Run Certificate"
**Scope**: MVP Phase 18 to Current
**Canonical Version**: `.claude/VERSION`

---

## Definition: "Green Run"

A **Green Run** is a state where the repository is certified "ready for release candidate". All required quality gates pass deterministically, and evidence is exportable in strict redacted mode.

### Certification Level
- **Level**: RC (Release Candidate)
- **Authority**: Automated QA Gate Suite
- **Validity**: Until superseded by newer certificate

---

## Required Gates (Stable Ordering)

All gates must pass (status = `pass`) with zero blockers for Green certification.

| Priority | Gate ID | Gate Function | Module | Phase | Strict Mode |
|----------|---------|---------------|--------|-------|-------------|
| 1 | `qa_gate` | Core QA checks (boot, layout, schemas, skills, policies, version) | `.claude/tools/skills/qa_gate.py` | MVP 10 | ✅ |
| 2 | `planning_drift_scan` | Version convergence, milestone links, roadmap phases | `claudeclockwork.core.gates.planning_drift` | MVP 18 | ✅ |
| 3 | `release_check` | Version drift, changelog entry for current version | `claudeclockwork.core.gates.release_check` | MVP 22 | ✅ |
| 4 | `docs_gate` | Required docs exist, INDEX.md links resolve | `claudeclockwork.core.gates.docs_gate` | MVP 45 | ✅ |
| 5 | `report_policy_gate` | Enforce `.report/` curated-only (no runtime JSON/PNG) | `claudeclockwork.core.gates.report_policy_gate` | MVP 63 | ✅ |
| 6 | `report_redaction_gate` | No host paths or secrets in `.report/` markdown | `claudeclockwork.core.gates.report_redaction_gate` | MVP 64 | ✅ |
| 7 | `runtime_root_gate` | `.llama_runtime` stubbed, `.clockwork_runtime` enforced | `claudeclockwork.core.gates.runtime_root_gate` | MVP 65 | ✅ |
| 8 | `perf_artifact_gate` | No runtime outputs under `.claude-performance/` (curated-only) | `claudeclockwork.core.gates.perf_artifact_gate` | MVP 69 | ✅ |
| 9 | `doc_path_leak_gate` | No absolute host paths in curated docs (Docs/, mvps/, .claude/) | `claudeclockwork.core.gates.doc_path_leak_gate` | MVP 70 | ✅ |

---

## Gate Pass Criteria (per gate)

### Gate 1: `qa_gate`
- **Inputs**: `project_root`, `checks=ALL_CHECK_IDS`, `write_report=False`
- **Pass Condition**: All 14 checks pass (BOOT_001, LAYOUT_001, ..., RELEASE_001)
- **Blocker Definition**: `fail_count == 0`
- **Evidence**: Skill result dict with `gate_pass=true`

### Gate 2: `planning_drift_scan`
- **Inputs**: `project_root`
- **Pass Condition**: `pass=true`, `errors=[]`
- **Checks**:
  - Version convergence (`.claude/VERSION` vs `VERSION`)
  - Milestone index links resolve (`.claude-development/milestones/index.md`)
  - Roadmap phases exist (mvps/MVP_Phase*.md referenced in roadmaps/)
- **Blocker Definition**: Any error in `errors` list

### Gate 3: `release_check`
- **Inputs**: `project_root`
- **Pass Condition**: `pass=true`, `errors=[]`
- **Checks**:
  - Version drift (delegated to planning_drift_scan)
  - Changelog mentions canonical version (`.claude/CHANGELOG.md`)
- **Blocker Definition**: Any error

### Gate 4: `docs_gate`
- **Inputs**: `project_root`
- **Pass Condition**: `pass=true`, `errors=[]`
- **Checks**:
  - 9 required docs exist (Docs/INDEX.md, Docs/troubleshooting.md, etc.)
  - All internal links in INDEX.md resolve
- **Blocker Definition**: Missing docs or broken links

### Gate 5: `report_policy_gate`
- **Inputs**: `project_root`
- **Pass Condition**: `pass=true`, `violations=[]`
- **Checks**:
  - No runtime-generated files in `.report/` (*.json, *.png, *.csv)
  - No timestamp-marked markdown in `.report/`
  - Only curated markdown (Report_*.md) allowed
- **Blocker Definition**: Any violation in `violations` list

### Gate 6: `report_redaction_gate`
- **Inputs**: `project_root`
- **Pass Condition**: `pass=true`, `violations=[]`
- **Scans**: `.report/**/*.md`
- **Redaction Rules**:
  - Windows drive paths (`<DRIVE>:\`, e.g. <DRIVE>:\, <DRIVE>:\)
  - Unix home paths (/Users/, /home/)
  - WSL mount paths (/mnt/[a-z]/)
  - System absolute paths (/opt/, /srv/, /var/, /workspace/, /work/, /project/, /app/)
  - Secret patterns (api_key=, token=, password=, credentials=, Bearer token)
- **Blocker Definition**: Any violation

### Gate 7: `runtime_root_gate`
- **Inputs**: `project_root`
- **Pass Condition**: `pass=true`, `violations=[]`
- **Checks**:
  - `.llama_runtime/` is stubbed (only README.md + .gitkeep)
  - `.llama_runtime/` README.md contains "DEPRECATED"
  - No code references `.llama_runtime` in active code (claudeclockwork/, tests/)
  - No doc references `.llama_runtime` in `.project/Docs/` (except deprecation notes)
- **Blocker Definition**: Any violation

### Gate 8: `perf_artifact_gate`
- **Inputs**: `project_root`
- **Pass Condition**: `pass=true`, `errors=[]`
- **Checks**:
  - No `reports/` or `events/` subdirectories under `.claude-performance/`
  - No machine-generated filenames (run-*, timestamped, _report_, performance_toggle)
- **Blocker Definition**: Any error
- **Drift Register**: DR-003

### Gate 9: `doc_path_leak_gate`
- **Inputs**: `project_root`
- **Pass Condition**: `pass=true`, `errors=[]`
- **Scans**: `Docs/`, `.project/Docs/`, `.claude/governance/`, `.claude/agents/`, `mvps/`
- **Checks**:
  - No Windows drive paths (`C:\`, `D:\`, etc.)
  - No Unix home paths (`/home/<user>/`, `/Users/<user>/`)
  - No WSL mount paths (`/mnt/<drive>/<path>`)
- **Blocker Definition**: Any error
- **Drift Register**: DR-004

---

## Certificate Output Format

Certificate is generated as deterministic markdown (`Docs/green_run_certificate.md`):

```markdown
# Green Run Release Candidate Certificate

**Issue Date**: [ISO 8601 timestamp]
**Canonical Version**: [.claude/VERSION content]
**Certified By**: Automated QA Gate Suite (MVP 18+)

## Gate Verification Summary
[table of gate results]

## Canonical Version
[version convergence status]

## Release Readiness
**Passing**: N/9 gates
**Failing**: 0 gates
**Pass Rate**: 100%

## Status: 🟢 GREEN RUN — READY FOR RELEASE CANDIDATE
```

---

## Evidence Bundle

When run in strict redacted mode (via Phase 65 export pipeline):

1. **Gate Results**: JSON artifacts from each gate execution
2. **Version Proof**: `.claude/VERSION` + `.claude/CHANGELOG.md` head
3. **Coverage Metrics**: Skill count, dispatch coverage, schema count
4. **Redaction Verification**: Scan results from redaction_gate
5. **Export Manifest**: `.clockwork_runtime/exports/green_run_manifest.json`

All evidence paths must be absolute and redacted of host paths.

---

## Determinism Contract

### Reproducibility Requirements

1. **Version-locked**: Canonical version from `.claude/VERSION` recorded exactly
2. **Timestamp-only variance**: ISO 8601 issue date is only non-deterministic element
3. **Stable ordering**: Gate execution order is always: qa_gate → planning_drift → release_check → docs_gate → report_policy_gate → report_redaction_gate → runtime_root_gate → perf_artifact_gate → doc_path_leak_gate
4. **No side effects**: Gate functions read-only; no state modification
5. **Re-runnable**: Same inputs → identical results (except timestamp)

### Verification

Run certificate generator twice in same session:

```bash
python3 claudeclockwork/qa/reports/green_run.py /path/to/project
python3 claudeclockwork/qa/reports/green_run.py /path/to/project
```

**Expected**: Both certificates identical except `Issue Date` field.

---

## Escalation

### Automatic Passes (Level 0)
- All 9 gates pass: Write certificate, export evidence bundle

### Partial Pass (Level 1)
- 8/9 gates pass: Warn, write certificate as "CONDITIONAL RC", escalate to review

### Failure (Level 2)
- <8/9 gates pass: Fail, block certificate, list blockers, escalate to design review

### Critical Failure (Level 3)
- Core gate unavailable (qa_gate, planning_drift): Stop, require manual diagnostic

---

## Gate Functions Module Map

| Gate | Callable | Signature | Return Type |
|------|----------|-----------|------------|
| qa_gate | `run(req: dict) -> dict` | inputs: {project_root, checks, write_report} | skill_result_spec |
| planning_drift_scan | `run_planning_drift_scan(project_root: Path\|str) -> dict` | returns {pass, errors, warnings} | dict |
| release_check | `run_release_check(project_root: Path\|str) -> dict` | returns {pass, errors, warnings} | dict |
| docs_gate | `run_docs_gate(project_root: Path\|str\|None) -> dict` | returns {pass, errors} | dict |
| report_policy_gate | `run_report_policy_gate(project_root: Path\|str\|None) -> dict` | returns {pass, violations, report_dir} | dict |
| report_redaction_gate | `run_report_redaction_gate(project_root: Path\|str\|None) -> dict` | returns {pass, violations, scanned_files, report_dir} | dict |
| runtime_root_gate | `run_runtime_root_gate(project_root: Path\|str\|None) -> dict` | returns {pass, violations, message} | dict |
| perf_artifact_gate | `run_perf_artifact_gate(project_root: Path\|str) -> dict` | returns {pass, errors, warnings} | dict |
| doc_path_leak_gate | `run_doc_path_leak_gate(project_root: Path\|str) -> dict` | returns {pass, errors, warnings} | dict |

---

## Related Documentation

- `.claude/CHANGELOG.md` — Version history and release notes
- `.claude/governance/qa_gate_policy.md` — QA gate policy details
- `Docs/report_vs_runtime_policy.md` — `.report/` vs `.clockwork_runtime/` separation
- `Docs/green_run_certificate.md` — Generated certificate (auto-updated)
- `Docs/quality_reaudit_from_mvp18.md` — Historical audit trail
- `Docs/drift_register.md` — Recurring drift types, gates, and remediation (Phase 71)

---

**Last Updated**: 2026-03-08
**Status**: Active (Green Run Criteria Approved)
