# evidence_bundle_build

**Pack:** `unclassified`

## Purpose
Builds an evidence bundle:
- `artifacts/evidence_bundle_manifest.json`
- `artifacts/evidence_bundle.zip`

## Implementation
- Tool: `.claude/tools/skills/evidence_bundle_build.py`
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
