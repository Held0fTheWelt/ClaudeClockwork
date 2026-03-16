# CLI API Reference — `claudeclockwork`

_Source: `claudeclockwork/cli.py`_

Invoke as `python -m claudeclockwork.cli <flags>`.

## Flags

| Flag | Type | Description |
|------|------|-------------|
| `--skill-id <id>` | string | Run a skill by its manifest ID |
| `--inputs <json>` | JSON string | Input dict passed to the skill (default: `{}`) |
| `--project-root <path>` | path | Override project root (default: current directory) |
| `--list-skills` | flag | List all registered manifest skills and exit |
| `--plugin-healthcheck <name>` | string | Run healthcheck for a named plugin |
| `--dry-run` | flag | Validate inputs without executing the skill |

## Examples

```bash
# Run a skill with inputs
python -m claudeclockwork.cli --skill-id budget_router --inputs '{"complexity":3,"risk":2,"urgency":1,"mode":"balanced"}'

# Run with empty inputs (uses skill defaults)
python -m claudeclockwork.cli --skill-id capability_map_build --inputs '{}'

# List all registered skills
python -m claudeclockwork.cli --list-skills

# Plugin healthcheck
python -m claudeclockwork.cli --plugin-healthcheck filesystem

# MCP STDIO server (optional — requires `pip install mcp`)
python -m claudeclockwork.mcp
```

## Input Format

`--inputs` accepts a JSON object string. Keys depend on the skill's manifest `inputs` schema.
Pass `'{}'` for skills with no required inputs.

## Output Format

All skills return a JSON object to stdout:
```json
{
  "type": "skill_result_spec",
  "skill_id": "<id>",
  "status": "ok" | "fail",
  "outputs": { ... },
  "errors": [],
  "warnings": [],
  "metrics": {}
}
```
Exit code is `0` for `ok`, `1` for `fail`.

## Dispatch Paths

The CLI uses the **manifest registry** path. An alternative legacy dispatch path exists via `python3 .claude/tools/skills/skill_runner.py <skill_id>`. Both paths reach the same 97 skills. See `CLAUDE.md` for full detail.
