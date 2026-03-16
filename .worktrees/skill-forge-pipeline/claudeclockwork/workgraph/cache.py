"""Phase 30 — Node output cache (hash-based) under runtime root."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class NodeCache:
    """Cache key = node_id + inputs hash. Store under runtime_root/workgraph_cache/."""

    def __init__(self, runtime_root: Path | str) -> None:
        self._root = Path(runtime_root).resolve() / "workgraph_cache"
        self._root.mkdir(parents=True, exist_ok=True)

    def _key(self, node_id: str, inputs: dict[str, Any]) -> str:
        h = hashlib.sha256(json.dumps({"id": node_id, "inputs": inputs}, sort_keys=True).encode()).hexdigest()[:16]
        return f"{node_id}_{h}"

    def get(self, node_id: str, inputs: dict[str, Any]) -> Any | None:
        k = self._key(node_id, inputs)
        p = self._root / f"{k}.json"
        if not p.is_file():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def set(self, node_id: str, inputs: dict[str, Any], output: Any) -> None:
        k = self._key(node_id, inputs)
        p = self._root / f"{k}.json"
        p.write_text(json.dumps(output) + "\n", encoding="utf-8")
