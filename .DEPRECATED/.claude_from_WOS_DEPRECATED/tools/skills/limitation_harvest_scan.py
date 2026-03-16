#!/usr/bin/env python3
from __future__ import annotations

import fnmatch
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

TEXT_EXT = {".md",".py",".json",".yml",".yaml",".txt"}

SCAN_LIMITATIONS = [
    "This is heuristic extraction; it cannot infer every 'expected' feature a human might assume.",
    "It prefers explicit statements (not implemented / non-goal / future work).",
    "It does not execute code; it cannot verify runtime behavior.",
    "Dynamic/implicit capabilities might be missed if not documented."
]

# English + German markers
LIMIT_RX = re.compile(r"(?i)\b(limitations?|limits?|boundaries|grenzen|limitierungen)\b")
NONGOAL_RX = re.compile(r"(?i)\b(non-?goals?|not\s+goal|nicht-?ziele|nichtziele|kein\s+ziel|out\s+of\s+scope|au[sß]erhalb\s+des\s+umfangs)\b")
FUTURE_RX = re.compile(r"(?i)\b(future\s+work|future|roadmap|thinkable|denkbar|m[öo]glich(?:keiten)?|sp[äa]ter|not\s+yet|noch\s+nicht|todo)\b")
MISSING_RX = re.compile(r"(?i)\b(not\s+implemented|not\s+supported|unsupported|missing|does\s+not\s+exist|not\s+available|noch\s+nicht\s+implementiert|nicht\s+implementiert|nicht\s+unterst[üu]tzt)\b")
PLACEHOLDER_RX = re.compile(r"(?i)\b(placeholder|stub)\b")

TASK_SKILL_RX = re.compile(r"^#\s*Skill Task:\s*([a-zA-Z0-9_]+)", re.MULTILINE)
REG_SKILL_RX = re.compile(r"^###\s+\d+\)\s+([a-zA-Z0-9_]+)\s*$", re.MULTILINE)
SKILL_MAP_RX = re.compile(r'^\s*"([a-zA-Z0-9_]+)"\s*:\s*([a-zA-Z0-9_]+)\s*,\s*$', re.MULTILINE)

def _snippet(text: str, start: int, end: int, max_chars: int) -> str:
    s = max(0, start - 80)
    e = min(len(text), end + 80)
    sn = text[s:e].replace("\n"," ").strip()
    if len(sn) > max_chars:
        sn = sn[:max_chars-1] + "…"
    return sn

def _match_globs(rel: str, globs: List[str]) -> bool:
    rel = rel.replace("\\","/")
    return any(fnmatch.fnmatch(rel, g) for g in globs)

def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")

def _collect_hits(p: Path, max_snip: int):
    txt = _read_text(p)
    hits = []
    for rx, kind in [
        (LIMIT_RX, "limit"),
        (NONGOAL_RX, "nongoal"),
        (FUTURE_RX, "future"),
        (MISSING_RX, "missing"),
        (PLACEHOLDER_RX, "placeholder"),
    ]:
        for m in rx.finditer(txt):
            hits.append((kind, m.start(), m.end(), _snippet(txt, m.start(), m.end(), max_snip)))
    return txt, hits

def _unimplemented_skills(root: Path) -> Tuple[List[str], List[dict]]:
    # skills declared in tasks but missing tool file or missing mapping
    tasks_dir = root/".claude/tasks/skills"
    tools_dir = root/".claude/tools/skills"
    sr_path = tools_dir/"skill_runner.py"
    registry_path = root/".claude/skills/registry.md"

    tool_ids = {p.stem for p in tools_dir.glob("*.py") if p.name != "skill_runner.py"}
    sr_text = sr_path.read_text(encoding="utf-8", errors="ignore") if sr_path.exists() else ""
    mapped = set(SKILL_MAP_RX.findall(sr_text))
    # mapped returns list of tuples (key, value) but regex captures both; we'll use key
    mapped_ids = {k for k, v in mapped}

    reg_text = registry_path.read_text(encoding="utf-8", errors="ignore") if registry_path.exists() else ""
    reg_ids = set(REG_SKILL_RX.findall(reg_text))

    missing = set()
    evidence = []

    # from tasks
    if tasks_dir.exists():
        for p in tasks_dir.glob("*.md"):
            txt = p.read_text(encoding="utf-8", errors="ignore")
            m = TASK_SKILL_RX.search(txt)
            if not m:
                continue
            sid = m.group(1).strip()
            if sid not in tool_ids:
                missing.add(sid)
                evidence.append({"path": str(p.relative_to(root)), "snippet": f"Task exists for {sid}, but tool missing: tools/skills/{sid}.py"})
            elif sid not in mapped_ids:
                missing.add(sid)
                evidence.append({"path": str(p.relative_to(root)), "snippet": f"Tool exists for {sid}, but not mapped in skill_runner SKILLS."})

    # from registry
    for sid in reg_ids:
        if sid == "skill_runner":
            continue
        if sid not in tool_ids:
            missing.add(sid)
            evidence.append({"path": ".claude/skills/registry.md", "snippet": f"Registry lists {sid}, but tool missing: tools/skills/{sid}.py"})
        elif sid not in mapped_ids:
            missing.add(sid)
            evidence.append({"path": ".claude/skills/registry.md", "snippet": f"Registry lists {sid}, but not mapped in skill_runner SKILLS."})

    return sorted(missing), evidence

