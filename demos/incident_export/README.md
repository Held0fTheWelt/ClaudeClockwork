# Demo: Incident / export bundle

Runs a skill then an export_bundle node. Stubbed; no real export. Deterministic.

## Run

```bash
python -m claudeclockwork.cli.run_graph demos/incident_export/graph.json --project-root .
```

## Expected output

- Exit code: 0
- JSON: `"status": "ok"`, `"results"` with `prepare` and `export` entries.
