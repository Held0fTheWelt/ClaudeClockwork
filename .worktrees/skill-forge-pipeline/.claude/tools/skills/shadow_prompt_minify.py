#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Tuple

DEFAULT_LIMITATIONS = [
    "Deterministic minify cannot produce perfect machine-level prompts; use LLM refinement playbook if needed.",
    "Compression may remove helpful narrative context; always keep canonical rules and constraints.",
    "If your docs rely on implicit knowledge, the shadow version might be insufficient without additional constraints."
]

HEADING_RX = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
BULLET_RX = re.compile(r"^\s*[-*]\s+(.+)$", re.MULTILINE)

CANONICAL_HINTS = [
    "canonical", "must", "never", "always", "critical", "required", "do not",
    "acceptance criteria", "non-goals", "limitations", "boundaries", "security"
]

def _score_line(line: str) -> int:
    l = line.strip().lower()
    score = 0
    for h in CANONICAL_HINTS:
        if h in l:
            score += 2
    if l.startswith("#"):
        score += 2
    if l.startswith(("-", "*")):
        score += 1
    if "```" in l:
        score += 0
    if len(l) < 5:
        score -= 1
    return score

def _minify_markdown(text: str, max_chars: int) -> str:
    # Remove long code blocks but keep short command snippets
    out_lines = []
    in_code = False
    code_buf = []
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            if not in_code:
                block = "\n".join(code_buf).strip()
                code_buf = []
                if len(block) <= 900:
                    out_lines.append("```")
                    out_lines.extend(block.splitlines())
                    out_lines.append("```")
                else:
                    out_lines.append("```")
                    out_lines.append("# (code block omitted in shadow; see source doc)")
                    out_lines.append("```")
            continue
        if in_code:
            code_buf.append(line)
            continue
        out_lines.append(line)

    # Now pick the most important lines
    scored = [(i, _score_line(l), l) for i, l in enumerate(out_lines)]
    # Always keep headings + bullets + canonical hints
    keep = []
    for i, s, l in scored:
        if l.strip().startswith("#") or l.strip().startswith(("-", "*")):
            keep.append((i, l))
            continue
        ll = l.strip().lower()
        if any(h in ll for h in CANONICAL_HINTS):
            keep.append((i, l))
            continue

    # Deduplicate consecutive empties
    keep_sorted = [l for _, l in sorted(set(keep), key=lambda x: x[0])]
    compact = []
    prev_empty = False
    for l in keep_sorted:
        if not l.strip():
            if prev_empty:
                continue
            prev_empty = True
            compact.append("")
        else:
            prev_empty = False
            compact.append(l)

    # Ensure limitations section exists
    txt = "\n".join(compact).strip() + "\n"
    if "## Limit" not in txt and "## Grenzen" not in txt:
        txt += "\n## Limitierungen & Grenzen (Shadow)\n- Diese Shadow-Prompts sind komprimiert.\n- Für Details siehe die Source-Dokumente.\n- LLM-Refinement nach Playbook empfohlen für Perfektion.\n"

    # Truncate if needed
    if len(txt) > max_chars:
        txt = txt[:max_chars-200].rstrip() + "\n\n> (truncated)\n"
    return txt

def run(req: dict) -> dict:
    inputs = req.get("inputs", {}) or {}
    root = Path(inputs.get("root", ".")).resolve()
    source_docs = inputs.get("source_docs") or []
    shadow_root = Path(inputs.get("shadow_root", ".claude_shadow")).resolve()
    max_chars = int(inputs.get("max_chars_per_file", 6000))
    mode = inputs.get("mode", "deterministic_minify")

    warnings = []
    if not source_docs:
        return {
            "type":"skill_result_spec",
            "request_id": req.get("request_id",""),
            "skill_id":"shadow_prompt_minify",
            "status":"error",
            "outputs": {},
            "errors": ["source_docs is required"],
            "warnings": [],
            "metrics": {}
        }

    shadow_root.mkdir(parents=True, exist_ok=True)

    written = []
    index_lines = ["# .claude_shadow Index", "", f"- Mode: `{mode}`", ""]
    for sd in source_docs:
        sp = (root / sd).resolve()
        if not sp.exists():
            warnings.append(f"Missing source doc: {sd}")
            continue
        text = sp.read_text(encoding="utf-8", errors="ignore")
        minified = _minify_markdown(text, max_chars=max_chars)

        # Mirror name but in shadow root
        target_name = sd.replace("/", "__").replace("\\", "__")
        out_path = shadow_root / target_name
        out_path.write_text(minified, encoding="utf-8")
        written.append(str(out_path))
        index_lines.append(f"- `{target_name}`  ←  `{sd}`")

    index_path = shadow_root / "INDEX.md"
    index_path.write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    # Conservative gap score: deterministic-only starts lower
    gap_score = 68 if mode == "deterministic_minify" else 80
    biggest_gaps = [
        "No semantic reasoning (deterministic); cannot fully optimize instruction density.",
        "Cannot validate whether compressed prompts still cover all edge-cases.",
    ]
    next_actions = [
        "Run the Shadow Prompt Perfection Playbook (Explore/Write/Critic/DecideGap).",
        "Have a strong judge model score ambiguity and missing constraints.",
        "Iterate only on the delta patches to keep the shadow set short.",
    ]

    now = __import__("datetime").datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    report = {
        "type":"shadow_prompt_report",
        "generated_at": now,
        "inputs":{
            "source_docs": source_docs,
            "shadow_root": str(shadow_root),
            "max_chars_per_file": max_chars,
            "mode": mode,
        },
        "outputs":{
            "written_files": written,
            "index_path": str(index_path),
        },
        "quality_gap":{
            "score_0_100": gap_score,
            "biggest_gaps": biggest_gaps,
            "next_actions": next_actions,
        },
        "warnings": warnings,
        "limitations": DEFAULT_LIMITATIONS,
    }

    report_json = shadow_root / f"shadow_prompt_report_{now.replace(':','').replace('-','')}.json"
    report_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "type":"skill_result_spec",
        "request_id": req.get("request_id",""),
        "skill_id":"shadow_prompt_minify",
        "status":"ok",
        "outputs":{
            "report": report,
            "report_json_path": str(report_json),
        },
        "errors": [],
        "warnings": warnings,
        "metrics":{
            "source_docs": len(source_docs),
            "written_files": len(written),
        }
    }
