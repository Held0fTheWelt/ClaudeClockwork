#!/usr/bin/env python3
"""doc_write

Deterministic file writer for documentation.

This skill does **not** generate prose. It persists *already prepared* content
(typically drafted by an LLM/agent) into one or multiple files, and emits a
reviewable unified diff against any existing content.
"""

from __future__ import annotations

import difflib
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _safe_join(project_root: Path, rel_path: str) -> Path:
    # Normalize and prevent path traversal
    rel = Path(rel_path)
    if rel.is_absolute():
        raise ValueError(f"target path must be relative: {rel_path}")
    target = (project_root / rel).resolve()
    pr = project_root.resolve()
    if target == pr or pr not in target.parents:
        raise ValueError(f"refusing to write outside project_root: {rel_path}")
    return target


def _unified_diff(old: str, new: str, fromfile: str, tofile: str, context: int = 3) -> str:
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=fromfile,
            tofile=tofile,
            n=context,
        )
    )


@dataclass
class _WriteResult:
    path: str
    created: bool
    bytes_written: int
    sha256_before: str
    sha256_after: str
    diff: str


def _write_one(project_root: Path, item: dict[str, Any], default_overwrite: bool, dry_run: bool) -> _WriteResult:
    rel_path = item.get("path")
    if not rel_path or not isinstance(rel_path, str):
        raise ValueError("files[].path must be a non-empty string")
    content = item.get("content")
    if content is None or not isinstance(content, str):
        raise ValueError(f"files[].content must be a string (path={rel_path})")

    overwrite = bool(item.get("overwrite", default_overwrite))
    target = _safe_join(project_root, rel_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    existed = target.exists()
    old = target.read_text(encoding="utf-8") if existed else ""
    if existed and (not overwrite) and old != content:
        raise ValueError(f"refusing to overwrite existing file without overwrite=true: {rel_path}")

    diff = _unified_diff(old, content, fromfile=f"a/{rel_path}", tofile=f"b/{rel_path}")
    before_b = old.encode("utf-8")
    after_b = content.encode("utf-8")

    if not dry_run:
        target.write_text(content, encoding="utf-8")

    return _WriteResult(
        path=rel_path,
        created=not existed,
        bytes_written=len(after_b),
        sha256_before=_sha256_bytes(before_b),
        sha256_after=_sha256_bytes(after_b),
        diff=diff,
    )


def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    project_root = Path(inputs.get("project_root", ".")).resolve()

    # Single-file convenience:
    # {path: "docs/user/guide.md", content: "..."}
    files = inputs.get("files")
    if files is None:
        p = inputs.get("path")
        c = inputs.get("content")
        if p is not None or c is not None:
            files = [{"path": p, "content": c, "overwrite": inputs.get("overwrite", True)}]

    if not isinstance(files, list) or not files:
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": req.get("skill_id", "doc_write"),
            "status": "fail",
            "outputs": {},
            "metrics": {},
            "errors": ["inputs.files must be a non-empty list, or provide inputs.path + inputs.content"],
            "warnings": [],
        }

    default_overwrite = bool(inputs.get("overwrite", True))
    dry_run = bool(inputs.get("dry_run", False))
    max_diff_chars = int(inputs.get("max_diff_chars", 50_000))

    written = []
    diffs = {}
    warnings = []
    total_bytes = 0
    created_count = 0

    try:
        for item in files:
            r = _write_one(project_root, item, default_overwrite, dry_run)
            written.append({
                "path": r.path,
                "created": r.created,
                "bytes": r.bytes_written,
                "sha256_before": r.sha256_before,
                "sha256_after": r.sha256_after,
            })
            total_bytes += r.bytes_written
            created_count += 1 if r.created else 0

            d = r.diff
            if len(d) > max_diff_chars:
                diffs[r.path] = d[:max_diff_chars] + "\n... (diff truncated)\n"
                warnings.append(f"Diff truncated for {r.path}")
            else:
                diffs[r.path] = d

    except Exception as e:
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": req.get("skill_id", "doc_write"),
            "status": "fail",
            "outputs": {"written": written},
            "metrics": {"written": len(written), "bytes": total_bytes},
            "errors": [str(e)],
            "warnings": warnings,
        }

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "doc_write"),
        "status": "ok",
        "outputs": {
            "project_root": str(project_root),
            "dry_run": dry_run,
            "written": written,
            "diffs": diffs,
        },
        "metrics": {
            "files": len(written),
            "created": created_count,
            "bytes": total_bytes,
            "diff_truncated": sum(1 for w in warnings if "Diff truncated" in w),
        },
        "errors": [],
        "warnings": warnings,
    }
