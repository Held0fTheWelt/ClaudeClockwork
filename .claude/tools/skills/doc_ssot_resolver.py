#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`([^`]+)`")

IGNORE_PREFIXES = ("http://", "https://", "mailto:")
PROJECT_ROOT_PREFIX = "<PROJECT_ROOT>/"
EVIDENCE_ROOT_PREFIX = "validation_runs/"

FILE_EXTS = (".md", ".json", ".jsonl", ".py", ".yaml", ".yml", ".txt", ".sh")

LOCATOR_SUFFIX_RE = re.compile(r"(?:#L\d+|:\d+(?:-\d+)?)$")

def _strip_locators(tok: str) -> str:
    """Strip common line/fragment locators like `:42` or `#L42` from a path token."""
    return LOCATOR_SUFFIX_RE.sub('', tok)

SINGLE_FILE_ALLOWLIST = {
    "SYSTEM.md",
    "skills.md",
    "collaboration.md",
    "MEMORY.md",
    "ROADMAP.md",
    "ARCHITECTURE.md",
}
PATHISH_RE = re.compile(r"^(?:[A-Za-z0-9_.\-]+/)+[A-Za-z0-9_.\-]+$")

def _strip_code_fences(md: str) -> str:
    return CODE_FENCE_RE.sub("", md)

def _iter_backtick_tokens(md: str) -> list[str]:
    md = _strip_code_fences(md)
    return [m.group(1).strip() for m in INLINE_CODE_RE.finditer(md)]

def _is_pathish(tok: str, *, verify_legacy: bool = False) -> bool:
    """
    Decide whether an inline-backtick token is intended to be a path reference.

    Notes:
    - Backticks are frequently used for *code formatting*; we avoid false positives.
    - We only validate *file-like* paths by default (directories and examples like `...` are ignored).
    """
    if not tok or " " in tok:
        return False
    if tok.startswith(IGNORE_PREFIXES):
        return False


    tok_norm = _strip_locators(tok)

    # Directories / examples
    if tok_norm.endswith("/") or tok_norm.endswith("...") or tok_norm.endswith("/..."):
        return False

    # Globs / templates / placeholders are not concrete paths
    if any(ch in tok for ch in ("*", "?", "[", "]", "{", "}")):
        return False
    if ("<" in tok or ">" in tok) and not tok.startswith(PROJECT_ROOT_PREFIX):
        return False

    # Templates like `<PROJECT_ROOT>/.../<NAME>.md` are not concrete paths
    if tok.startswith(PROJECT_ROOT_PREFIX):
        tail = tok[len(PROJECT_ROOT_PREFIX):]
        if ("<" in tail) or (">" in tail):
            return False

    # Runtime outputs should live under evidence root (validation_runs/...)
    if tok.startswith(("reports/", "artifacts/", "logs/")):
        return False

    # Legacy cross-project references are optional
    if tok.startswith(".claude/") and not verify_legacy:
        return False

    # Strong prefixes
    if tok.startswith(EVIDENCE_ROOT_PREFIX):
        return True  # will be skipped in resolver
    if tok.startswith(PROJECT_ROOT_PREFIX):
        # only validate file-like refs (avoid directory pointers)
        return True
    if tok.startswith(".claude/"):
        return tok_norm.endswith(FILE_EXTS)

    if tok.startswith(".claude/"):
        return True  # verify_legacy=True case

    if "contracts/" in tok:
        return True

    # Slash paths must look like files
    if "/" in tok:
        return tok_norm.endswith(FILE_EXTS)

    # Single-file tokens are treated as paths only for key allowlisted filenames
    if tok_norm in SINGLE_FILE_ALLOWLIST and tok_norm.endswith(FILE_EXTS):
        return True

    return False



def _unique_match(root: Path, filename: str) -> tuple[Path | None, int]:
    hits = [p for p in root.rglob(filename) if p.is_file()]
    if len(hits) == 1:
        return hits[0], 1
    return None, len(hits)

