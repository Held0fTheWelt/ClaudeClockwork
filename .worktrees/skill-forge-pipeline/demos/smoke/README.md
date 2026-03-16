# Demo: Smoke pipeline

One-command demo that runs a minimal work graph (gate + skill stub). Deterministic; no external services.

## Run

```bash
python -m claudeclockwork.cli.run_graph demos/smoke/graph.json --project-root .
```

## Expected output

- Exit code: 0
- JSON: `"status": "ok"`, `"results"` contains `gate` and `step` with `"status": "ok"`.

## Seed / stubs

Execution uses the built-in work graph runner; nodes are stubbed (no real gate or skill call). Deterministic for CI.
