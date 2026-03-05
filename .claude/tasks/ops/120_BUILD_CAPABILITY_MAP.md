# Task: Build Capability Map

## Goal
Generate a machine-readable snapshot of the clockwork capabilities.

## Steps
1) Create request `request_capmap.json`:
```json
{
  "type": "skill_request_spec",
  "request_id": "cap-001",
  "skill_id": "capability_map_build",
  "inputs": { "claude_root": ".claude", "out": "validation_runs/capability_map.json" }
}
```
2) Run:
`python .claude/tools/skills/skill_runner.py --in request_capmap.json`

## Acceptance
- Output JSON exists and lists skills/agents/contracts