def _resolve(tok: str, claude_root: Path, project_root: Path, *, verify_project_root: bool) -> tuple[Path | None, str]:
    """Resolve tok to a file path.

    Returns (path_or_none, note). note can be:
    - "ok"
    - "skip_evidence"
    - "ambiguous:<n>"
    - "missing"
    """
    tok_norm = _strip_locators(tok)
    if tok.startswith(EVIDENCE_ROOT_PREFIX):
        return None, "skip_evidence"

    if tok.startswith(PROJECT_ROOT_PREFIX):
        rel = tok_norm[len(PROJECT_ROOT_PREFIX):]
        # By default we treat <PROJECT_ROOT>/... refs as external, unless explicitly enabled.
        # Exception: <PROJECT_ROOT>/.claude/... is internal to this distribution and is always checked.
        if (not verify_project_root) and (not rel.startswith('.claude/')):
            return None, 'skip_project'
        p = (project_root / rel).resolve()
        return (p, 'ok') if p.exists() else (p, 'missing')

    # legacy: explicit repo-root paths
    if tok.startswith((".claude/", ".claude/")):
        p = (project_root / tok_norm).resolve()
        return (p, 'ok') if p.exists() else (p, 'missing')

    # default: .claude-root-relative
    p = (claude_root / tok_norm).resolve()
    if p.exists():
        return p, "ok"

    # legacy compatibility: if token has no slash, try to locate by filename
    if "/" not in tok_norm:
        # common legacy placement
        for candidate in [
            claude_root / "tasks" / tok_norm,
            claude_root / "governance" / tok_norm,
            claude_root / "agents" / tok_norm,
            claude_root / "tools" / tok_norm,
            claude_root / "tools" / "skills" / tok_norm,
        ]:
            if candidate.exists():
                return candidate.resolve(), "ok"

        # as a last resort, search within .claude for a unique match by filename
        m, n = _unique_match(claude_root, tok_norm)
        if m is not None:
            return m.resolve(), "ok"
        if n > 1:
            return None, f"ambiguous:{n}"

    return p, "missing"

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    claude_root = Path(inputs.get("claude_root", ".claude")).resolve()
    project_root = Path(inputs.get("project_root", ".")).resolve()
    scan_root = Path(inputs.get("scan_root", str(claude_root))).resolve()

    md_files = list(scan_root.rglob("*.md"))
    missing: list[dict] = []
    ambiguous: list[dict] = []
    checked = 0
    skipped = 0
    skipped_evidence = 0
    skipped_project = 0

    for md in md_files:
        text = md.read_text(encoding="utf-8", errors="ignore")
        for tok in _iter_backtick_tokens(text):
            if not _is_pathish(tok, verify_legacy=bool(inputs.get("verify_legacy", False))):
                continue
            resolved, note = _resolve(tok, claude_root=claude_root, project_root=project_root, verify_project_root=bool(inputs.get('verify_project_root', False)))
            if note == "skip_evidence":
                skipped += 1
                skipped_evidence += 1
                continue
            if note == "skip_project":
                skipped += 1
                skipped_project += 1
                continue
            checked += 1
            if note.startswith("ambiguous"):
                ambiguous.append({
                    "file": str(md.relative_to(project_root)) if md.is_relative_to(project_root) else str(md),
                    "token": tok,
                    "note": note,
                })
                continue
            if resolved is not None and not resolved.exists():
                missing.append({
                    "file": str(md.relative_to(project_root)) if md.is_relative_to(project_root) else str(md),
                    "token": tok,
                    "resolved": str(resolved),
                })

    status = "ok" if not missing else "fail"
    warnings = []
    if ambiguous:
        warnings.append(f"Ambiguous filename refs: {len(ambiguous)}")

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "doc_ssot_resolver"),
        "status": status,
        "outputs": {
            "scan_root": str(scan_root),
            "missing": missing,
            "ambiguous": ambiguous,
        },
        "metrics": {
            "markdown_files": len(md_files),
            "checked_tokens": checked,
            "skipped_tokens": skipped,
            "skipped_evidence": skipped_evidence,
            "skipped_project": skipped_project,
            "missing_count": len(missing),
            "ambiguous_count": len(ambiguous),
        },
        "errors": [f"Missing referenced paths: {len(missing)}"] if missing else [],
        "warnings": warnings,
    }