"""Phase 56 — Policy resolver: precedence and enforcement."""
import json
from pathlib import Path

import pytest

from claudeclockwork.workspace.policy_resolver import resolve_policy


def test_precedence_project_over_default(tmp_path: Path) -> None:
    (tmp_path / ".clockwork_policy.json").write_text(json.dumps({"budget_profile": "fast"}), encoding="utf-8")
    out = resolve_policy(tmp_path)
    assert out["budget_profile"] == "fast"


def test_precedence_project_over_org(tmp_path: Path) -> None:
    org = tmp_path / "org.json"
    org.write_text(json.dumps({"budget_profile": "balanced"}), encoding="utf-8")
    (tmp_path / ".clockwork_policy.json").write_text(json.dumps({"budget_profile": "strong"}), encoding="utf-8")
    out = resolve_policy(tmp_path, org_config_path=org)
    assert out["budget_profile"] == "strong"


def test_per_project_plugin_policy(tmp_path: Path) -> None:
    (tmp_path / ".clockwork_policy.json").write_text(
        json.dumps({"plugin_allowlist_only": True, "max_plugins": 5}), encoding="utf-8"
    )
    out = resolve_policy(tmp_path)
    assert out["plugin_allowlist_only"] is True
    assert out["max_plugins"] == 5
