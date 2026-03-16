"""Phase 26 — Router v3 bandit and rationale contract tests."""
from __future__ import annotations

import pytest

from claudeclockwork.router.contracts import RouterRationale, select_with_rationale
from claudeclockwork.router.bandit import BanditPolicy
from claudeclockwork.router.profiles_store import ProfilesStore


def test_select_with_rationale_returns_contract_compliant_rationale() -> None:
    r = select_with_rationale(["fast_model", "strong_model"], budget_level="fast")
    assert isinstance(r, RouterRationale)
    assert r.chosen_option == "fast_model"
    assert "fast_model" in r.alternatives_considered
    assert "budget" in r.reason_codes
    assert r.budget_level == "fast"


def test_select_with_rationale_strong_picks_last() -> None:
    r = select_with_rationale(["a", "b", "c"], budget_level="strong")
    assert r.chosen_option == "c"
    assert "quality" in r.reason_codes or "budget" in r.reason_codes


def test_bandit_policy_deterministic_with_seed() -> None:
    policy = BanditPolicy(seed=42)
    options = ["x", "y", "z"]
    chosen1, _ = policy.select(options, "balanced", profiles={})
    chosen2, _ = policy.select(options, "balanced", profiles={})
    assert chosen1 == chosen2


def test_bandit_policy_cold_start_uses_budget() -> None:
    policy = BanditPolicy(seed=1)
    chosen, rationale = policy.select(["fast", "strong"], "fast", profiles={})
    assert chosen in ["fast", "strong"]
    assert rationale["budget_level"] == "fast"
    assert "chosen_option" in rationale


def test_profiles_store_load_empty_when_missing() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        store = ProfilesStore(d)
        assert store.load_profiles() == {}


def test_profiles_store_append_feedback_and_update() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        store = ProfilesStore(d)
        store.append_feedback("opt1", True, 10.0)
        store.append_feedback("opt1", False, 20.0)
        profiles = store.update_from_feedback()
        assert "opt1" in profiles
        assert profiles["opt1"]["trials"] == 2
        assert profiles["opt1"]["successes"] == 1
