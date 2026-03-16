"""Phase 16 — changelog_generate: git log → structured CHANGELOG entry."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult

_CLASSIFICATIONS = [
    (re.compile(r'^(feat|add|new)\b', re.I), "Added"),
    (re.compile(r'^(fix|bug)\b', re.I), "Fixed"),
    (re.compile(r'^refactor\b', re.I), "Changed"),
    (re.compile(r'^(docs?|doc)\b', re.I), "Documentation"),
    (re.compile(r'^(chore|test|ci)\b', re.I), "Maintenance"),
]


def _classify(message: str) -> str:
    for pattern, label in _CLASSIFICATIONS:
        if pattern.match(message):
            return label
    return "Changed"


def _run_git(args: list[str], cwd: Path) -> tuple[int, str]:
    r = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


class ChangelogGenerateSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        root = Path(context.working_directory).resolve()
        since_tag = kwargs.get("since_tag", "")
        max_commits = max(1, int(kwargs.get("max_commits", 20)))
        output_path_str = kwargs.get("output_path", "")
        version_label = kwargs.get("version_label", "Unreleased")

        # Build git log range
        if since_tag:
            range_arg = f"{since_tag}..HEAD"
            log_args = ["log", "--format=%H|%s", range_arg]
        else:
            log_args = ["log", "--format=%H|%s", f"-n{max_commits}"]

        rc, log_out = _run_git(log_args, root)
        if rc != 0 or not log_out:
            entries: list[dict] = []
        else:
            entries = []
            for line in log_out.splitlines():
                if "|" not in line:
                    continue
                commit_hash, message = line.split("|", 1)
                entry_type = _classify(message.strip())
                entries.append({
                    "type": entry_type,
                    "description": message.strip(),
                    "hash": commit_hash[:8],
                })

        # Build markdown block
        from collections import defaultdict
        by_type: dict[str, list[dict]] = defaultdict(list)
        for e in entries:
            by_type[e["type"]].append(e)

        lines = [f"## [{version_label}]", ""]
        for label in ["Added", "Fixed", "Changed", "Documentation", "Maintenance"]:
            section = by_type.get(label, [])
            if section:
                lines.append(f"### {label}")
                for e in section:
                    lines.append(f"- {e['description']} ({e['hash']})")
                lines.append("")
        changelog_text = "\n".join(lines).rstrip() + "\n"

        # Optionally write to file
        written = False
        if output_path_str:
            out_path = Path(output_path_str)
            if not out_path.is_absolute():
                out_path = (root / output_path_str).resolve()
            try:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with out_path.open("a", encoding="utf-8") as f:
                    f.write(changelog_text + "\n")
                written = True
            except Exception:
                pass

        return SkillResult(True, "changelog_generate", data={
            "entries": entries,
            "changelog_text": changelog_text,
            "written": written,
        })
