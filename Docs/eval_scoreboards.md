# Eval Scoreboards (Phase 25)

- **Machine-readable:** `.clockwork_runtime/eval/scoreboard.json` (or custom out_dir).
- **Human summary:** `.clockwork_runtime/eval/scoreboard.md`.
- **Generation:** `claudeclockwork.eval.scoreboard.generate_scoreboard(results)`.
- Repeated runs produce consistent formatting and stable ordering (sorted by name, status).
- Optional: export redacted scoreboard summary to `.report/` for sharing.
