"""Phase 38 — Retrieval: keyword fallback (BM25-like); deterministic ranked results."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from claudeclockwork.kb.store import load_index


def search(kb_root: Path | str, query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Keyword search over index. Returns [{path, snippet, score}] deterministic."""
    kb = Path(kb_root).resolve()
    index = load_index(kb)
    q_lower = query.lower().split()
    scored: list[tuple[float, dict]] = []
    for rec in index:
        path = rec.get("path", "")
        snippet = path  # minimal snippet
        score = 0.0
        for t in q_lower:
            if t in path.lower():
                score += 1.0
        if score > 0:
            scored.append((score, {"path": path, "snippet": snippet, "score": score}))
    scored.sort(key=lambda x: (-x[0], x[1]["path"]))
    return [s for _, s in scored[:top_k]]


def explain(kb_root: Path | str, question: str, top_k: int = 3) -> dict[str, Any]:
    """Return answer summary plus file path citations."""
    results = search(kb_root, question, top_k=top_k)
    citations = [r["path"] for r in results]
    return {"answer": "See cited files.", "citations": citations, "hits": results}
