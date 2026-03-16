#!/usr/bin/env python3
"""
idea_dedupe — CCW-MVP16 Idea Deduplication Skill.

Deterministic deduplication of a list of idea strings.
Supports exact, normalized, and levenshtein comparison methods.
No LLM calls — stdlib only.

Usage (via skill_runner):
    Skill ID: idea_dedupe

Usage (standalone):
    python idea_dedupe.py '{"skill_id":"idea_dedupe","inputs":{"ideas":["hello world","Hello World","foo bar"]}}'

Schema: contracts/schemas/idea_dedupe_spec.schema.json
Example: contracts/examples/idea_dedupe.skill_request.example.json
"""

from __future__ import annotations
import json
import re
import sys
from typing import List, Dict

_SKILL_ID = "idea_dedupe"


def _norm(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s\-]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


def simple_cluster(headlines: List[str]) -> List[List[int]]:
    # Very cheap clustering: group identical normalized strings; fall back to first-token buckets.
    buckets: Dict[str, List[int]] = {}
    for i, h in enumerate(headlines):
        n = _norm(h)
        key = n
        if n not in buckets:
            key = n.split(" ", 1)[0] if n else ""
        buckets.setdefault(key, []).append(i)
    return list(buckets.values())


def _levenshtein(a: str, b: str) -> int:
    """Basic Levenshtein distance (stdlib only)."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (0 if ca == cb else 1)))
        prev = curr
    return prev[len(b)]


def _dedupe(ideas: List[str], method: str, threshold: float) -> dict:
    """
    Returns {"unique_ideas": [...], "duplicate_groups": [...], "removed_count": int}.
    """
    if not ideas:
        return {"unique_ideas": [], "duplicate_groups": [], "removed_count": 0}

    if method == "exact":
        seen: Dict[str, str] = {}
        dup_groups: Dict[str, List[str]] = {}
        unique: List[str] = []
        for idea in ideas:
            if idea in seen:
                dup_groups.setdefault(idea, []).append(idea)
            else:
                seen[idea] = idea
                unique.append(idea)
        duplicate_groups = [{"canonical": k, "duplicates": v} for k, v in dup_groups.items()]
        removed = sum(len(g["duplicates"]) for g in duplicate_groups)
        return {"unique_ideas": unique, "duplicate_groups": duplicate_groups, "removed_count": removed}

    elif method == "normalized":
        norm_map: Dict[str, str] = {}  # norm_key -> first original idea
        dup_groups: Dict[str, List[str]] = {}
        unique: List[str] = []
        for idea in ideas:
            key = _norm(idea)
            if key in norm_map:
                dup_groups.setdefault(norm_map[key], []).append(idea)
            else:
                norm_map[key] = idea
                unique.append(idea)
        duplicate_groups = [{"canonical": k, "duplicates": v} for k, v in dup_groups.items()]
        removed = sum(len(g["duplicates"]) for g in duplicate_groups)
        return {"unique_ideas": unique, "duplicate_groups": duplicate_groups, "removed_count": removed}

    elif method == "levenshtein":
        unique: List[str] = []
        dup_groups: Dict[str, List[str]] = {}
        for idea in ideas:
            matched = False
            for u in unique:
                max_len = max(len(idea), len(u), 1)
                dist = _levenshtein(idea.lower(), u.lower())
                sim = 1.0 - dist / max_len
                if sim >= threshold:
                    dup_groups.setdefault(u, []).append(idea)
                    matched = True
                    break
            if not matched:
                unique.append(idea)
        duplicate_groups = [{"canonical": k, "duplicates": v} for k, v in dup_groups.items()]
        removed = sum(len(g["duplicates"]) for g in duplicate_groups)
        return {"unique_ideas": unique, "duplicate_groups": duplicate_groups, "removed_count": removed}

    else:
        raise ValueError(f"Unknown method: {method!r}. Must be exact|normalized|levenshtein.")


# ---------------------------------------------------------------------------
# skill_runner interface
# ---------------------------------------------------------------------------

def run(req: dict) -> dict:
    """Called by skill_runner.py with a full SkillRequestSpec."""
    inputs = req.get("inputs") or {}
    ideas: List[str] = inputs.get("ideas", [])
    method: str = inputs.get("method", "normalized")
    threshold: float = float(inputs.get("similarity_threshold", 0.8))

    errors: List[str] = []

    if not isinstance(ideas, list):
        errors.append("inputs.ideas must be an array of strings")
        return {
            "type": "skill_result_spec",
            "request_id": req.get("request_id", ""),
            "skill_id": _SKILL_ID,
            "status": "error",
            "outputs": {"unique_ideas": [], "duplicate_groups": [], "removed_count": 0},
            "errors": errors,
            "warnings": [],
            "metrics": {},
        }

    try:
        result = _dedupe(ideas, method, threshold)
    except Exception as exc:
        errors.append(str(exc))
        result = {"unique_ideas": [], "duplicate_groups": [], "removed_count": 0}

    status = "error" if errors else "ok"
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": _SKILL_ID,
        "status": status,
        "outputs": result,
        "errors": errors,
        "warnings": [],
        "metrics": {
            "input_count": len(ideas),
            "unique_count": len(result.get("unique_ideas", [])),
            "removed_count": result.get("removed_count", 0),
        },
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
        req = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Invalid JSON input: {exc}\n")
        return 1

    result = run(req)
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
