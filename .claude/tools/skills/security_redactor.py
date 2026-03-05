#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "<REDACTED_AWS_ACCESS_KEY>"),
    (re.compile(r"-----BEGIN (?:RSA|EC|OPENSSH) PRIVATE KEY-----[\s\S]*?-----END (?:RSA|EC|OPENSSH) PRIVATE KEY-----"), "<REDACTED_PRIVATE_KEY_BLOCK>"),
    (re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)['\"]?[A-Za-z0-9_\-]{16,}['\"]?"), r"\1<REDACTED_API_KEY>"),
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9_\-\.]{16,}"), r"\1<REDACTED_BEARER>"),
]

BINARY_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".exe", ".dll", ".so", ".dylib", ".bin"}


def _is_binary(p: Path) -> bool:
    if p.suffix.lower() in BINARY_EXTS:
        return True
    try:
        data = p.read_bytes()[:2048]
    except Exception:
        return False
    return b"\x00" in data


def _redact_text(text: str) -> tuple[str, int]:
    hits = 0
    for rx, repl in SECRET_PATTERNS:
        text2, c = rx.subn(repl, text)
        if c:
            hits += c
            text = text2
    return text, hits


def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    src = Path(inputs.get("input_dir", "validation_runs")).resolve()
    dst = Path(inputs.get("output_dir", "validation_runs_redacted")).resolve()

    if not src.exists():
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": req.get("skill_id", "security_redactor"),
            "status": "fail",
            "outputs": {"input_dir": str(src)},
            "metrics": {},
            "errors": ["input_dir does not exist"],
            "warnings": [],
        }

    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)

    redactions = []
    files_copied = 0
    total_hits = 0

    for p in src.rglob("*"):
        rel = p.relative_to(src)
        outp = dst / rel
        if p.is_dir():
            outp.mkdir(parents=True, exist_ok=True)
            continue

        outp.parent.mkdir(parents=True, exist_ok=True)

        if _is_binary(p):
            shutil.copy2(p, outp)
            files_copied += 1
            continue

        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            shutil.copy2(p, outp)
            files_copied += 1
            continue

        redacted, hits = _redact_text(text)
        total_hits += hits
        outp.write_text(redacted, encoding="utf-8")
        files_copied += 1
        if hits:
            redactions.append({"file": str(rel), "hits": hits})

    report = {
        "type": "redaction_report",
        "input_dir": str(src),
        "output_dir": str(dst),
        "files_copied": files_copied,
        "total_hits": total_hits,
        "redactions": redactions,
    }

    report_path = dst / "reports" / "redaction_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "security_redactor"),
        "status": "ok",
        "outputs": {"report": str(report_path), "output_dir": str(dst)},
        "metrics": {"files": files_copied, "redaction_hits": total_hits},
        "errors": [],
        "warnings": [],
    }
