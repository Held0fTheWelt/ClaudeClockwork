"""
Phase 6 — CI / Eval / Quality Gates

Seven automated gates that permanently verify the skill system.
All gates must pass on a clean checkout.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from claudeclockwork.bridge import run_manifest_skill
from claudeclockwork.runtime import build_registry, build_plugin_registry
from claudeclockwork.core.registry.loader import SkillLoader

ROOT = Path(__file__).resolve().parents[1]
BASELINES_DIR = ROOT / ".clockwork_runtime" / "eval" / "baselines"


# ---------------------------------------------------------------------------
# D6.1 — Manifest Lint Gate
# ---------------------------------------------------------------------------

def test_manifest_lint() -> None:
    """All manifests must pass schema validation (strict mode rejects invalid ones)."""
    registry = build_registry(ROOT, strict=True)
    assert len(registry.validation_errors) == 0, (
        f"{len(registry.validation_errors)} manifest validation error(s):\n"
        + "\n".join(f"  {e}" for e in registry.validation_errors)
    )


# ---------------------------------------------------------------------------
# D6.2 — Import Lint Gate
# ---------------------------------------------------------------------------

def test_import_lint() -> None:
    """All manifest entrypoints must be importable without ModuleNotFoundError."""
    registry = build_registry(ROOT)
    errors: list[str] = []
    for manifest in registry.list_skills(enabled_only=False):
        try:
            SkillLoader.load_skill_class(manifest.entrypoint)
        except (ModuleNotFoundError, AttributeError) as exc:
            errors.append(f"{manifest.name}: {exc}")
    assert not errors, "Import errors:\n" + "\n".join(f"  {e}" for e in errors)


# ---------------------------------------------------------------------------
# D6.3 — Permission Lint Gate
# ---------------------------------------------------------------------------

def test_permission_lint() -> None:
    """All manifest permissions must be declared in .claude/config/permissions.json."""
    cfg_path = ROOT / ".claude" / "config" / "permissions.json"
    assert cfg_path.exists(), f".claude/config/permissions.json not found at {cfg_path}"
    allowed = set(json.loads(cfg_path.read_text(encoding="utf-8")).get("allowed", []))

    registry = build_registry(ROOT)
    errors: list[str] = []
    for manifest in registry.list_skills(enabled_only=False):
        for perm in (manifest.permissions or []):
            if perm not in allowed:
                errors.append(f"{manifest.name}: unknown permission {perm!r}")
    assert not errors, "Permission errors:\n" + "\n".join(f"  {e}" for e in errors)


# ---------------------------------------------------------------------------
# D6.4 — Smoke Run Gate
# ---------------------------------------------------------------------------

def _get_all_manifest_skill_ids() -> list[str]:
    registry = build_registry(ROOT)
    return sorted(m.name for m in registry.list_skills(enabled_only=False))


@pytest.mark.parametrize("skill_id", _get_all_manifest_skill_ids())
def test_skill_smoke(skill_id: str) -> None:
    """Every manifest skill must return a well-formed result dict with status and errors."""
    registry = build_registry(ROOT)
    manifest = registry.get_manifest(skill_id)
    assert manifest is not None

    smoke_inputs = manifest.metadata.get("smoke_inputs", {})
    result = run_manifest_skill(
        {"request_id": "smoke", "skill_id": skill_id, "inputs": smoke_inputs},
        ROOT,
    )
    assert result is not None, f"{skill_id}: run_manifest_skill returned None"
    assert result.get("status") in ("ok", "fail"), (
        f"{skill_id}: status must be 'ok' or 'fail', got {result.get('status')!r}"
    )
    assert "errors" in result, f"{skill_id}: result must contain 'errors' key"


# ---------------------------------------------------------------------------
# D6.5 — Registry Export Diff Gate
# ---------------------------------------------------------------------------

def test_registry_export_diff() -> None:
    """Manifest skill count must not drop below the baseline."""
    baseline_path = BASELINES_DIR / "capability_map.json"
    if not baseline_path.exists():
        pytest.skip("No baseline — run: python3 scripts/update_baselines.py")

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    baseline_count = baseline.get("manifest_skills", 0)

    result = run_manifest_skill(
        {"request_id": "gate", "skill_id": "capability_map_build", "inputs": {}},
        ROOT,
    )
    assert result is not None and result.get("status") == "ok"
    current_count = result["outputs"].get("manifest_skills", 0)

    assert current_count >= baseline_count, (
        f"Skill count dropped: {baseline_count} → {current_count}. "
        "A previously-registered skill is no longer in the registry."
    )

    # Check no previously-present skill is missing by name
    baseline_ids = set(baseline.get("skill_ids", []))
    if baseline_ids:
        registry = build_registry(ROOT)
        current_ids = {m.name for m in registry.list_skills(enabled_only=False)}
        missing = baseline_ids - current_ids
        assert not missing, f"Skills removed from registry: {sorted(missing)}"


# ---------------------------------------------------------------------------
# D6.6 — Plugin Index Diff Gate
# ---------------------------------------------------------------------------

def test_plugin_index_diff() -> None:
    """Plugin count must not drop below the baseline."""
    baseline_path = BASELINES_DIR / "plugin_index.json"
    if not baseline_path.exists():
        pytest.skip("No baseline — run: python3 scripts/update_baselines.py")

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    baseline_count = baseline.get("plugin_count", 0)

    result = run_manifest_skill(
        {"request_id": "gate", "skill_id": "plugin_registry_export", "inputs": {}},
        ROOT,
    )
    assert result is not None and result.get("status") == "ok"
    current_count = result["outputs"].get("plugin_count", 0)

    assert current_count >= baseline_count, (
        f"Plugin count dropped: {baseline_count} → {current_count}."
    )

    baseline_ids = set(baseline.get("plugin_ids", []))
    if baseline_ids:
        plugin_reg = build_plugin_registry(ROOT)
        current_ids = {p.id for p in plugin_reg.list_plugins(enabled_only=False)}
        missing = baseline_ids - current_ids
        assert not missing, f"Plugins removed from registry: {sorted(missing)}"


# ---------------------------------------------------------------------------
# D6.7 — Eval Run Integration Gate
# ---------------------------------------------------------------------------

def test_eval_run_writes_snapshot() -> None:
    """eval_run must write a timestamped JSON snapshot to .clockwork_runtime/eval/results/."""
    results_dir = ROOT / ".clockwork_runtime" / "eval" / "results"

    result = run_manifest_skill(
        {"request_id": "gate", "skill_id": "eval_run", "inputs": {}},
        ROOT,
    )
    assert result is not None
    assert result.get("status") == "ok", f"eval_run failed: {result.get('errors')}"

    outputs = result["outputs"]
    assert "results_path" in outputs, "eval_run must report results_path in outputs"

    results_path = Path(outputs["results_path"])
    assert results_path.exists(), f"Results file not written: {results_path}"

    snapshot = json.loads(results_path.read_text(encoding="utf-8"))
    # Verify D6.7 schema: run_id, pass_count, fail_count, tests
    for key in ("run_id", "pass_count", "fail_count", "tests"):
        assert key in snapshot, f"eval_run snapshot missing key {key!r}: {list(snapshot.keys())}"
    assert isinstance(snapshot["tests"], list)


# ---------------------------------------------------------------------------
# D18 — Planning Drift Gate (Phase 18)
# ---------------------------------------------------------------------------

def test_planning_drift_scan_clean_repo() -> None:
    """planning_drift_scan must pass on a clean repo (version convergence, milestone links, roadmap)."""
    from claudeclockwork.core.gates import run_planning_drift_scan

    result = run_planning_drift_scan(ROOT)
    assert result.get("pass") is True, (
        f"planning_drift_scan failed: {result.get('errors')}"
    )


def test_planning_drift_version_mismatch_fails() -> None:
    """A version mismatch between .claude/VERSION and root VERSION must cause drift scan to fail."""
    from claudeclockwork.core.gates.planning_drift import run_planning_drift_scan, _check_version_convergence
    from pathlib import Path
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / ".claude").mkdir(parents=True)
        (root / ".claude" / "VERSION").write_text("1.0.0", encoding="utf-8")
        (root / "VERSION").write_text("2.0.0", encoding="utf-8")
        ok, errors = _check_version_convergence(root)
        assert ok is False
        assert any("mismatch" in e.lower() or "1.0.0" in e for e in errors)
