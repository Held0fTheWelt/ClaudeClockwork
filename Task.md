You are Claude running inside ClaudeClockwork.

Mission: Re-run MVP Phase 62 (Version & Drift Hard Lock) onwards in the current repo, fix version drift, and prove it is resolved with gates.

Hard rules:
- Repo-local only. Do not reference external repos.
- Do not change anything unrelated to version drift.
- Prefer minimal, deterministic edits.
- English only for project-facing artifacts.

Step 0 — Inventory (required)
1) Read `Docs/versioning.md`, `VERSION`, and `.claude/VERSION`.
2) Identify the canonical version source defined by the docs. If ambiguous, make it explicit by updating `Docs/versioning.md` (minimal edit).

Step 1 — Fix the drift (required)
Choose ONE canonical approach and implement it:

A) Canonical `.claude/VERSION`:
- Set root `VERSION` to exactly match `.claude/VERSION`, OR remove root `VERSION` if policy allows.
- If you remove root `VERSION`, update `Docs/versioning.md` and the drift gate rules accordingly.

B) Canonical `VERSION`:
- Set `.claude/VERSION` to exactly match root `VERSION`.
- Update `Docs/versioning.md` to confirm this is canonical.

Step 2 — Enforce and verify (required)
1) Run the drift gate / scan (or the closest available command) and ensure it passes.
2) Run `release_check` (or the closest available gate) and ensure it uses the canonical version.
3) If there is a `qa_gate` scope for MVP18+, run it and ensure the version-related checks are green.

Step 3 — Evidence & output (required)
Produce a short report at `Docs/phase62_version_drift_fix_report.md` containing:
- Canonical version source (file path)
- Final version value
- What changed (file list)
- Gate results (pass/fail) with exact command outputs summarized

Exit criteria:
- `VERSION` and `.claude/VERSION` are consistent per the documented policy
- Drift scan passes
- Release check passes
- Report file exists and is accurate

Step 4 - Commit to git.