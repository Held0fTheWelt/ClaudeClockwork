from __future__ import annotations

import json
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from claudeclockwork.runtime import build_registry


def _run_manifest_validate(repo_root: Path) -> dict:
    """Run manifest_validate logic inline."""
    from claudeclockwork.core.registry.loader import SkillLoader

    registry = build_registry(repo_root)
    issues: list[dict] = []
    for manifest in registry.list_skills(enabled_only=False):
        for field in ("name", "version", "category", "description", "entrypoint"):
            if not getattr(manifest, field, None):
                issues.append({"skill": manifest.name, "field": field, "detail": f"missing {field}"})
        try:
            SkillLoader.load_skill_class(manifest.entrypoint)
        except Exception as exc:
            issues.append({"skill": manifest.name, "field": "entrypoint", "detail": str(exc)})

    return {"pass": not issues, "checked": len(registry.list_skills(enabled_only=False)), "issues": issues}


def _check_required_paths(repo_root: Path) -> dict:
    """Check that core required paths exist."""
    required = [
        ".claude/INDEX.md",
        ".claude/SYSTEM.md",
        ".claude/skills/",
        ".claude/contracts/schemas/",
        ".claude/governance/",
        "VERSION",
        ".report/",
    ]
    missing = [p for p in required if not (repo_root / p).exists()]
    return {"pass": not missing, "missing": missing}


class QaGateSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        gate_level = int(kwargs.get("gate_level", 1))

        gate_results: dict = {}

        # Gate 1: required paths
        path_check = _check_required_paths(repo_root)
        gate_results["required_paths"] = path_check

        # Gate 2: manifest validate (always run)
        manifest_check = _run_manifest_validate(repo_root)
        gate_results["manifest_validate"] = manifest_check

        if gate_level >= 2:
            # Gate 3: all JSON files parse
            bad_json: list[str] = []
            for p in repo_root.rglob("*.json"):
                # skip large/noisy dirs
                parts = p.parts
                if any(d in parts for d in ("__pycache__", ".git", "node_modules", "validation_runs")):
                    continue
                try:
                    json.loads(p.read_text(encoding="utf-8"))
                except Exception as e:
                    bad_json.append(f"{p.relative_to(repo_root)}: {e}")
            gate_results["json_validity"] = {"pass": not bad_json, "bad_count": len(bad_json), "bad_files": bad_json[:5]}

        all_pass = all(v.get("pass", False) for v in gate_results.values())
        return SkillResult(
            all_pass,
            "qa_gate",
            data={
                "pass": all_pass,
                "gate_level": gate_level,
                "gate_results": gate_results,
            },
            error=None if all_pass else "One or more QA gates failed",
        )
