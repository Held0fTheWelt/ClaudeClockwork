# Capability Policy — LocalAI (Phase 24)

LocalAI capabilities (`embed.text`, `audio.asr`) are governed by:

- **Namespace:** `localai` (skills under `.claude/skills/localai/`).
- **Allowlist:** Only capabilities listed in `.claude/config/localai_registry.yaml` may be invoked.
- **Parameter validation:** Each capability has a JSON Schema for inputs (see `claudeclockwork/localai/validation.py` and contract schemas).
- **Resource limits:** Timeouts and max input sizes enforced in `claudeclockwork/localai/runtime.py` (Phase 20; limits extended in Phase 24).
- **Audit:** Every invocation (including blocked) is logged under the runtime root (Phase 24 audit module).

Unauthorized or invalid calls return a deterministic typed error (e.g. `unknown_capability`, `invalid_params`).
