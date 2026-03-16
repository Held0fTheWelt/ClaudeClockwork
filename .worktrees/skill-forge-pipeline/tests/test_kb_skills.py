"""Phase 38 — kb.search and kb.explain return citations; no runtime artifacts."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.kb.indexer import index_project
from claudeclockwork.kb.retrieval import search, explain


def test_search_returns_path_snippet_score() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "Docs").mkdir()
        (root / "Docs" / "readme.md").write_text("readme", encoding="utf-8")
        index_project(root)
        kb = root / ".clockwork_runtime" / "kb"
        hits = search(kb, "readme", top_k=5)
        for h in hits:
            assert "path" in h and "snippet" in h and "score" in h
        assert ".clockwork_runtime" not in str(hits)