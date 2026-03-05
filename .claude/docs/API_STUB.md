# CLI API Reference Stub — `oodle` / `llamacode`

_Last updated: 2026-03-02 (CCW-MVP04)_
_Source: `llamacode/cli.py` and sub-modules_

Invoke as `oodle <command>` or `python -m llamacode <command>`.

---

## Top-level flags

| Flag          | Description                              |
|---------------|------------------------------------------|
| `--version`   | Print version and exit                   |
| `--self-test` | Run a quick internal self-test and exit  |

---

## Commands

### `doctor`
Run diagnostics and report system health (Python version, app version, Ollama connectivity).
```
oodle doctor [--json]
```

### `task run <TASK_FILE>`
Execute a task from a JSON task file (single-phase, no planning step).
```
oodle task run <task_file> [--workspace DIR] [--json]
```

### `pack <TASK_SPEC_FILE>`
Build a context pack from a `TaskSpec` JSON file.
```
oodle pack <task_spec_file> [--workspace DIR] [--budget FILE] [--out FILE] [--suggest FILE] [--json]
```

### `plan build <TASK_SPEC_FILE>`
Build a plan from a `TaskSpec` (dry-run, no execution).
```
oodle plan build <task_spec_file> [--workspace DIR] [--out FILE] [--json]
```

### `plan run <TASK_SPEC_FILE>`
Plan then execute (two-phase enforcement). Optionally auto-commit on success.
```
oodle plan run <task_spec_file> [--workspace DIR] [--json] [--git-commit] [--auto-branch]
```

### `snapshot ls`
List all workspace snapshots.
```
oodle snapshot ls [--workspace DIR] [--json]
```

### `snapshot restore <SNAPSHOT_ID>`
Restore workspace to a named snapshot.
```
oodle snapshot restore <snapshot_id> [--workspace DIR]
```

### `chat`
Start a conversational REPL session (natural language → TaskSpec → execution).
```
oodle chat [--workspace DIR] [--replay FILE] [--json]
```

### `team <TASK_SPEC_FILE>`
Run the Planner → Executor multi-agent team protocol for a `TaskSpec`.
```
oodle team <task_spec_file> [--workspace DIR] [--json] [--max-payload-bytes N]
```

### `io import <SRC> <DST>`
Import SRC to DST with I/O policy enforcement.
```
oodle io import <src> <dst> [--workspace DIR] [--binary] [--json]
```

### `io overwrite <DST> --from <SRC>`
Overwrite DST from SRC. Always creates a snapshot and audit record.
```
oodle io overwrite <dst> --from <src> [--workspace DIR] [--json]
```

### `artifact build <MANIFEST_FILE>`
Build an artifact from a manifest JSON into a staging directory.
```
oodle artifact build <manifest_file> [--workspace DIR] [--json]
```

### `artifact run <ARTIFACT_ID>`
Run smoke tests for a built artifact in a sandbox.
```
oodle artifact run <artifact_id> [--workspace DIR] [--json]
```

### `artifact export <ARTIFACT_ID> <DST>`
Export a built artifact to DST, verifying checksums.
```
oodle artifact export <artifact_id> <dst> [--workspace DIR] [--json]
```

### `plugins ls`
List all discovered plugins and their enabled/disabled state.
```
oodle plugins ls [--workspace DIR] [--json]
```

### `plugins enable <NAME>`
Enable a plugin by name.
```
oodle plugins enable <name> [--workspace DIR]
```

### `plugins disable <NAME>`
Disable a plugin by name.
```
oodle plugins disable <name> [--workspace DIR]
```

### `plugins verify`
Check that all enabled plugins can be imported (informational, non-crashing).
```
oodle plugins verify [--workspace DIR] [--json]
```

### `models ls`
List installed local models from catalog or live Ollama query.
```
oodle models ls [--workspace DIR] [--json]
```

### `models refresh`
Rebuild `model_catalog.json` and `capability_map.json` from Ollama.
```
oodle models refresh [--workspace DIR] [--base-url URL] [--json]
```

### `models capmap`
Show the capability map for all models or a single model.
```
oodle models capmap [--model NAME] [--workspace DIR] [--json]
```

### `agents ls`
List all agents in the registry.
```
oodle agents ls [--workspace DIR] [--json]
```

### `agents tree`
Display the agent hierarchy as an ASCII tree.
```
oodle agents tree [--workspace DIR]
```

### `agents verify`
Validate the agent registry for orphans and cycles.
```
oodle agents verify [--workspace DIR] [--json]
```

---

_Full reference: `docs/tech/api_or_cli.md`_
