from __future__ import annotations

import re
import shutil
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult

_SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "<REDACTED_AWS_ACCESS_KEY>"),
    (
        re.compile(r"-----BEGIN (?:RSA|EC|OPENSSH) PRIVATE KEY-----[\s\S]*?-----END (?:RSA|EC|OPENSSH) PRIVATE KEY-----"),
        "<REDACTED_PRIVATE_KEY_BLOCK>",
    ),
    (re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)['\"]?[A-Za-z0-9_\-]{16,}['\"]?"), r"\1<REDACTED_API_KEY>"),
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9_\-\.]{16,}"), r"\1<REDACTED_BEARER>"),
]
_BINARY_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".exe", ".dll", ".so", ".dylib", ".bin"}


def _is_binary(p: Path) -> bool:
    if p.suffix.lower() in _BINARY_EXTS:
        return True
    try:
        return b"\x00" in p.read_bytes()[:2048]
    except Exception:
        return False


def _redact(text: str) -> tuple[str, int]:
    hits = 0
    for rx, repl in _SECRET_PATTERNS:
        text2, count = rx.subn(repl, text)
        hits += count
        text = text2
    return text, hits


class SecurityRedactorSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        repo_root = Path(context.working_directory).resolve()
        src = Path(kwargs.get("input_dir") or "validation_runs").resolve()
        if not src.is_absolute():
            src = (repo_root / kwargs.get("input_dir", "validation_runs")).resolve()
        dst_rel = kwargs.get("output_dir", "validation_runs_redacted")
        dst = Path(dst_rel).resolve() if Path(dst_rel).is_absolute() else (repo_root / dst_rel).resolve()
        dry_run = bool(kwargs.get("dry_run", False))

        if not src.exists():
            return SkillResult(False, "security_redactor", error=f"input_dir not found: {src}")

        if not dry_run:
            if dst.exists():
                shutil.rmtree(dst)
            dst.mkdir(parents=True, exist_ok=True)

        redactions: list[dict] = []
        for p in sorted(src.rglob("*")):
            if p.is_dir():
                continue
            rel = p.relative_to(src)
            if _is_binary(p):
                if not dry_run:
                    out = dst / rel
                    out.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, out)
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            redacted, hits = _redact(text)
            if hits:
                redactions.append({"file": str(rel), "hits": hits})
            if not dry_run:
                out = dst / rel
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(redacted, encoding="utf-8")

        return SkillResult(
            True,
            "security_redactor",
            data={
                "input_dir": str(src),
                "output_dir": str(dst) if not dry_run else None,
                "dry_run": dry_run,
                "redacted_count": len(redactions),
                "findings": redactions,
            },
        )
