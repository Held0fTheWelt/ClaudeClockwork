# Playbook: Analysis Suite Pipeline

Recurring engineering work:
- Patterns erkennen
- Mutationen erkennen
- Systeme erfassen
- Mechaniken verstehen
- Assimilieren von Code
- Logs standardisieren
- Copyrights standardisieren
- Broken references fix

All skills run via:
`python .claude/tools/skills/skill_runner.py --in request.json`

## Recommended run order
1) `system_map` (emit Mermaid graph)
2) `pattern_detect` (seed pattern catalogue)
3) `mutation_detect` (snapshot diffs + renames)
4) `mechanic_explain` (deep-dive doc scaffold)
5) `code_assimilate` (integration plan)
6) `log_standardize` (log lint)
7) `copyright_standardize` (header lint)
8) `reference_fix` (docs link integrity after moves)
