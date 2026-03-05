# Task: Skill Discovery (Auto)

## Goal
Find the best existing skills for an intent **before** doing work.

## Run (SkillRequestSpec)
Create `request.json`:
```json
{
  "type": "skill_request_spec",
  "request_id": "req-skill-discovery-001",
  "skill_id": "skill_registry_search",
  "inputs": { "query": "<your intent>", "max_results": 25 }
}
```

Execute:
`python .claude/tools/skills/skill_runner.py --in request.json`

## Output
- Candidate skills + suggested pipeline order
