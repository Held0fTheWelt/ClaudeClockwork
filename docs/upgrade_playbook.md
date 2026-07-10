# Clockwork Upgrade Playbook

Short, executable steps for upgrading Clockwork versions.

## 1. Pull and read version

- Pull latest; read canonical version: `cat .claude/VERSION`.
- Check `.claude/CHANGELOG.md` for the new version section or `current-version` comment.

## 2. Align version markers

- If your repo has a root `VERSION` file, set it to the same value as `.claude/VERSION` (single source of truth is `.claude/VERSION`).
- Run: `python -c "from claudeclockwork.core.gates import run_planning_drift_scan; from pathlib import Path; print('OK' if run_planning_drift_scan(Path('.'))['pass'] else 'FAIL')"` to verify no version drift.

## 3. Runtime paths

- The canonical runtime root is `.clockwork_runtime/` (Phase 19+). The legacy `.llama_runtime/` was deprecated in Phase 65 and must not be used.
- All artifacts live under `.clockwork_runtime/` (telemetry, reports, evidence, redacted_exports).

## 4. Validation

- Boot check: `python .claude/tools/boot_check.py`.
- QA gate: `python -m claudeclockwork.cli --skill-id qa_gate --inputs '{}'` (or run via skill runner).
- Tests: `python -m pytest tests/ -v -q --tb=line`.

## 5. Redacted export (optional)

- To create a shareable evidence bundle: use the evidence export skill/tool with redaction enabled (Phase 23). Do not export unredacted bundles from CI.
