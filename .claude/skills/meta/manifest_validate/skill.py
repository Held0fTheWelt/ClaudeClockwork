from __future__ import annotations

import json
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from claudeclockwork.core.registry.loader import SkillLoader
from claudeclockwork.runtime import build_registry

_ALLOWED_CATEGORIES = {
    "analysis", "bundle", "cleanup", "demo", "docs", "evidence",
    "meta", "misc", "ops", "performance", "planning", "plugins",
    "qa", "routing", "security",
}

_REQUIRED_FIELDS = ["name", "version", "description", "category", "entrypoint"]


def _load_allowed_permissions(repo_root: Path) -> set[str]:
    cfg = repo_root / "configs" / "permissions.json"
    if cfg.exists():
        data = json.loads(cfg.read_text(encoding="utf-8"))
        return set(data.get("allowed", []))
    return set()


def _validate_manifest(manifest, allowed_permissions: set[str], registry) -> list[dict]:
    errors: list[dict] = []
    skill = manifest.name

    # Check 1: required fields present
    for field in _REQUIRED_FIELDS:
        if not getattr(manifest, field, None):
            errors.append({"skill": skill, "check": "required_fields", "field": field, "detail": f"missing or empty: {field}"})

    # Check 2: field types (version semver, category string)
    version = getattr(manifest, "version", "")
    if version and not _is_semver(version):
        errors.append({"skill": skill, "check": "field_types", "field": "version", "detail": f"not semver: {version!r}"})

    # Check 3: category is allowed
    category = getattr(manifest, "category", "")
    if category and category not in _ALLOWED_CATEGORIES:
        errors.append({"skill": skill, "check": "category", "field": "category", "detail": f"unknown category {category!r} — allowed: {sorted(_ALLOWED_CATEGORIES)}"})

    # Check 4: permissions exist in configs/permissions.json
    for perm in getattr(manifest, "permissions", []):
        if allowed_permissions and perm not in allowed_permissions:
            errors.append({"skill": skill, "check": "permissions", "field": "permissions", "detail": f"unknown permission {perm!r}"})

    # Check 5: entrypoint resolves without ImportError
    entrypoint = getattr(manifest, "entrypoint", "")
    skill_class = None
    if entrypoint:
        try:
            skill_class = SkillLoader.load_skill_class(entrypoint)
        except Exception as exc:
            errors.append({"skill": skill, "check": "entrypoint", "field": "entrypoint", "detail": f"import failed: {exc}"})

    # Check 6: loaded class is SkillBase subclass
    if skill_class is not None:
        try:
            if not (isinstance(skill_class, type) and issubclass(skill_class, SkillBase)):
                errors.append({"skill": skill, "check": "skill_base", "field": "entrypoint", "detail": f"{skill_class.__name__} is not a subclass of SkillBase"})
        except Exception as exc:
            errors.append({"skill": skill, "check": "skill_base", "field": "entrypoint", "detail": f"subclass check failed: {exc}"})

    return errors


def _is_semver(v: str) -> bool:
    parts = v.split(".")
    if len(parts) != 3:
        return False
    return all(part.isdigit() for part in parts)


class ManifestValidateSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        registry = build_registry(repo_root)
        allowed_permissions = _load_allowed_permissions(repo_root)

        all_errors: list[dict] = []
        checked = 0

        for manifest in registry.list_skills(enabled_only=False):
            checked += 1
            errors = _validate_manifest(manifest, allowed_permissions, registry)
            all_errors.extend(errors)

        payload = {
            "checked": checked,
            "issue_count": len(all_errors),
            "valid": not all_errors,
            "errors": all_errors,
        }

        output_path = kwargs.get("output_path")
        if output_path:
            out = Path(output_path)
            if not out.is_absolute():
                out = repo_root / out
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            payload["output_path"] = str(out)

        warnings = ["Manifest issues detected"] if all_errors else []
        return SkillResult(True, "manifest_validate", data=payload, warnings=warnings)
