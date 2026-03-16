#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path

CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]*`")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA|EC|OPENSSH) PRIVATE KEY-----"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
]

def _strip_code(md: str) -> str:
    md = CODE_FENCE_RE.sub("", md)
    md = INLINE_CODE_RE.sub("", md)
    return md

def _check_markdown_links(root: Path) -> list[str]:
    broken = []
    for p in root.rglob("*.md"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        text = _strip_code(text)
        for target in LINK_RE.findall(text):
            if target.startswith(("http://","https://","mailto:")):
                continue
            if "#" in target:
                target = target.split("#",1)[0]
            if not target:
                continue
            tp = (p.parent / target).resolve()
            if not tp.exists():
                broken.append(f"{p.relative_to(root)} -> {target}")
    return broken

def _check_json_validity(root: Path) -> list[str]:
    bad = []
    for p in root.rglob("*.json"):
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            bad.append(f"{p.relative_to(root)}: {e}")
    return bad

def _scan_secrets(root: Path) -> list[str]:
    hits = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if p.suffix.lower() in {".png",".jpg",".jpeg",".zip",".exe",".dll",".bin",".pdf"}:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for rx in SECRET_PATTERNS:
            if rx.search(text):
                hits.append(str(p.relative_to(root)))
                break
    return hits

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    root = Path(inputs.get("root", ".")).resolve()
    scan_secrets = bool(inputs.get("scan_secrets", False))
    broken = _check_markdown_links(root)
    bad_json = _check_json_validity(root)
    secrets = _scan_secrets(root) if scan_secrets else []
    status = "ok" if (not broken and not bad_json and not secrets) else "fail"
    errors = []
    if broken: errors.append(f"Broken links: {len(broken)}")
    if bad_json: errors.append(f"Invalid JSON: {len(bad_json)}")
    if secrets: errors.append(f"Secrets detected: {len(secrets)}")
    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id": req.get("skill_id","repo_validate"),
        "status": status,
        "outputs": {
            "broken_links": broken,
            "invalid_json": bad_json,
            "secrets": secrets,
        },
        "metrics": {
            "broken_links_count": len(broken),
            "invalid_json_count": len(bad_json),
            "secrets_count": len(secrets),
        },
        "errors": errors if status=="fail" else [],
        "warnings": [],
    }
