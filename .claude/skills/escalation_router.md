# Skill: escalation_router

**Purpose:** Route requests through the cheapest model first; escalate to the
next rung automatically when the current model is overloaded, times out, or
returns an empty response.

## Input

| Field        | Type            | Required | Description                                |
|--------------|-----------------|----------|--------------------------------------------|
| ladder_name  | str             | yes      | `"haiku"` or `"sonnet"`                    |
| messages     | list[dict]      | yes      | Anthropic-format message list              |
| max_tokens   | int             | no       | Override per-rung max_tokens               |
| config_path  | str             | no       | Path to `model_escalation_ladder.yaml`     |

## Output

| Field              | Type        | Description                                   |
|--------------------|-------------|-----------------------------------------------|
| model_used         | str         | model_id that produced the response           |
| rung               | int         | rung index that succeeded (0 = cheapest)      |
| content            | str         | response text                                 |
| escalated          | bool        | True if at least one escalation occurred      |
| escalation_reason  | str \| None | Reason for last escalation, or None           |

## Implementation Note

The active skill implementation is the legacy wrapper:
  `.claude/tools/skills/escalation_router.py`

A native `claudeclockwork` implementation is planned for Phase 3 (Native Core Services).
The legacy wrapper does not import from `llamacode` — that dependency was removed in Phase 8 (H8.2).

## Escalation triggers

| Trigger        | Enabled by default | Condition                                    |
|----------------|--------------------|----------------------------------------------|
| overloaded     | yes                | HTTP 429 / 529 / 503 / 500 or error text     |
| timeout        | yes                | Response exceeds rung `timeout_seconds`      |
| empty_response | yes                | Response shorter than `min_response_length`  |
| poor_quality   | no                 | Output score below threshold (needs scorer)  |

Config: `.claude/config/model_escalation_ladder.yaml`
Demo: `python3 .claude/tools/skills/escalation_router.py '{"skill_id":"escalation_router","inputs":{"ladder":"haiku","messages":[{"role":"user","content":"hello"}],"dry_run":true}}'`

## Clockwork Skill Files
- Schema: `.claude/contracts/schemas/escalation_router.schema.json`
- Example: `.claude/contracts/examples/escalation_router_example.json`
- Implementation: `.claude/tools/skills/escalation_router.py`

## Quick test
```bash
python3 .claude/tools/skills/escalation_router.py '{"skill_id":"escalation_router","inputs":{"ladder":"haiku","messages":[{"role":"user","content":"hello"}],"dry_run":true}}'
```
