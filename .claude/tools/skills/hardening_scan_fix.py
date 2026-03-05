#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import fnmatch
from pathlib import Path
from typing import List, Dict, Any

DEFAULT_LIMITATIONS = [
    "Hardening is still heuristic; it can detect drift patterns but cannot guarantee perfect correctness.",
    "Apply mode edits files; always review a report first.",
    "Some inconsistencies are design choices; keep decisions in the brain store to avoid flip-flopping."
]

TEXT_EXT = {".md",".py",".json",".yml",".yaml",".txt"}

JUNK_GLOBS = ["**/__pycache__/**","**/*.pyc","**/.pytest_cache/**","**/.mypy_cache/**","**/.ruff_cache/**","**/.DS_Store","**/Thumbs.db"]

def _is_junk(rel: str) -> bool:
    rel = rel.replace("\\","/")
    for g in JUNK_GLOBS:
        if fnmatch.fnmatch(rel, g):
            return True
    return False

def _load_json(p: Path, default: Any):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def _save_json(p: Path, obj: Any):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def _append_jsonl(p: Path, obj: Any):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def _load_addons_map(p: Path) -> dict:
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

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}
    root = Path(inputs.get("root",".")).resolve()
    apply_fixes = bool(inputs.get("apply_fixes", False))
    scenarios = inputs.get("scenarios") or ["scan_inconsistencies"]

    brain_path = (root / (inputs.get("brain_path") or ".llama_runtime/brain/decisions.json")).resolve()
    brain_log_path = (root / (inputs.get("brain_log_path") or ".llama_runtime/brain/decisions.jsonl")).resolve()

    findings = []
    fixes = []
    warnings = []
    brain_updates = []

    brain = _load_json(brain_path, {"decisions": {}, "notes": []})

    def decide(key: str, value: Any, note: str):
        # Brain: persist stable decisions
        prev = brain["decisions"].get(key)
        if prev != value:
            brain["decisions"][key] = value
            brain_updates.append(f"{key}={value}")
            _append_jsonl(brain_log_path, {"ts": __import__("datetime").datetime.utcnow().isoformat()+"Z", "key": key, "value": value, "note": note})

    # Scenario: scan_inconsistencies
    if "scan_inconsistencies" in scenarios:
        # 1) detect `.oodle/` references (should be zero)
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(root).as_posix()
            if rel.startswith(".llama_runtime/writes/") or rel.startswith(".llama_runtime/knowledge/writes/") or rel.startswith(".claude/knowledge/-Writes/") or rel.startswith(".claude/_archive/"):
                continue
            if _is_junk(rel):
                findings.append({"kind":"junk_in_repo","path":rel,"details":"Cache artifact present in tree (should be cleaned before archiving).","severity":"warn"})
                continue
            if p.suffix.lower() in TEXT_EXT:
                txt = p.read_text(encoding="utf-8", errors="ignore")
                if ".oodle/" in txt or ".oodle/runtime" in txt:
                    findings.append({"kind":"legacy_oodle_ref","path":rel,"details":"Contains obsolete .oodle path reference.","severity":"error"})

        # 2) registry vs tools/skills mapping drift
        reg = root/".claude/skills/registry.md"
        if reg.exists():
            reg_text = reg.read_text(encoding="utf-8", errors="ignore")
            reg_ids = re.findall(r"^###\s+\d+\)\s+([a-zA-Z0-9_]+)\s*$", reg_text, flags=re.MULTILINE)
            tools = root/".claude/tools/skills"
            tool_ids = [p.stem for p in tools.glob("*.py") if p.name != "skill_runner.py"]
            missing_tool = sorted([sid for sid in reg_ids if sid not in tool_ids and sid != "skill_runner"])
            if missing_tool:
                findings.append({"kind":"registry_without_tool","path":str(reg.relative_to(root)),"details":f"Registry lists skills without tool implementation: {missing_tool[:30]}","severity":"warn"})
            unregistered_tool = sorted([sid for sid in tool_ids if sid not in set(reg_ids)])
            if unregistered_tool:
                findings.append({"kind":"tool_without_registry","path":str(tools.relative_to(root)),"details":f"Tools exist without registry entry: {unregistered_tool[:30]}","severity":"warn"})

    # Scenario: purge_oodle_refs
    if "purge_oodle_refs" in scenarios:
        decide("legacy_policy.oodle", "purge_all", "User requested complete elimination of .oodle references.")
        repl = {
            ".oodle/runtime": ".llama_runtime/writes",
            ".oodle/": ".claude/",
        }
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(root).as_posix()
            if rel.startswith(".llama_runtime/writes/") or rel.startswith(".llama_runtime/knowledge/writes/") or rel.startswith(".claude/knowledge/-Writes/") or rel.startswith(".claude/_archive/"):
                continue
            if p.suffix.lower() not in TEXT_EXT:
                continue
            txt = p.read_text(encoding="utf-8", errors="ignore")
            if ".oodle/" not in txt and ".oodle/runtime" not in txt:
                continue
            new = txt
            for k, v in repl.items():
                new = new.replace(k, v)
            if new != txt:
                action = "replace .oodle paths"
                if apply_fixes:
                    p.write_text(new, encoding="utf-8")
                    fixes.append({"kind":"purge_oodle_refs","path":rel,"action":action,"status":"applied","message":"replaced"})
                else:
                    fixes.append({"kind":"purge_oodle_refs","path":rel,"action":action,"status":"planned","message":"dry-run"})

    # Scenario: validate_addon_boundaries
    if "validate_addon_boundaries" in scenarios:
        addons_map_path = root/".claude/addons/map.yaml"
        addons_map = _load_addons_map(addons_map_path) if addons_map_path.exists() else {"core": [], "addons": {}}
        tools = root/".claude/tools/skills"
        tool_ids = [p.stem for p in tools.glob("*.py") if p.name != "skill_runner.py"]
        unclassified = []
        for sid in tool_ids:
            if _pack_for(sid, addons_map) == "unclassified":
                unclassified.append(sid)
        if unclassified:
            findings.append({"kind":"addon_boundary_missing","path":str(addons_map_path.relative_to(root)),"details":f"Unclassified skills in addons/map.yaml: {unclassified}", "severity":"warn"})
            if apply_fixes:
                # auto-classify into meta_doc_ops
                addons_map.setdefault("addons", {}).setdefault("meta_doc_ops", [])
                for sid in unclassified:
                    addons_map["addons"]["meta_doc_ops"].append(sid)
                addons_map["addons"]["meta_doc_ops"] = sorted(list(set(addons_map["addons"]["meta_doc_ops"])))
                _save_json(addons_map_path, addons_map)
                fixes.append({"kind":"validate_addon_boundaries","path":str(addons_map_path.relative_to(root)),"action":"auto-classify unclassified into addon:meta_doc_ops","status":"applied","message":"updated addons/map.yaml"})
            else:
                fixes.append({"kind":"validate_addon_boundaries","path":str(addons_map_path.relative_to(root)),"action":"auto-classify unclassified into addon:meta_doc_ops","status":"planned","message":"dry-run"})





    # Scenario: validate_performance_budgeting
    if "validate_performance_budgeting" in scenarios:
        cfg_path = root/".claude/config/performance_budgeting.yaml"
        if not cfg_path.exists():
            findings.append({"kind":"perf_config_missing","path":".claude/config/performance_budgeting.yaml","details":"Performance budgeting config missing; budgeting cannot be toggled properly.", "severity":"warn"})
        else:
            try:
                cfg = json.loads(cfg_path.read_text(encoding="utf-8", errors="ignore"))
                if "enabled" not in cfg:
                    findings.append({"kind":"perf_config_invalid","path":str(cfg_path.relative_to(root)),"details":"Config missing 'enabled' flag.", "severity":"warn"})
            except Exception:
                findings.append({"kind":"perf_config_parse_error","path":str(cfg_path.relative_to(root)),"details":"Config is not valid JSON (JSON-in-YAML expected).", "severity":"warn"})

    # Scenario: enforce_src_origin_rule
    if "enforce_src_origin_rule" in scenarios:
        decide("layout_policy.product_code_root", "src", "User requires all product code under src/.")
        src_dir = root/"src"
        if not src_dir.exists():
            findings.append({"kind":"src_missing","path":"src/","details":"src/ does not exist. Create it as the single origin for product code.", "severity":"warn"})
        # flag code-like files outside src (excluding .claude, .claude-performance, tools, docs)
        code_ext = {".py",".js",".ts",".tsx",".jsx",".cpp",".c",".h",".hpp",".cs",".go",".rs",".java",".kt",".swift",".uplugin",".uproject",".ini",".cfg"}
        exclude_prefix = (".claude/","\.claude-performance/","\.git/","node_modules/","dist/","build/","\.venv/","venv/")
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(root).as_posix()
            if rel.startswith(".claude/") or rel.startswith(".claude-performance/") or rel.startswith(".git/"):
                continue
            if rel.startswith("src/"):
                continue
            if p.suffix.lower() in code_ext or p.name.endswith((".uplugin",".uproject")):
                findings.append({"kind":"code_outside_src","path":rel,"details":"Product code file outside src/. Move under src/ to comply with SRC_ORIGIN_RULE.", "severity":"warn"})

    # Scenario: ensure_autodocs
    if "ensure_autodocs" in scenarios:
        decide("docs_policy.autodocs", "required", "User requested Auto-Docs for all skills.")
        if apply_fixes:
            # call autodocs_generate by importing its run() if available
            try:
                import importlib.util
                auto_path = root/".claude/tools/skills/autodocs_generate.py"
                spec = importlib.util.spec_from_file_location("autodocs_generate", auto_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)  # type: ignore
                auto_req = {
                    "type":"skill_request_spec",
                    "request_id": req.get("request_id","") + ":autodocs",
                    "skill_id":"autodocs_generate",
                    "inputs":{
                        "root": str(root),
                        "skills_tools_dir": ".claude/tools/skills",
                        "skills_docs_dir": ".claude/skills",
                        "registry_path": ".claude/skills/registry.md",
                        "addons_map_path": ".claude/addons/map.yaml",
                        "mode": "write_missing_only",
                        "max_chars": 3500
                    }
                }
                res = mod.run(auto_req)
                fixes.append({"kind":"ensure_autodocs","path":".claude/skills/","action":"generate missing per-skill docs","status":"applied","message":f"written={res.get('outputs',{}).get('report',{}).get('written',[])[:5]}..."})
            except Exception as e:
                fixes.append({"kind":"ensure_autodocs","path":".claude/tools/skills/autodocs_generate.py","action":"invoke autodocs_generate","status":"failed","message":str(e)})
        else:
            fixes.append({"kind":"ensure_autodocs","path":".claude/skills/","action":"generate missing per-skill docs","status":"planned","message":"dry-run"})

    # persist brain
    if brain_updates:
        _save_json(brain_path, brain)

    now = __import__("datetime").datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    report = {
        "type":"hardening_report",
        "generated_at": now,
        "scenarios": scenarios,
        "findings": findings,
        "fixes": fixes,
        "brain_updates": brain_updates,
        "warnings": warnings,
        "limitations": DEFAULT_LIMITATIONS
    }

    out_dir = root/".llama_runtime/writes/hardening"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir/f"hardening_report_{now.replace(':','').replace('-','')}.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id":"hardening_scan_fix",
        "status":"ok",
        "outputs":{"report": report, "report_json_path": str(out_path), "brain_path": str(brain_path)},
        "errors": [],
        "warnings": warnings,
        "metrics":{"findings": len(findings), "fixes": len(fixes), "brain_updates": len(brain_updates)}
    }
