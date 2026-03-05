#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


def _first_nonempty_line(p: Path) -> str:
    try:
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            s = line.strip()
            if s:
                return s[:200]
    except Exception:
        return ""
    return ""


def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    claude_root = Path(inputs.get("claude_root", ".claude")).resolve()
    out_path = Path(inputs.get("out", "validation_runs/capability_map.json")).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    skills_dir = claude_root / "tools/skills"
    agents_dir = claude_root / "agents"

    skills = []
    for p in sorted(skills_dir.glob("*.py")):
        if p.name in {"__init__.py", "skill_runner.py"}:
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")
        # Only include true skills (must export run(req))
        if not re.search(r"^def\s+run\s*\(", txt, flags=re.M):
            continue
        skills.append({
            "skill_id": p.stem,
            "path": str(p.relative_to(claude_root)),
            "hint": _first_nonempty_line(p).lstrip("# "),
        })

    agents = [{"agent": p.stem, "path": str(p.relative_to(claude_root))} for p in sorted(agents_dir.rglob("*.md"))]

    schemas = [str(p.relative_to(claude_root)) for p in sorted((claude_root / "contracts/schemas").glob("*.json"))]
    examples = [str(p.relative_to(claude_root)) for p in sorted((claude_root / "contracts/examples").rglob("*.json"))]
    governance = [str(p.relative_to(claude_root)) for p in sorted((claude_root / "governance").glob("*.md"))]
    tasks = [str(p.relative_to(claude_root)) for p in sorted((claude_root / "tasks").rglob("*.md"))]

    manifest = {
        "type": "capability_map",
        "clock_root": ".claude",
        "skills": skills,
        "agents": agents,
        "contracts": {"schemas": schemas, "examples": examples},
        "governance": governance,
        "tasks": tasks,
    }

    out_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "capability_map_build"),
        "status": "ok",
        "outputs": {"out": str(out_path), "skills": len(skills), "agents": len(agents)},
        "metrics": {"skills": len(skills), "agents": len(agents), "schemas": len(schemas), "examples": len(examples), "tasks": len(tasks)},
        "errors": [],
        "warnings": [],
    }
