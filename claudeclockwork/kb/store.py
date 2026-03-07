"""Phase 38 — KB store: doc id, path, content hash, metadata. Incremental by hash."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def doc_id(path: str, content_hash: str) -> str:
    return hashlib.sha256(f"{path}:{content_hash}".encode()).hexdigest()[:16]


def index_path(kb_root: Path | str) -> Path:
    return Path(kb_root).resolve() / "kb_index.jsonl"


def append_doc(kb_root: Path | str, path: str, content_hash: str, metadata: dict[str, Any]) -> None:
    root = Path(kb_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    idx = index_path(kb_root)
    rec = {"doc_id": doc_id(path, content_hash), "path": path, "content_hash": content_hash, "metadata": metadata}
    with open(idx, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def load_index(kb_root: Path | str) -> list[dict[str, Any]]:
    idx = index_path(kb_root)
    if not idx.is_file():
        return []
    out = []
    for line in idx.read_text(encoding="utf-8").strip().split("\n"):
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out
