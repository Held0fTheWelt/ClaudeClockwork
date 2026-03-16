"""Phase 30 — CLI: run a work graph and optionally resume from cache."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from claudeclockwork.workgraph.runner import run_graph


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python -m claudeclockwork.cli.run_graph <graph.json> [--project-root .] [--no-cache]", file=sys.stderr)
        return 1
    graph_path = Path(sys.argv[1])
    project_root = Path(".")
    use_cache = True
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--project-root" and i + 1 < len(sys.argv):
            project_root = Path(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--no-cache":
            use_cache = False
            i += 1
        else:
            i += 1
    if not graph_path.is_file():
        print(f"Graph file not found: {graph_path}", file=sys.stderr)
        return 1
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    result = run_graph(graph, project_root, use_cache=use_cache, resume=True)
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
