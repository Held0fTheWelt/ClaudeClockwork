from __future__ import annotations

import importlib
import json
from pathlib import Path

from claudeclockwork.core.models.skill_manifest import SkillManifest


class SkillLoader:
    @staticmethod
    def load_manifest(manifest_path: Path) -> SkillManifest:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        return SkillManifest.from_dict(data)

    @staticmethod
    def load_skill_class(entrypoint: str):
        module_name, class_name = entrypoint.split(":", maxsplit=1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
