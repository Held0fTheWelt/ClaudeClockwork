# economics_regression

**Pack:** `unclassified`

## Purpose
Checks routing spend rules (Oodle-first, Claude tier caps) against evidence (RoutingSpec, OpsLedgerSummary, QualitySignal) when present.

## Where the code lives
- `tools/skills/skill_runner.py` (entrypoint)
- `tools/skills/*.py` (skill implementations)

## Minimal usage rule
Prefer running a skill over creating an agent discussion, especially for:
validation, scanning, hashing, and evidence collection.

## Meta roles
- Skill Scout: observes runs and proposes new deterministic skills (max 3 at a…

## Implementation
- Tool: `.claude/tools/skills/economics_regression.py`
- Skill runner: `.claude/tools/skills/skill_runner.py`
- Contracts: `.claude/contracts/`

## Typical usage
```bash
python .claude/tools/skills/skill_runner.py --in <request.json> --out <result.json>
```

## Outputs
Describe output files and write locations here.

## Constraints / Non-Goals
- Deterministic: no semantic "truth verification" of content.
- Can produce candidate lists, but cannot prove that something is obsolete.
- If LLM refinement is needed: use the appropriate playbook (Explore/Write/Critic/DecideGap).
