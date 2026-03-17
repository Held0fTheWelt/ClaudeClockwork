"""Code Apply Skill - Write generated code to repository files."""
from __future__ import annotations

from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


class CodeApplySkill(SkillBase):
    """Apply generated code to repository files via Ollama agents."""

    ALLOWED_ROOTS = {".claude", "claudeclockwork", "tests", ".project"}

    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        """
        Write code/content to a file in the repository.

        Args:
            context: ExecutionContext with project_root
            file_path (str): Target file path relative to project root
            content (str): Code/content to write
            create_if_missing (bool): Create file if missing (default: True)
            make_dirs (bool): Create parent directories (default: True)

        Returns:
            SkillResult with success, file_path, and error (if any)
        """
        file_path_str = kwargs.get("file_path", "").strip()
        content = kwargs.get("content", "")
        create_if_missing = kwargs.get("create_if_missing", True)
        make_dirs = kwargs.get("make_dirs", True)

        # Validate inputs
        if not file_path_str:
            return SkillResult(
                success=False,
                skill_name="code_apply",
                error="Missing required parameter: file_path",
            )

        if not isinstance(content, str):
            return SkillResult(
                success=False,
                skill_name="code_apply",
                error="Parameter 'content' must be a string",
            )

        try:
            project_root = Path(context.working_directory).resolve()
            file_path = (project_root / file_path_str).resolve()

            # Validate path is within allowed roots
            if not self._is_allowed_path(file_path, project_root):
                return SkillResult(
                    success=False,
                    skill_name="code_apply",
                    error=f"Path {file_path_str} outside allowed write roots: {', '.join(self.ALLOWED_ROOTS)}",
                )

            # Check if file exists
            if file_path.exists() and not create_if_missing:
                return SkillResult(
                    success=False,
                    skill_name="code_apply",
                    error=f"File {file_path_str} exists; set create_if_missing=True to overwrite",
                )

            # Create parent directories if needed
            if make_dirs:
                file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            return SkillResult(
                success=True,
                skill_name="code_apply",
                data={"file_path": str(file_path.relative_to(project_root))},
            )

        except Exception as e:
            return SkillResult(
                success=False,
                skill_name="code_apply",
                error=f"Error writing file: {str(e)}",
            )

    @staticmethod
    def _is_allowed_path(file_path: Path, project_root: Path) -> bool:
        """Check if file path is within allowed write roots."""
        try:
            rel_path = file_path.relative_to(project_root)
            path_parts = rel_path.parts
            if not path_parts:
                return False
            first_part = path_parts[0]
            return first_part in CodeApplySkill.ALLOWED_ROOTS
        except ValueError:
            return False
