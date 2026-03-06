from __future__ import annotations

import json
import re
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult

_SNAKE_RE = re.compile(r'^[a-z][a-z0-9_]+$')
_DEFAULT_ROOT = ".claude/skills"


def _class_name(skill_name: str) -> str:
    return "".join(p.title() for p in skill_name.split("_")) + "Skill"


class SkillScaffoldSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        category = str(kwargs.get("category") or "custom").strip().lower()
        skill_name = str(kwargs.get("skill_name") or "").strip().lower()
        description = str(kwargs.get("description") or "").strip()
        dry_run = bool(kwargs.get("dry_run", True))
        legacy_bridge = bool(kwargs.get("legacy_bridge", False))
        root_rel = str(kwargs.get("root") or _DEFAULT_ROOT).strip().strip("/")

        if not _SNAKE_RE.match(skill_name):
            return SkillResult(False, "skill_scaffold", error="inputs.skill_name must be snake_case starting with a letter")
        if not _SNAKE_RE.match(category):
            return SkillResult(False, "skill_scaffold", error="inputs.category must be snake_case starting with a letter")
        if not description:
            return SkillResult(False, "skill_scaffold", error="inputs.description is required")

        cls = _class_name(skill_name)
        base_dir = repo_root / root_rel / category / skill_name
        manifest_path = base_dir / "manifest.json"
        module_path = base_dir / "skill.py"
        init_path = base_dir / "__init__.py"
        readme_path = base_dir / "README.md"

        if any(p.exists() for p in [manifest_path, module_path, init_path]):
            return SkillResult(False, "skill_scaffold", error="collision: target skill package already exists")

        manifest = {
            "id": skill_name,
            "name": skill_name,
            "version": "0.1.0",
            "category": category,
            "description": description,
            "entrypoint": f"skills.{category}.{skill_name}.skill:{cls}",
            "permissions": list(kwargs.get("permissions", [])),
            "aliases": list(kwargs.get("aliases", [])),
            "tags": list(kwargs.get("tags", [])),
            "enabled": True,
            "trust_level": "local",
            "inputs": {},
            "outputs": {},
            "metadata": {"legacy_bridge": legacy_bridge, "source_root": root_rel},
        }

        if legacy_bridge:
            skill_body = (
                f"from __future__ import annotations\n\n"
                f"from claudeclockwork.legacy.adapter import LegacySkillAdapter\n\n\n"
                f"class {cls}(LegacySkillAdapter):\n"
                f'    legacy_skill_id = "{skill_name}"\n'
            )
        else:
            skill_body = (
                f"from __future__ import annotations\n\n"
                f"from claudeclockwork.core.base.skill_base import SkillBase\n"
                f"from claudeclockwork.core.models.execution_context import ExecutionContext\n"
                f"from claudeclockwork.core.models.skill_result import SkillResult\n\n\n"
                f"class {cls}(SkillBase):\n"
                f"    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:\n"
                f'        return SkillResult(True, "{skill_name}", data={{"inputs": kwargs, "note": "Implement skill logic here."}})\n'
            )

        planned = {
            "base_dir": str(base_dir.relative_to(repo_root)),
            "manifest": str(manifest_path.relative_to(repo_root)),
            "module": str(module_path.relative_to(repo_root)),
            "legacy_bridge": legacy_bridge,
            "root": root_rel,
        }

        if dry_run:
            return SkillResult(True, "skill_scaffold", data={"dry_run": True, "planned": planned, "manifest_preview": manifest})

        base_dir.mkdir(parents=True, exist_ok=True)
        init_path.write_text('"""skill package"""\n', encoding="utf-8")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        module_path.write_text(skill_body, encoding="utf-8")
        readme_path.write_text(f"# {skill_name}\n\n{description}\n", encoding="utf-8")

        return SkillResult(True, "skill_scaffold", data={"dry_run": False, "written": planned})
