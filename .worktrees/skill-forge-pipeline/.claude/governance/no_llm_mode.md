# No-LLM Mode (Tool-only)

This mode is for **bulk health checks** and **validation campaigns** where you want near-zero token spend.

## Rules
- Only deterministic tools/skills are allowed.
- Claude is allowed only as a relay (C0) if you explicitly request a summary.
- No planning/ideation steps that require LLMs.

## Typical uses
- QA campaigns
- Schema/example drift checks
- Determinism proofs
- Repo consistency validation
- Economics regression checks

## Enable/Disable
Set in `.claude/settings.local.json`:
- `modes.no_llm = true/false`
