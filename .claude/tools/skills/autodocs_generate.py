#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

DEFAULT_LIMITATIONS = [
    "This is deterministic scaffolding; it does not deeply understand semantics of code.",
    "It will not overwrite existing docs unless mode allows it.",
    "Registry parsing is heuristic (expects '### N) skill_id')."
]

REG_RX = re.compile(r"^###\s+\d+\)\s+([a-zA-Z0-9_]+)\s*$", re.MULTILINE)

def _load_addons_map(p: Path) -> dict:
    # map.yaml is stored as JSON for simplicity in this repo
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"core": [], "addons": {}}

def _pack_for(skill_id: str, addons_map: dict) -> str:
    if skill_id in (addons_map.get("core") or []):
        return "core"
    for pack, skills in (addons_map.get("addons") or {}).items():
        if skill_id in (skills or []):
            return f"addon:{pack}"
    return "unclassified"

def _registry_summary(reg_text: str, skill_id: str, max_len: int = 500) -> str:
    # naive: grab paragraph after heading until next heading
    m = re.search(rf"^###\s+\d+\)\s+{re.escape(skill_id)}\s*$", reg_text, flags=re.MULTILINE)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^###\s+\d+\)\s+", reg_text[start:], flags=re.MULTILINE)
    end = start + (nxt.start() if nxt else len(reg_text[start:]))
    block = reg_text[start:end].strip()
    block = re.sub(r"\n{3,}", "\n\n", block)
    if len(block) > max_len:
        block = block[:max_len].rstrip() + "…"
    return block

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}
    root = Path(inputs.get("root", ".")).resolve()
    tools_dir = (root / (inputs.get("skills_tools_dir") or ".claude/tools/skills")).resolve()
    docs_dir = (root / (inputs.get("skills_docs_dir") or ".claude/skills")).resolve()
    registry_path = (root / (inputs.get("registry_path") or ".claude/skills/registry.md")).resolve()
    addons_map_path = (root / (inputs.get("addons_map_path") or ".claude/addons/map.yaml")).resolve()
    mode = str(inputs.get("mode","write_missing_only"))
    max_chars = int(inputs.get("max_chars", 3500))

    warnings = []
    if not tools_dir.exists():
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),"skill_id":"autodocs_generate",
                "status":"error","outputs":{},"errors":[f"tools dir missing: {tools_dir}"],"warnings":[],
                "metrics":{}}

    reg_text = registry_path.read_text(encoding="utf-8", errors="ignore") if registry_path.exists() else ""
    addons_map = _load_addons_map(addons_map_path) if addons_map_path.exists() else {"core": [], "addons": {}}

    skill_files = sorted([p for p in tools_dir.glob("*.py") if p.name != "skill_runner.py"])
    skills_seen = [p.stem for p in skill_files]
    written, updated = [], []

    for sid in skills_seen:
        sdir = docs_dir / sid
        readme = sdir / "README.md"
        sdir.mkdir(parents=True, exist_ok=True)

        pack = _pack_for(sid, addons_map)
        summary = _registry_summary(reg_text, sid)
        if not summary:
            summary = "(No registry summary found. See registry.md for cataloging.)"

        body = f"""# {sid}

**Pack:** `{pack}`

## Purpose
{summary}

## Implementation
- Tool: `.claude/tools/skills/{sid}.py`
- Skill runner: `.claude/tools/skills/skill_runner.py`
- Contracts: `.claude/contracts/`

## Typical usage
```bash
python .claude/tools/skills/skill_runner.py --in <request.json> --out <result.json>
```

## Outputs
Describe output files and write locations here.

## Grenzen / Nicht-Ziele
- Deterministisch: keine semantische "Wahrheitsprüfung" über Inhalte.
- Kann Kandidatenlisten liefern, aber nicht beweisen, dass etwas obsolet ist.
- Wenn LLM-Verfeinerung nötig ist: nutze das passende Playbook (Explore/Write/Critic/DecideGap).
"""
        if len(body) > max_chars:
            body = body[:max_chars-100].rstrip() + "\n\n> (truncated)\n"

        if not readme.exists():
            readme.write_text(body, encoding="utf-8")
            written.append(str(readme.relative_to(root)))
        else:
            if mode in ("overwrite", "update_if_stub"):
                cur = readme.read_text(encoding="utf-8", errors="ignore")
                if mode == "overwrite" or cur.strip() in ("", "# "+sid, f"# {sid}"):
                    readme.write_text(body, encoding="utf-8")
                    updated.append(str(readme.relative_to(root)))

    now = __import__("datetime").datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    report = {
        "type":"autodocs_report",
        "generated_at": now,
        "skills_seen": skills_seen,
        "written": written,
        "updated": updated,
        "warnings": warnings,
        "limitations": DEFAULT_LIMITATIONS,
    }

    out_dir = root / ".llama_runtime/knowledge/writes/autodocs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"autodocs_report_{now.replace(':','').replace('-','')}.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id":"autodocs_generate",
        "status":"ok",
        "outputs":{"report": report, "report_json_path": str(out_path)},
        "errors": [],
        "warnings": warnings,
        "metrics":{"skills_seen": len(skills_seen), "written": len(written), "updated": len(updated)}
    }
