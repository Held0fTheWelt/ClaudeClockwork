# Playbook: Skill Forge Pipeline (Autodiscovery → Gap → Scaffold → Use)

This playbook turns recurring work into reusable deterministic skills.

## Core rule
Before doing non-trivial work:
1) Search existing skills (`skill_registry_search`)
2) If coverage is weak, detect a gap (`skill_gap_detect`)
3) If gap exists, scaffold a new skill (`skill_scaffold`) and run it once immediately.

## Commands
All skills run via:
`python .claude/tools/skills/skill_runner.py --in request.json`

## Steps
1) Skill discovery
- skill: `skill_registry_search`
- input: `{ "query": "<intent>" }`

2) Gap detect
- skill: `skill_gap_detect`
- input: `{ "intent": "<intent>" }`

3) Scaffold (dry-run)
- skill: `skill_scaffold`
- input: `{ "skill_name": "<snake_case>", "description": "<one sentence>", "dry_run": true }`

4) Scaffold (write)
- same, but `dry_run: false`

5) Validate
- Create a SkillRequestSpec for the new skill and run it on a small sample
