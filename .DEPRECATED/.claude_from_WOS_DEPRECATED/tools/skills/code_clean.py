#!/usr/bin/env python3
"""
code_clean — CCW-MVP13 Cleaning Suite skill.

Scans Python files for code quality issues:
  - TODO/FIXME/HACK markers
  - Unused imports (heuristic: import X with no usage of X in file body)
  - Long functions (>100 lines)
  - Files with only comments/docstrings (no real code)
  - Stub files (body is only `pass` or placeholder comments)

Usage (standalone):
    python code_clean.py '{"skill_id":"code_clean","inputs":{"root":"llamacode","scan_only":true}}'
    echo '{"inputs":{"root":"."}}' | python code_clean.py

Usage (via skill_runner):
    The run(req) interface is called with a SkillRequestSpec dict.

Inputs:
    root       (str)  — directory to scan for .py files; default "."
    scan_only  (bool) — default True; set False only when write mode is implemented
    emit_plan  (bool) — default False; when True, add a "plan" field with suggested actions

Output (skill_result_spec):
    {
      "type": "skill_result_spec",
      "status": "ok",
      "outputs": {
        "findings": [
          {
            "category": "marker"|"stub"|"long_function"|"unused_import",
            "file": str,
            "line": int,
            "detail": str
          }
        ],
        "summary": {"files_scanned": N, "findings_total": N, "by_category": {...}},
        "scan_only": bool,
        "plan": [...]  # only present when emit_plan=True
      }
    }
"""

from __future__ import annotations

import ast
import collections
import json
import re
import sys
from pathlib import Path

_LIMITATIONS = [
    "scan_only=True by default — this skill never modifies the filesystem.",
    "Unused-import detection is heuristic: it checks whether the top-level name appears in the file text.",
    "Long-function detection counts physical lines (including blank lines and comments).",
    "Stub detection is conservative: only flags files whose entire body is `pass` or short placeholder text.",
    "Dynamic imports, exec(), and __import__() are not tracked.",
]

# Marker patterns
_MARKER_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("todo", re.compile(r"(?i)\bTODO\b")),
    ("fixme", re.compile(r"(?i)\bFIXME\b")),
    ("hack", re.compile(r"(?i)\bHACK\b")),
    ("xxx", re.compile(r"(?i)\bXXX\b")),
    ("placeholder", re.compile(r"(?i)\bplaceholder\b")),
]

_LONG_FUNCTION_LINES = 100
_EXCLUDE_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".tox"}


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------

def _collect_imports(tree: ast.Module) -> list[tuple[int, str, str]]:
    """
    Return list of (lineno, import_name, alias) for top-level imports.
    alias is the name used in the file (after `as`).
    """
    imports = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                used_name = alias.asname if alias.asname else alias.name.split(".")[0]
                imports.append((node.lineno, alias.name, used_name))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                used_name = alias.asname if alias.asname else alias.name
                imports.append((node.lineno, f"{node.module}.{alias.name}", used_name))
    return imports


def _collect_function_lengths(tree: ast.Module) -> list[tuple[int, str, int]]:
    """
    Return list of (lineno, func_name, line_count) for functions exceeding threshold.
    """
    long_funcs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if hasattr(node, "end_lineno") and node.end_lineno is not None:
                length = node.end_lineno - node.lineno + 1
                if length > _LONG_FUNCTION_LINES:
                    long_funcs.append((node.lineno, node.name, length))
    return long_funcs


def _is_stub(tree: ast.Module, text: str) -> bool:
    """
    Heuristic: file is a stub if the module body consists only of
    Expr(Constant(str)) (docstring), Pass, or Ellipsis nodes.
    """
    real_statements = 0
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue  # docstring
        if isinstance(node, ast.Pass):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and node.value.value is ...:
            continue  # Ellipsis
        real_statements += 1
    return real_statements == 0


# ---------------------------------------------------------------------------
# Single-file scan
# ---------------------------------------------------------------------------

