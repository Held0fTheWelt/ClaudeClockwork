"""Phase 38 — KB indexer: indexing and retrieval determinism."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claudeclockwork.kb.indexer import index_project
from claudeclockwork.kb.store import load_index
from claudeclockwork.kb.retrieval import search, explain


def test_indexing_deterministic() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "Docs").mkdir()
        (root / "Docs" / "a.md").write_text("hello", encoding="utf-8")
        (root / "mvps").mkdir()
        (root / "mvps" / "p1.md").write_text("mvp", encoding="utf-8")
        kb = root / ".clockwork_runtime" / "kb"
        r1 = index_project(root)
        r2 = index_project(root)
        assert r1["total"] == r2["total"]
        assert r1["total"] >= 2
        idx = load_index(kb)
        assert len(idx) == r1["total"]


def test_retrieval_deterministic() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "Docs").mkdir()
        (root / "Docs" / "policy.md").write_text("policy", encoding="utf-8")
        index_project(root)
        kb = root / ".clockwork_runtime" / "kb"
        out1 = search(kb, "policy", top_k=5)
        out2 = search(kb, "policy", top_k=5)
        assert out1 == out2
        exp = explain(kb, "policy", top_k=3)
        assert "citations" in exp
        assert all(isinstance(c, str) for c in exp["citations"])