# Demo: Gate pipeline

Runs a gate check node then a skill call. Stubbed execution; deterministic.

## Run

```bash
python -m claudeclockwork.cli.run_graph demos/gate_pipeline/graph.json --project-root .
```

## Expected output

- Exit code: 0
- JSON: `"status": "ok"`, `"results"` with `release_check` and `run_skill` entries.
