# Feedback (Phase 31)

Router and outcome feedback: manual rating, reason codes, latency satisfaction.

## Capture

- **Schema:** `.claude/contracts/schemas/feedback_event.schema.json`
- **Writer:** `claudeclockwork.router.feedback.capture_feedback`
- Events are appended to `.clockwork_runtime/telemetry/feedback.jsonl`.

## Fields

- success/failure, quality_rating, latency_satisfaction
- reason_codes: e.g. wrong_tool, wrong_model, too_slow
- run_id, node_id, option_id for attribution

## Training

Offline trainer (Phase 31) reads feedback + telemetry and produces profile snapshots. Guardrails prevent banned capabilities from being promoted.
