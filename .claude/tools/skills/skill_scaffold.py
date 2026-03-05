#!/usr/bin/env python3
"""skill_scaffold

Scaffold a new skill/tool (tool+schema+example+task+registry).

Interface: run(req: dict) -> SkillResultSpec
- Reads req["inputs"]
- Writes optional markdown to inputs["output_path"]

Deterministic local-file tool. No network.
"""

from __future__ import annotations

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

def _sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()

def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def _list_files(root: Path, include_ext: Optional[List[str]] = None) -> List[Path]:
    out: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {'.git','.svn','.hg','__pycache__','.pytest_cache','node_modules','.venv'}]
        for fn in filenames:
            p = Path(dirpath) / fn
            if include_ext and p.suffix.lower() not in include_ext:
                continue
            out.append(p)
    return out

def _ok(req: dict, outputs: dict, warnings: Optional[List[str]] = None, metrics: Optional[dict] = None) -> dict:
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", ""),
        "status": "ok",
        "outputs": outputs,
        "errors": [],
        "warnings": warnings or [],
        "metrics": metrics or {},
    }

def _fail(req: dict, errors: List[str], warnings: Optional[List[str]] = None, metrics: Optional[dict] = None) -> dict:
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", ""),
        "status": "fail",
        "outputs": {},
        "errors": errors,
        "warnings": warnings or [],
        "metrics": metrics or {},
    }
def _find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(25):
        if (cur / ".claude").is_dir():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start.resolve()

def run(req: dict) -> dict:
    try:
        inputs=req.get("inputs", {})
        repo_root = Path(inputs.get("repo_root") or _find_repo_root(Path.cwd())).resolve()
        skill_name = str(inputs.get("skill_name") or "").strip()
        description = str(inputs.get("description") or "").strip()
        if not skill_name or not re.match(r"^[a-z][a-z0-9_]+$", skill_name):
            return _fail(req, ["inputs.skill_name must be snake_case starting with a letter"])
        if not description:
            return _fail(req, ["inputs.description is required"])

        dry_run=bool(inputs.get("dry_run", True))
        task_id=int(inputs.get("task_id") or 90)

        tool_path = repo_root / ".claude" / "tools" / "skills" / f"{skill_name}.py"
        schema_path = repo_root / ".claude" / "contracts" / "schemas" / f"{skill_name}_spec.json"
        example_path = repo_root / ".claude" / "contracts" / "examples" / f"{skill_name}_example.json"
        task_path = repo_root / ".claude" / "tasks" / "skills" / f"{task_id:03d}_{skill_name.upper()}.md"
        registry_path = repo_root / ".claude" / "skills" / "registry.md"

        collisions=[str(p) for p in [tool_path, schema_path, example_path, task_path] if p.exists()]
        if collisions:
            return _fail(req, ["collision: some files already exist"], warnings=collisions)

        desc_escaped = description.replace('"','\\"')

        tool_lines = [
            "#!/usr/bin/env python3",
            f'"""{skill_name}',
            "",
            description,
            "",
            "Deterministic local-file tool. No network.",
            '"""',
            "",
            "from __future__ import annotations",
            "",
            "import os",
            "from pathlib import Path",
            "from typing import Any, Dict",
            "",
            "def _write_text(path: Path, content: str) -> None:",
            "    path.parent.mkdir(parents=True, exist_ok=True)",
            "    path.write_text(content, encoding=\"utf-8\")",
            "",
            "def run(req: dict) -> dict:",
            "    inputs = req.get(\"inputs\", {})",
            "    outputs = {",
            f'        \"skill\": \"{skill_name}\",',
            f'        \"description\": \"{desc_escaped}\",',
            "        \"inputs\": inputs,",
            "        \"notes\": [\"Implement deterministic logic here.\"]",
            "    }",
            "    out_path = inputs.get(\"output_path\")",
            "    if out_path:",
            "        _write_text(Path(out_path), \"# Report\\n\\nTODO\\n\")",
            "        outputs[\"output_path\"] = out_path",
            "    return {",
            "        \"type\": \"skill_result_spec\",",
            "        \"request_id\": req.get(\"request_id\", \"\"),",
            "        \"skill_id\": req.get(\"skill_id\", \"\"),",
            "        \"status\": \"ok\",",
            "        \"outputs\": outputs,",
            "        \"errors\": [],",
            "        \"warnings\": [],",
            "        \"metrics\": {},",
            "    }",
            "",
        ]
        tool_text = "\n".join(tool_lines)

        schema = inputs.get("schema") or {}
        props = schema.get("properties") if isinstance(schema, dict) else None
        if not props:
            props = {
                "root": {"type":"string", "description":"Root directory"},
                "output_path": {"type":"string", "description":"Optional markdown report path"},
                "dry_run": {"type":"boolean", "description":"Do not modify files"},
            }
        json_schema = {"type":"object","required":["root"],"properties":props}
        example = inputs.get("example") or {"root":"./", "output_path": f"docs/{skill_name}_report.md", "dry_run": True}

        task_md = "\n".join([
            f"# Task: {skill_name}",
            "",
            "## Goal",
            description,
            "",
            "## Run",
            f"Tool: `{skill_name}`",
            f"Schema: `.claude/contracts/schemas/{skill_name}_spec.json`",
            f"Example: `.claude/contracts/examples/{skill_name}_example.json`",
            "",
            "## Output",
            "- JSON report",
            "- Optional markdown at `output_path`",
            "",
        ])

        registry_entry = f"- {skill_name} — {description}"

        planned = {
            "repo_root": str(repo_root),
            "tool": str(tool_path),
            "schema": str(schema_path),
            "example": str(example_path),
            "task": str(task_path),
            "registry_path": str(registry_path),
            "registry_entry": registry_entry,
        }

        if dry_run:
            return _ok(req, {"dry_run": True, "planned": planned})

        tool_path.parent.mkdir(parents=True, exist_ok=True)
        schema_path.parent.mkdir(parents=True, exist_ok=True)
        example_path.parent.mkdir(parents=True, exist_ok=True)
        task_path.parent.mkdir(parents=True, exist_ok=True)

        tool_path.write_text(tool_text, encoding="utf-8")
        schema_path.write_text(json.dumps(json_schema, indent=2), encoding="utf-8")
        example_path.write_text(json.dumps(example, indent=2), encoding="utf-8")
        task_path.write_text(task_md, encoding="utf-8")

        if registry_path.exists():
            reg = registry_path.read_text(encoding="utf-8", errors="replace").rstrip() + "\n" + registry_entry + "\n"
        else:
            reg = "# Skills Registry\n\n" + registry_entry + "\n"
        registry_path.write_text(reg, encoding="utf-8")

        return _ok(req, {"dry_run": False, "written": planned})
    except Exception as e:
        return _fail(req, [f"Unhandled error: {e!r}"])
