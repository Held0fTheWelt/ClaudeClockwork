from __future__ import annotations

import json
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


def _load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


class SpecValidateSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        schema_rel = kwargs.get("schema")
        examples = kwargs.get("examples", [])
        if isinstance(examples, str):
            examples = [examples]

        if not schema_rel:
            return SkillResult(False, "spec_validate", error="inputs.schema is required")

        schema_path = (repo_root / schema_rel).resolve() if not Path(schema_rel).is_absolute() else Path(schema_rel)
        if not schema_path.exists():
            return SkillResult(False, "spec_validate", error=f"schema not found: {schema_path}")

        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            return SkillResult(False, "spec_validate", error="jsonschema package not installed")

        try:
            schema = _load_json(schema_path)
            validator = Draft202012Validator(schema)
        except Exception as e:
            return SkillResult(False, "spec_validate", error=f"failed to load schema: {e}")

        example_paths = [
            (repo_root / ex).resolve() if not Path(ex).is_absolute() else Path(ex)
            for ex in examples
        ]

        failures: list[dict] = []
        for p in example_paths:
            try:
                inst = _load_json(p)
            except Exception as e:
                failures.append({"example": str(p), "errors": [f"failed to load: {e}"]})
                continue
            errs = sorted(validator.iter_errors(inst), key=lambda e: e.path)
            if errs:
                failures.append({
                    "example": str(p),
                    "errors": [f"{'/'.join(str(x) for x in e.path)}: {e.message}" for e in errs[:20]],
                })

        valid = not failures
        return SkillResult(
            valid,
            "spec_validate",
            data={
                "valid": valid,
                "checked": len(example_paths),
                "failures": failures,
            },
            error=f"{len(failures)} examples failed validation" if failures else None,
        )
