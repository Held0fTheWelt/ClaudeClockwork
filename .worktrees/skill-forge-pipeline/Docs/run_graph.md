# Run Graph (Phase 30)

Run a Work Graph (DAG) with caching and resume.

## Usage

```bash
python -m claudeclockwork.cli.run_graph path/to/graph.json [--project-root .] [--no-cache]
```

- **graph.json** — Must conform to `work_graph.schema.json` (nodes, optional edges).
- **--project-root** — Project root (default: current dir). Runtime root is `project_root/.clockwork_runtime`.
- **--no-cache** — Disable cache (run all nodes).

## Resume

When cache is enabled, nodes whose (id, inputs) match a cached result are skipped. Run again after a failure after fixing the failed node; completed nodes will be reused.

## Failure

On first failing node, the run stops and prints a summary with `failed_node` and `error`. Fix and re-run to resume from cache.