def _write_report_files(report_dir: Path, report: dict, md: str):
    report_dir.mkdir(parents=True, exist_ok=True)
    ts = report["generated_at"].replace(":","").replace("-","")
    j = report_dir/f"limitation_harvest_report_{ts}.json"
    m = report_dir/f"limitation_harvest_report_{ts}.md"
    j.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    m.write_text(md, encoding="utf-8")
    return str(j), str(m)

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}
    root = Path(inputs.get("root",".")).resolve()
    scan_roots = inputs.get("scan_roots") or [
        ".claude/skills",".claude/tasks",".claude/tools/skills",".claude/governance",".claude/policies"
    ]
    max_files = int(inputs.get("max_files", 5000))
    max_snip = int(inputs.get("max_snippet_chars", 220))
    write_reports = bool(inputs.get("write_reports", True))
    report_dir = (root / (inputs.get("report_dir") or ".clockwork_runtime/knowledge/writes/limitation_harvest")).resolve()

    warnings = []
    sources = []
    limitations = []
    non_goals = []
    future_work = []
    expected = []

    # Scan text files for explicit statements (cheap, deterministic)
    scanned = 0
    for sr in scan_roots:
        base = (root/sr).resolve()
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if scanned >= max_files:
                warnings.append(f"max_files reached ({max_files}); scan truncated")
                break
            if not p.is_file():
                continue
            if p.suffix.lower() not in TEXT_EXT:
                continue
            rel = str(p.relative_to(root))
            sources.append(rel)
            scanned += 1
            txt, hits = _collect_hits(p, max_snip)
            # categorize: prefer heading contexts by simple line window
            for kind, s, e, sn in hits:
                ev = [{"path": rel, "snippet": sn}]
                if kind == "limit":
                    limitations.append({"text": sn, "evidence": ev})
                elif kind == "nongoal":
                    non_goals.append({"text": sn, "evidence": ev})
                elif kind == "future":
                    future_work.append({"text": sn, "evidence": ev})
                elif kind in ("missing","placeholder"):
                    expected.append({
                        "item": sn,
                        "category":"missing_capability",
                        "reason":"Explicit marker suggests expected-but-missing or placeholder content.",
                        "confidence":"medium" if kind=="missing" else "low",
                        "evidence": ev
                    })

    # Unimplemented skills / integration gaps
    missing_skills, miss_ev = _unimplemented_skills(root)
    for sid in missing_skills:
        ev = [e for e in miss_ev if sid in e["snippet"]]
        expected.append({
            "item": sid,
            "category":"unimplemented_skill",
            "reason":"Skill referenced by tasks/registry but missing tool implementation or mapping.",
            "confidence":"high",
            "evidence": ev[:6]
        })

    # De-duplicate expected list by item+category
    uniq = {}
    for it in expected:
        key = (it["item"], it["category"])
        if key not in uniq:
            uniq[key] = it
        else:
            # merge evidence
            uniq[key]["evidence"].extend(it.get("evidence", []))
            uniq[key]["evidence"] = uniq[key]["evidence"][:8]
    expected = list(uniq.values())

    now = __import__("datetime").datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    report = {
        "type":"limitation_harvest_report",
        "generated_at": now,
        "root": str(root),
        "sources_scanned": sources,
        "expected_but_missing": expected,
        "limitations": limitations,
        "non_goals": non_goals,
        "future_work": future_work,
        "unimplemented_skills": missing_skills,
        "warnings": warnings,
        "limitations_of_scan": SCAN_LIMITATIONS,
    }

    # Markdown summary focusing on "Writer-ready" sections
    md = []
    md.append("# Limitation Harvest Report")
    md.append(f"- Generated: `{now}`")
    md.append(f"- Scanned sources: **{len(sources)}** files")
    md.append("")
    md.append("## Expected-but-missing (Writer-ready)")
    md.append(f"Items: **{len(expected)}**")
    for it in sorted(expected, key=lambda x: (x["category"], x["confidence"]), reverse=False)[:200]:
        md.append(f"- **{it['category']}** / {it['confidence']}: `{it['item']}`")
        md.append(f"  - Reason: {it['reason']}")
        for ev in it.get("evidence", [])[:3]:
            md.append(f"  - Evidence: `{ev['path']}` — `{ev['snippet']}`")
    md.append("")
    md.append("## Limitierungen (explicit markers)")
    md.append(f"Count: **{len(limitations)}**")
    for it in limitations[:120]:
        md.append(f"- `{it['text']}` ({it['evidence'][0]['path']})")
    md.append("")
    md.append("## Nicht-Ziele (explicit markers)")
    md.append(f"Count: **{len(non_goals)}**")
    for it in non_goals[:120]:
        md.append(f"- `{it['text']}` ({it['evidence'][0]['path']})")
    md.append("")
    md.append("## Denkbar / Future Work (explicit markers)")
    md.append(f"Count: **{len(future_work)}**")
    for it in future_work[:120]:
        md.append(f"- `{it['text']}` ({it['evidence'][0]['path']})")
    md.append("")
    md.append("## Limitations of this scan")
    for lim in SCAN_LIMITATIONS:
        md.append(f"- {lim}")
    md_text = "\n".join(md) + "\n"

    out_json_path = None
    out_md_path = None
    if write_reports:
        out_json_path, out_md_path = _write_report_files(report_dir, report, md_text)

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id":"limitation_harvest_scan",
        "status":"ok",
        "outputs":{
            "report": report,
            "report_json_path": out_json_path,
            "report_md_path": out_md_path
        },
        "errors": [],
        "warnings": warnings,
        "metrics":{
            "files_scanned": len(sources),
            "expected_but_missing": len(expected),
            "unimplemented_skills": len(missing_skills),
            "limit_markers": len(limitations),
            "nongoal_markers": len(non_goals),
            "future_markers": len(future_work),
        }
    }
