from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult

_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`]*`")
_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA|EC|OPENSSH) PRIVATE KEY-----"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
]
_BINARY_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".exe", ".dll", ".so", ".bin"}


def _check_json_validity(root: Path) -> list[str]:
    bad = []
    for p in root.rglob("*.json"):
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            bad.append(f"{p.relative_to(root)}: {e}")
    return bad


def _check_boot(project_root: Path) -> tuple[bool, str]:
    boot = project_root / ".claude" / "tools" / "boot_check.py"
    if not boot.is_file():
        return False, f"boot_check.py not found at {boot}"
    try:
        r = subprocess.run([sys.executable, str(boot)], capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            return True, "boot_check passed"
        return False, (r.stdout + r.stderr).strip()[:200]
    except Exception as exc:
        return False, f"boot_check error: {exc}"


class RepoValidateSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(kwargs.get("root") or context.working_directory).resolve()
        scan_secrets = bool(kwargs.get("scan_secrets", False))

        bad_json = _check_json_validity(repo_root)
        boot_ok, boot_msg = _check_boot(repo_root)

        secrets: list[str] = []
        if scan_secrets:
            for p in repo_root.rglob("*"):
                if p.is_dir() or p.suffix.lower() in _BINARY_EXTS:
                    continue
                try:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                for rx in _SECRET_PATTERNS:
                    if rx.search(text):
                        secrets.append(str(p.relative_to(repo_root)))
                        break

        findings = []
        if bad_json:
            findings.append({"check": "json_validity", "status": "fail", "count": len(bad_json), "detail": bad_json[:5]})
        if not boot_ok:
            findings.append({"check": "boot_check", "status": "fail", "detail": boot_msg})
        if secrets:
            findings.append({"check": "secrets", "status": "fail", "count": len(secrets), "detail": secrets[:5]})

        passed = not findings
        return SkillResult(
            passed,
            "repo_validate",
            data={
                "pass": passed,
                "boot_check": boot_msg,
                "bad_json_count": len(bad_json),
                "secret_count": len(secrets),
                "findings": findings,
            },
            error=None if passed else f"{len(findings)} check(s) failed",
        )
