# Runbook: Work Graphs

Execute and recover work graphs.

## Run a work graph

1. **Graph file:** Have a valid graph JSON per [work_graph_spec.md](../work_graph_spec.md).
2. **Command:** `python -m claudeclockwork.cli.run_graph <path/to/graph.json> --project-root .`
3. **Validation:** Exit 0 and JSON `"status": "ok"`. Inspect outputs for each node if needed.
4. **Cache:** Use `--no-cache` to force recompute.

**Rollback:** Re-run with same graph; resume from cache if supported. Fix failing node and re-run.

---

## Resume after failure

1. **Identify:** Check graph run output for failed node ID.
2. **Fix:** Correct input, config, or code for that node.
3. **Resume:** Re-run same graph; runner resumes from last good state when supported.
4. **Validation:** Full run completes with `"status": "ok"`.

**Rollback:** Clear node cache for failed node only if documented; otherwise full re-run.
