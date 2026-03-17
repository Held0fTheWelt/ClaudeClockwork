import os
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


class CodeApplySkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        """Write code/content to a file in the repository."""
        try:
            file_path = kwargs.get('file_path')
            content = kwargs.get('content')
            create_if_missing = kwargs.get('create_if_missing', True)
            make_dirs = kwargs.get('make_dirs', True)

            if not file_path or not content:
                return SkillResult(
                    success=False,
                    error="file_path and content are required"
                )

            # Security check: only allow writing to specific directories
            allowed_roots = ['.claude', 'claudeclockwork', 'tests', '.project']
            normalized_path = os.path.normpath(file_path)
            path_parts = normalized_path.split(os.sep)

            if not path_parts or path_parts[0] not in allowed_roots:
                return SkillResult(
                    success=False,
                    error=f"file_path must be within: {', '.join(allowed_roots)}"
                )

            # Create parent directories if requested
            file_dir = os.path.dirname(normalized_path)
            if make_dirs and file_dir:
                os.makedirs(file_dir, exist_ok=True)

            # Write file
            if os.path.exists(normalized_path) or create_if_missing:
                with open(normalized_path, 'w') as f:
                    f.write(content)

                return SkillResult(
                    success=True,
                    file_path=os.path.abspath(normalized_path)
                )
            else:
                return SkillResult(
                    success=False,
                    error=f"File does not exist: {normalized_path}"
                )

        except Exception as e:
            return SkillResult(
                success=False,
                error=f"Error writing file: {str(e)}"
            )
