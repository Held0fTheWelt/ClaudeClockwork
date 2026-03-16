"""Phase 16 — git_summary: structured git log and diff output."""
from __future__ import annotations

import subprocess
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


def _run_git(args: list[str], cwd: Path) -> tuple[int, str]:
    result = subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip()


class GitSummarySkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        root = Path(kwargs.get("root", context.working_directory)).resolve()
        max_commits = max(1, int(kwargs.get("max_commits", 10)))
        include_diff = bool(kwargs.get("include_diff", False))

        # Check we're inside a git repo
        rc, _ = _run_git(["rev-parse", "--git-dir"], root)
        if rc != 0:
            return SkillResult(True, "git_summary", data={
                "commits": [], "files_changed": [], "commit_count": 0,
            })

        # git log
        rc, log_out = _run_git(
            ["log", f"--format=%H|%an|%ad|%s", "--date=short", f"-n{max_commits}"],
            root,
        )
        commits = []
        if rc == 0 and log_out:
            for line in log_out.splitlines():
                parts = line.split("|", 3)
                if len(parts) == 4:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3],
                    })

        # files changed across the commit range
        range_arg = f"HEAD~{max_commits}..HEAD"
        rc2, files_out = _run_git(["diff", "--name-only", range_arg], root)
        if rc2 != 0:
            # Fallback for repos with fewer commits than max_commits
            _, files_out = _run_git(
                ["diff", "--name-only", "$(git rev-list --max-parents=0 HEAD)", "HEAD"],
                root,
            )
        files_changed = [f for f in files_out.splitlines() if f] if files_out else []

        data: dict = {
            "commits": commits,
            "files_changed": files_changed,
            "commit_count": len(commits),
        }

        if include_diff:
            _, diff_text = _run_git(["diff", range_arg], root)
            data["diff_text"] = diff_text

        return SkillResult(True, "git_summary", data=data)
