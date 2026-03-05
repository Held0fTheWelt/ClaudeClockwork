# Claude Clockwork Index

## Start Here

Run the boot check to verify the Clockwork environment is intact:

```
python .claude/tools/boot_check.py
```

Expected output: one `[PASS]` / `[FAIL]` line per required path, then `Result: ALL CHECKS PASSED`.

**Version:** See `.claude/VERSION` (current: `17.7.0`).

**Output locations:**
- Runtime reports → `.report/`
- Generated artifacts / diffs → `.llama_runtime/knowledge/writes/`
- Raw telemetry → `.claude-performance/`

---

## Boot Check

| Script | Purpose |
|---|---|
| `.claude/tools/boot_check.py` | Validates required Clockwork paths and VERSION file. Exit 0 = all pass. |

---

## Entry docs (start here)
- `SYSTEM.md`
- `ARCHITECTURE.md`
- `ROADMAP.md`
- `MODEL_POLICY.md`
- `skills.md`
- `skills/registry.md` (unter `.claude/skills/`)
- `CHANGELOG.md`

## Key directories
- `agents/` — agent definitions
- `skills/` — curated skill docs + playbooks (human-readable)
- `tools/skills/` — deterministic skill implementations (Python)
- `contracts/` — schemas + examples for skill IO
- `tasks/` — implementation tasks / work packages
- `governance/`, `policies/`, `performance/` — operating rules

## Add-on packs (conceptual)
See `addons/` for concise "what's included" pack docs (DocForge/PDF, Cleaning, Last-Train, Shadow Prompts).

## Where outputs go
- `.llama_runtime/knowledge/writes/` — reports, diffs, generated artifacts
- `_archive/` — archive-first cleanup targets

## Development (ClaudeClockwork MVP list & milestones)
- **`.claude-development/`** — canonical **ClaudeClockwork** MVP list (`Clockwork_MVP_Chain.md`), milestone plans, designs, audits. ClaudeClockwork only; LlamaCode is a separate framework with its own roadmap. Add new Clockwork MVPs only to the chain (see `.claude-development/MVP_RULE.md` and `.claude/governance/mvp_development_standard.md`).

## Reports
- `.report/` — organized human-facing reports (canonical)
- `.claude-performance/` — raw telemetry + performance artifacts
