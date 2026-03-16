from __future__ import annotations

import re
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


def _lint_plan(text: str) -> tuple[list[dict], list[dict]]:
    errors: list[dict] = []
    warnings: list[dict] = []

    heading_re = re.compile(r"^#{1,3}\s+(.*)", re.MULTILINE)
    headings = [m.group(1).strip() for m in heading_re.finditer(text)]

    # Definition of Done
    has_dod = any(re.search(r"\bDefinition of Done\b|\bDoD\b", h, re.I) for h in headings)
    if not has_dod:
        errors.append({"section": "Definition of Done", "message": "Missing '## Definition of Done' or '## DoD' section"})
    elif not re.search(r"- \[", text):
        warnings.append({"section": "Definition of Done", "message": "DoD section has no checkboxes (- [ ])"})

    # Numbered task sections (## N1, ## P1, ## S1, etc.)
    if not re.search(r"^##\s+[NPS]\d+", text, re.MULTILINE):
        warnings.append({"section": "tasks", "message": "No numbered task sections found (## N1, ## P1, ## S1 etc.)"})

    # Files Changed
    if not any(re.search(r"\bFiles Changed\b", h, re.I) for h in headings):
        warnings.append({"section": "Files Changed", "message": "Missing '## Files Changed' section"})

    # Acceptance Criteria
    if not any(re.search(r"\bAcceptance Criteria\b", h, re.I) for h in headings):
        errors.append({"section": "Acceptance Criteria", "message": "Missing '## Acceptance Criteria' section"})

    return errors, warnings


class PlanLintSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        path_str = kwargs.get("path", "")
        text = kwargs.get("text", "")

        if not path_str and not text:
            return SkillResult(False, "plan_lint", error="one of 'path' or 'text' is required")

        if path_str:
            p = Path(path_str)
            if not p.is_absolute():
                p = (Path(context.working_directory) / path_str).resolve()
            if not p.exists():
                return SkillResult(False, "plan_lint", error=f"plan file not found: {p}")
            text = p.read_text(encoding="utf-8")

        errors, warnings_list = _lint_plan(text)
        ok = len(errors) == 0

        return SkillResult(
            ok,
            "plan_lint",
            data={
                "pass": ok,
                "errors": errors,
                "warnings": [w["message"] for w in warnings_list],
            },
            error=(f"{len(errors)} lint error(s)" if not ok else None),
            warnings=[w["message"] for w in warnings_list],
        )
