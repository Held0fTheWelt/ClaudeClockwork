from __future__ import annotations

from pathlib import Path

from claudeclockwork.runtime import build_registry

ROOT = Path(__file__).resolve().parents[1]


def test_search_case_insensitive() -> None:
    registry = build_registry(ROOT)
    upper = registry.search("QA")
    lower = registry.search("qa")
    assert {m.name for m in upper} == {m.name for m in lower}


def test_search_exact_name_ranks_first() -> None:
    registry = build_registry(ROOT)
    results = registry.search("qa_gate")
    assert len(results) > 0
    assert results[0].name == "qa_gate"


def test_search_no_match_returns_empty() -> None:
    registry = build_registry(ROOT)
    # Use pure gibberish with no underscore separators so the search tokenizer
    # produces a single token that matches nothing in any corpus.
    results = registry.search("xyzzyqqqfrobnicatorzzzz")
    assert results == []


def test_list_skills_enabled_only_lte_all() -> None:
    registry = build_registry(ROOT)
    all_skills = registry.list_skills(enabled_only=False)
    enabled_skills = registry.list_skills(enabled_only=True)
    assert len(enabled_skills) <= len(all_skills)


def test_list_skills_sorted_by_category_then_name() -> None:
    registry = build_registry(ROOT)
    skills = registry.list_skills(enabled_only=False)
    pairs = [(m.category, m.name) for m in skills]
    assert pairs == sorted(pairs)
