# pdf_export

**Pack:** `unclassified`

## Purpose
Batch-export Markdown documentation files to PDF (or HTML fallback) — ghost-skill registration (CCW-MVP15).
- Input: `{"project_root": str, "doc_files": [str], "output_dir": str, "naming_scheme": "flat_underscore"|"hierarchical", "fallback_fmt": "html"|"markdown", "mermaid": "embed_as_text"|"skip", "dry_run": bool}`
- Output: `{"exported": [{input_file, output_file, status, tool, bytes, warnings}], "skipped": [{input_file, reason}], "tool_used": str, "output_dir": str, "dry_run": bool}`
- Auto-d…

## Implementation
- Tool: `.claude/tools/skills/pdf_export.py`
- Skill runner: `.claude/tools/skills/skill_runner.py`
- Contracts: `.claude/contracts/`

## Typical usage
```bash
python .claude/tools/skills/skill_runner.py --in <request.json> --out <result.json>
```

## Outputs
Describe output files and write locations here.

## Grenzen / Nicht-Ziele
- Deterministisch: keine semantische "Wahrheitsprüfung" über Inhalte.
- Kann Kandidatenlisten liefern, aber nicht beweisen, dass etwas obsolet ist.
- Wenn LLM-Verfeinerung nötig ist: nutze das passende Playbook (Explore/Write/Critic/DecideGap).
