# Drift Register — ClaudeClockwork

**Phase 71.** This register documents every recurring drift type observed in the repository,
its root cause, disposition (forbidden vs allowed-with-constraints), the gate that enforces
the decision, and the remediation procedure.

**Rule (Phase 71 — Explain or Eliminate):**
Any drift that recurs must be either eliminated or documented here with a gate.
Future PRs that reintroduce a listed drift type must include either:
- removal of the drift source, OR
- an explicit update to this register with documented rationale + gate.

---

## DR-001 — VERSION vs `.claude/VERSION` Mismatch

| Field | Value |
|-------|-------|
| **Symptom** | Root `VERSION` file differs from `.claude/VERSION` |
| **Root Cause** | `.claude/VERSION` is auto-incremented on each agent invocation. Root `VERSION` must be manually synced. NTFS/WSL2 file visibility issues can also cause `.claude/VERSION` to disappear from the filesystem while remaining git-tracked. |
| **Decision** | FORBIDDEN — both files must match at commit time |
| **Gate** | `planning_drift_scan` (DRIFT_001) — `claudeclockwork/core/gates/planning_drift.py` |
| **Remediation** | `python3 scripts/sync_version.py` then re-run `python3 -m pytest tests/test_gates.py::test_planning_drift_scan_clean_repo` |
| **Auto-Sync** | `scripts/sync_version.py` (Phase 72) — run before each commit to keep root `VERSION` in sync with `.claude/VERSION` SSOT |
| **Phases** | 62 (introduced gate), 62-re-run (fixed NTFS issue), 72 (sync utility added, DR-001 kill) |

---

## DR-002 — `.report/` Runtime Pollution

| Field | Value |
|-------|-------|
| **Symptom** | Machine-generated JSON, JSONL, PNG, or timestamped files appear in `.report/` |
| **Root Cause** | `_report_publish.py`, `model_routing_select.py`, and `model_routing_record_outcome.py` defaulted to writing into `.report/performance/` and `.report/routing/`. Phase 63 migration moved existing files but did not update write paths. |
| **Decision** | FORBIDDEN — `.report/` is curated-only (human-facing summaries only) |
| **Gate** | `report_policy_gate` — `claudeclockwork/core/gates/report_policy_gate.py` |
| **Remediation** | Delete runtime files from `.report/`; fix write paths to use `.clockwork_runtime/reports/<category>/` |
| **Phases** | 63 (gate added), 66 (source fixed) |

---

## DR-003 — `.claude-performance/` Runtime Pollution

| Field | Value |
|-------|-------|
| **Symptom** | `reports/` or `events/` subdirectories under `.claude-performance/` contain machine-generated budget reports, event logs, or timestamped output files |
| **Root Cause** | `budget_analyze.py`, `performance_finalize.py`, and `performance_toggle.py` default to `.claude-performance/reports/`. These were committed to git, polluting the curated space. |
| **Decision** | FORBIDDEN — `.claude-performance/` is curated-only; runtime outputs are gitignored |
| **Gate** | `perf_artifact_gate` — `claudeclockwork/core/gates/perf_artifact_gate.py` |
| **Remediation** | Delete `.claude-performance/reports/` and `.claude-performance/events/` from disk; they are gitignored and will not be recommitted |
| **Phases** | 69 (gate added, gitignore updated, 3,669 files removed) |

---

## DR-004 — Absolute Host Paths in Curated Docs

| Field | Value |
|-------|-------|
| **Symptom** | Windows drive paths (`<DRIVE>:\...`), Unix home paths (`/home/<username>/`, `/Users/<username>/`), or WSL mounts (`/mnt/<drive>/...`) appear in curated markdown outside runtime roots |
| **Root Cause** | Example paths in documentation used real machine paths instead of placeholders. Phase 64 redaction gate covered `.report/` but not broader curated docs (Docs/, mvps/, governance/, agents/). |
| **Decision** | FORBIDDEN — all examples must use placeholders (`<PROJECT_ROOT>`, `<DRIVE>`, `<username>`, `<ABS_PATH>`) |
| **Gate** | `doc_path_leak_gate` — `claudeclockwork/core/gates/doc_path_leak_gate.py` |
| **Remediation** | Replace concrete paths with placeholders in the affected file; re-run gate |
| **Phases** | 64 (`.report/` scope), 70 (curated docs scope extended) |

---

## DR-005 — Governance/Agent Docs with Placeholder Links

| Field | Value |
|-------|-------|
| **Symptom** | `docs_link_lint` reports broken links in `.claude/governance/` or `.claude/agents/` docs (e.g. `../path/to/canonical.md`, `agents/`, `ollama_client/claude_client`) |
| **Root Cause** | Template examples using markdown link syntax inside code blocks are parsed as real links by the link-lint tool. Arrow (`→`) references in spawn-prompt templates were also caught. |
| **Decision** | FORBIDDEN for real broken links; ALLOWED for examples if formatted without link syntax |
| **Gate** | `docs_link_lint` (full scope) — `.claude/tools/skills/docs_link_lint.py` |
| **Remediation** | Replace `[text](../placeholder.md)` with backtick-escaped text; replace `→` arrows in code examples with `->` |
| **Phases** | 68 |

---

## Summary Table

| ID | Drift Type | Decision | Gate |
|----|-----------|----------|------|
| DR-001 | VERSION mismatch | FORBIDDEN | `planning_drift_scan` |
| DR-002 | `.report/` runtime pollution | FORBIDDEN | `report_policy_gate` |
| DR-003 | `.claude-performance/` pollution | FORBIDDEN | `perf_artifact_gate` |
| DR-004 | Host paths in curated docs | FORBIDDEN | `doc_path_leak_gate` |
| DR-005 | Governance doc broken links | FORBIDDEN | `docs_link_lint` |

All five drifts are **forbidden** — no allowed-with-constraints exceptions.
Every gate is deterministic and must pass before release.