def _scan_file(py_path: Path, root: Path) -> list[dict]:
    findings: list[dict] = []
    rel = str(py_path.relative_to(root))

    try:
        text = py_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return findings

    # ---- Marker scan (line by line) ----
    for lineno, line in enumerate(text.splitlines(), start=1):
        for cat, rx in _MARKER_PATTERNS:
            m = rx.search(line)
            if m:
                snippet = line.strip()[:120]
                findings.append({
                    "category": "marker",
                    "file": rel,
                    "line": lineno,
                    "detail": f"{cat.upper()}: {snippet}",
                })
                break  # one finding per line

    # ---- AST-based checks ----
    try:
        tree = ast.parse(text, filename=str(py_path))
    except SyntaxError:
        findings.append({
            "category": "marker",
            "file": rel,
            "line": 1,
            "detail": "SyntaxError: file could not be parsed",
        })
        return findings

    # Unused imports (heuristic)
    all_imports = _collect_imports(tree)
    for lineno, import_name, used_name in all_imports:
        # Strip the line itself from the check to avoid false negatives
        lines_without_import = [
            ln for i, ln in enumerate(text.splitlines(), start=1)
            if i != lineno
        ]
        body_text = "\n".join(lines_without_import)
        # Simple heuristic: does used_name appear as a word token in the rest?
        pattern = re.compile(r"\b" + re.escape(used_name) + r"\b")
        if not pattern.search(body_text):
            findings.append({
                "category": "unused_import",
                "file": rel,
                "line": lineno,
                "detail": f"import {import_name!r} (as {used_name!r}) may be unused",
            })

    # Long functions
    for lineno, func_name, line_count in _collect_function_lengths(tree):
        findings.append({
            "category": "long_function",
            "file": rel,
            "line": lineno,
            "detail": f"function {func_name!r} is {line_count} lines (threshold: {_LONG_FUNCTION_LINES})",
        })

    # Stub file
    if _is_stub(tree, text):
        findings.append({
            "category": "stub",
            "file": rel,
            "line": 1,
            "detail": "file body contains only stubs/pass/docstrings",
        })

    return findings


# ---------------------------------------------------------------------------
# skill_runner interface
# ---------------------------------------------------------------------------

def run(req: dict) -> dict:
    """Called by skill_runner.py with a full SkillRequestSpec."""
    inputs = req.get("inputs", {}) or {}
    root = Path(inputs.get("root", ".")).resolve()
    scan_only: bool = bool(inputs.get("scan_only", True))
    emit_plan: bool = bool(inputs.get("emit_plan", False))

    if not root.exists():
        return _error(req, f"root does not exist: {root}")

    def _is_excluded(p: Path) -> bool:
        try:
            parts = p.relative_to(root).parts
        except ValueError:
            return False
        return any(part in _EXCLUDE_DIRS for part in parts)

    all_findings: list[dict] = []
    files_scanned = 0

    for py_path in sorted(root.rglob("*.py")):
        if _is_excluded(py_path):
            continue
        files_scanned += 1
        all_findings.extend(_scan_file(py_path, root))

    # Summary
    by_category: dict[str, int] = collections.Counter(f["category"] for f in all_findings)
    summary = {
        "files_scanned": files_scanned,
        "findings_total": len(all_findings),
        "by_category": dict(by_category),
    }

    outputs: dict = {
        "findings": all_findings,
        "summary": summary,
        "scan_only": scan_only,
        "limitations": _LIMITATIONS,
    }

    if emit_plan:
        plan_ops = []
        for f in all_findings:
            if f["category"] == "stub":
                plan_ops.append({
                    "action": "review",
                    "file": f["file"],
                    "reason": "stub file — consider removing or implementing",
                })
            elif f["category"] == "unused_import":
                plan_ops.append({
                    "action": "remove_import",
                    "file": f["file"],
                    "line": f["line"],
                    "reason": f["detail"],
                })
            elif f["category"] == "long_function":
                plan_ops.append({
                    "action": "refactor",
                    "file": f["file"],
                    "line": f["line"],
                    "reason": f["detail"],
                })
            elif f["category"] == "marker":
                plan_ops.append({
                    "action": "resolve_marker",
                    "file": f["file"],
                    "line": f["line"],
                    "reason": f["detail"],
                })
        outputs["plan"] = plan_ops

    warnings: list[str] = []
    if not scan_only:
        warnings.append("scan_only=False passed but write mode is not yet implemented; treated as scan_only.")

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "code_clean",
        "status": "ok",
        "outputs": outputs,
        "errors": [],
        "warnings": warnings,
        "metrics": summary,
    }


def _error(req: dict, msg: str) -> dict:
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "code_clean",
        "status": "error",
        "outputs": {},
        "errors": [msg],
        "warnings": [],
        "metrics": {},
    }


# ---------------------------------------------------------------------------
# Standalone entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) >= 2:
        raw = sys.argv[1]
    else:
        raw = sys.stdin.read()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Invalid JSON input: {exc}\n")
        return 1

    if data.get("type") == "skill_request_spec" or data.get("skill_id") == "code_clean":
        result = run(data)
    else:
        result = run({"skill_id": "code_clean", "inputs": data})

    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
