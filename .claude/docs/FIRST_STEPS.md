# First Steps — OllamaCode Clockwork

_Last updated: 2026-03-02 (CCW-MVP04)_

## 1. Boot check
```bash
python3 .claude/tools/boot_check.py
```
Verifies Python, Ollama availability, and workspace integrity.

## 2. Run a skill
```bash
python3 .claude/tools/skills/skill_runner.py --in <input.json> --out <result.json>
```
Set `"skill": "<skill_id>"` in the input JSON to select the skill.

## 3. Where reports go

| Output type       | Location                           |
|-------------------|------------------------------------|
| Skill run reports | `.report/`                         |
| Performance logs  | `.claude-performance/`             |
| Evidence bundles  | `.llama_runtime/validation_runs/`  |
| Audit log         | `.llama_runtime/runtime/audit.log` |

## 4. Find an agent

Agent definitions: `.claude/agents/` — sub-folders by domain (`docs/`, `learning/`, `workers/`).

## 5. Find a skill

- Registry: `.claude/skills/registry.md` — full list of all skills with descriptions.
- Quick-start: `.claude/skills/QUICKSTART.md`
- Per-skill detail: `.claude/skills/<skill_id>/README.md`
