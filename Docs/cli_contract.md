# CLI Contract — Stable vs Experimental

> Single source of truth for Clockwork CLI stability. Changes to stable surface require SemVer bump and deprecation policy.

## Stable commands

| Command | Description | Output | Exit codes |
|---------|-------------|--------|------------|
| `first-run` | Create runtime root, validate environment | JSON: `{"ok": bool, "errors": list, "info": dict}` | 0 success, 1 failure |
| `env-check` | Verify environment (paths, Ollama, etc.) | JSON: `{"ok": bool, "errors": list, "info": dict}` | 0 success, 1 failure |
| `--skill-id <id> --inputs '{}'` | Run a manifest skill by ID | JSON: `{"status": "ok"\|"fail", ...}` | 0 success, 1 failure |
| (default pipeline) | Run execution pipeline with `--user-input` | JSON: `{"status": "ok"\|"fail", ...}` | 0 success, 1 failure |

**Stable global flags:**
- `--project-root` (default: `.`) — project root directory
- `--inputs` (default: `"{}"`) — JSON object for skill/pipeline inputs

**Stable JSON keys (all commands):**
- Top-level: `status` ("ok" | "fail"), `errors` (list of strings when fail), `ok` (bool where used)

---

## Experimental commands

| Command | Description | Notes |
|---------|-------------|--------|
| `--plugin-healthcheck <PLUGIN_ID>` | Run plugin healthcheck hook | May change output shape |

---

## Output stability rules

- Table-style output is **not** stable; use JSON for scripting.
- JSON keys listed above are stable; additional keys may be added in minor releases.
- Exit code 0 = success, 1 = failure. No other exit codes are guaranteed for these commands.

---

## Version

Contract version: 1.0. See `Docs/semver_policy.md` for change rules.
