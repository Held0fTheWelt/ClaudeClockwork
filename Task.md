You are Claude running inside ClaudeClockwork.

Mission:
Run the repo from MVP Phase 72 onward (72 → 73 → 74 → 75). Fix all drift issues and prove each phase is complete by running the required gates. After each phase, create a git commit with a clear message and a short summary of evidence.

Hard rules:
- English only for all project-facing artifacts (docs, rules, prompts, code comments).
- Repo-local only. Do not reference external repos or paths.
- Deterministic changes only (stable ordering, seeded where needed, no timestamps in committed artifacts unless explicitly required).
- Never proceed to the next phase unless the current phase is fully green.
- After each phase, run the gate suite for scope MVP18+ (or the closest available “green suite”), and ensure it is green.
- Commit after each completed phase. Do not bundle multiple phases into one commit.

Before you start:
- Confirm you are in the correct repo root.
- Ensure you can run git commands locally (status, diff, commit).
- Do not commit runtime artifacts. Only commit curated docs/code/config.

Global execution loop (repeat per phase):
1) Read the MVP document for the phase (mvps/MVP_PhaseXX_*.md).
2) Implement exactly what it requires (minimal changes).
3) Run the required gates:
   - qa_gate (MVP18+ scope, if supported)
   - planning_drift_scan
   - release_check
   - docs link-lint
   - report policy gate
   - report redaction / doc path leak gate
   - runtime root gate
   - any new phase-specific gate (e.g., validation_artifact_gate, doc_policy_consistency_gate)
4) Collect evidence:
   - Save gate outputs (as short summaries) into `Docs/phaseXX_completion_report.md`
   - Update `Docs/drift_register.md` when the phase requires it
5) Git commit:
   - `git status` must show only intended changes
   - Commit message format:
     - "Phase XX: <short title>"
   - Commit body must include:
     - key files changed
     - gates run + pass summary
6) Only then continue to the next phase.

Phase 72 — Version Sync Automation
- Enforce SSOT for versioning (recommended: `.claude/VERSION`).
- Implement `clockwork version sync` (or equivalent) OR remove the mirror file cleanly.
- Tighten gates so drift cannot pass.
- Update `Docs/versioning.md` and `Docs/drift_register.md` accordingly.
- Verify: `VERSION` and `.claude/VERSION` cannot drift without gates failing.

Phase 73 — Validation Artifacts: Placement + Redaction Fix
- Decide policy for `validation_runs/` and `validation_runs_redacted/` (runtime-only preferred).
- Remove absolute host paths from any redacted manifests (placeholders only).
- Add `validation_artifact_gate` and tests.
- Ensure the repo does not commit runtime validation artifacts unintentionally.

Phase 74 — Performance Policy Convergence
- Make `.claude-performance/README.md` fully consistent with curated-only `.report/`.
- Add `doc_policy_consistency_gate` + tests.
- Ensure no docs instruct writing runtime outputs into `.report/*`.

Phase 75 — Re-run Phase 66 (Green Run Certificate)
- Update green criteria to include Phase 72–74 gates.
- Re-run the full MVP18+ green suite.
- Export a strict redacted evidence bundle (no host paths).
- Generate `Docs/green_run_certificate.md` in a stable format.

Stop condition:
- If any gate fails, fix the cause within the current phase until all required gates pass.
- Do not advance and do not commit until the phase is fully green.