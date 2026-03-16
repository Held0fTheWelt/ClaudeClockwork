"""Phase 35 — Local worker: process job envelope using existing runtime."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from claudeclockwork.workgraph.runner import run_graph


def process_envelope(envelope: dict[str, Any], project_root: Path | str) -> dict[str, Any]:
    """Process a job envelope. Build minimal graph from node_spec, run, return result under runtime root."""
    root = Path(project_root).resolve()
    run_root = root / ".clockwork_runtime"
    run_root.mkdir(parents=True, exist_ok=True)
    node_spec = envelope.get("node_spec", {})
    node_id = node_spec.get("id", envelope.get("job_id", "job"))
    graph = {
        "nodes": [{"id": node_id, "inputs": envelope.get("input_artifact_refs") or {}, "config": node_spec}],
        "edges": [],
    }
    out = run_graph(graph, root, use_cache=True, resume=True)
    if out.get("status") == "fail":
        return {"status": "error", "job_id": envelope.get("job_id"), "error": out.get("error"), "failed_node": out.get("failed_node")}
    result = (out.get("results") or {}).get(node_id, {})
    # Persist result for artifact shipping
    jobs_dir = run_root / "worker_jobs"
    jobs_dir.mkdir(parents=True, exist_ok=True)
    job_file = jobs_dir / f"{envelope.get('job_id', 'unknown')}.json"
    job_file.write_text(json.dumps({"envelope": envelope, "result": result}) + "\n", encoding="utf-8")
    return {"status": "ok", "job_id": envelope.get("job_id"), "result": result}
