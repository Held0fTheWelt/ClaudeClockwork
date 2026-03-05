#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

from doc_ssot_resolver import run as doc_ssot_resolver
from contract_drift_sentinel import run as contract_drift_sentinel

SKILL_HEADING_RE = re.compile(r"^###\s+\d+\)\s+([a-z0-9_\-]+)\s*$", re.IGNORECASE)


def _parse_registry(registry_path: Path) -> set[str]:
    ids: set[str] = set()
    for line in registry_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = SKILL_HEADING_RE.match(line.strip())
        if m:
            ids.add(m.group(1))
    return ids


def _parse_skill_runner(skill_runner_path: Path) -> set[str]:
    """
    Extract SKILLS keys from skill_runner.py reliably.

    We intentionally parse the `SKILLS = {...}` dict via AST to avoid false positives
    from other JSON-like dicts in the file.
    """
    import ast

    txt = skill_runner_path.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = ast.parse(txt)
    except SyntaxError:
        return set()

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "SKILLS":
                    if isinstance(node.value, ast.Dict):
                        keys: set[str] = set()
                        for k in node.value.keys:
                            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                                keys.add(k.value)
                            elif hasattr(ast, "Str") and isinstance(k, ast.Str):  # py<3.8
                                keys.add(k.s)
                        return keys
    return set()


def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    claude_root = Path(inputs.get("claude_root", ".claude")).resolve()

    registry = claude_root / "skills/registry.md"
    skill_runner = claude_root / "tools/skills/skill_runner.py"

    reg_ids = _parse_registry(registry) if registry.exists() else set()
    runner_ids = _parse_skill_runner(skill_runner) if skill_runner.exists() else set()

    missing_in_runner = sorted([x for x in reg_ids if x not in runner_ids])
    missing_in_registry = sorted([x for x in runner_ids if x not in reg_ids and x not in {"__init__"}])

    doc_res = doc_ssot_resolver({
        "type": "skill_request_spec",
        "skill_id": "doc_ssot_resolver",
        "request_id": "_",
        "inputs": {"claude_root": str(claude_root), "scan_root": str(claude_root), "project_root": str(Path(inputs.get("project_root", ".")).resolve()), "verify_project_root": bool(inputs.get("verify_project_root", False)), "verify_legacy": bool(inputs.get("verify_legacy", False))},
    })

    drift_res = contract_drift_sentinel({
        "type": "skill_request_spec",
        "skill_id": "contract_drift_sentinel",
        "request_id": "_",
        "inputs": {"root": str(claude_root)},
    })

    status = "ok" if (not missing_in_runner and doc_res.get("status") == "ok" and drift_res.get("status") == "ok") else "fail"

    errors = []
    if missing_in_runner:
        errors.append(f"Skills in registry missing in runner: {len(missing_in_runner)}")
    if doc_res.get("status") != "ok":
        errors.append("SSoT path references missing")
    if drift_res.get("status") != "ok":
        errors.append("Contract drift detected")

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "drift_semantic_check"),
        "status": status,
        "outputs": {
            "missing_in_runner": missing_in_runner,
            "missing_in_registry": missing_in_registry,
            "doc_ssot": doc_res.get("outputs", {}),
            "contract_drift": {
                "status": drift_res.get("status"),
                "outputs": drift_res.get("outputs", {}),
                "errors": drift_res.get("errors", []),
                "warnings": drift_res.get("warnings", []),
                "metrics": drift_res.get("metrics", {}),
            },
        },
        "metrics": {
            "missing_in_runner": len(missing_in_runner),
            "missing_in_registry": len(missing_in_registry),
            "doc_missing": len(doc_res.get("outputs", {}).get("missing", [])),
            "invalid_examples": drift_res.get("metrics", {}).get("invalid_examples", 0),
        },
        "errors": errors if status == "fail" else [],
        "warnings": [],
    }
