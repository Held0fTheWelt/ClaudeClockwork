#!/usr/bin/env python3
"""
review_panel.py — Consolidate multi-reviewer verdicts into a single panel result.

Skill ID: review_panel
MVP:      CCW-MVP12 (Telemetry & Feedback Loop v1)

Inputs (via req["inputs"]):
  reviews         list   Each review is:
                           {
                             "reviewer": str,
                             "role":     "worker" | "team_lead" | "judge",
                             "verdict":  "pass" | "warn" | "fail",
                             "score":    float [0.0–1.0],
                             "notes":    str
                           }
  task_ref        str    Reference to the task/artifact being reviewed.
  consolidation   str    "majority" | "unanimous" | "weighted"  (default: "majority")
                         majority:   verdict = most common verdict across all reviewers
                                     (tie-break order: fail > warn > pass)
                         unanimous:  pass only if every reviewer says pass;
                                     any warn → warn; any fail → fail
                         weighted:   worker=0.3, team_lead=0.5, judge=0.2 on scores;
                                     weighted_score >= 0.6 → pass,
                                     0.4 <= weighted_score < 0.6 → warn,
                                     weighted_score < 0.4 → fail

Output:
  {
    "type":               "review_panel_result",
    "task_ref":           str,
    "final_verdict":      "pass" | "warn" | "fail",
    "confidence":         float,   # [0.0–1.0]
    "individual_reviews": [...],   # copy of input reviews (normalized)
    "dissenting":         [str],   # reviewer names that differ from final_verdict
    "recommendations":    [str],   # aggregated from notes of warn/fail reviewers
    "status":             "ok" | "error",
    "error":              str      # only on error
  }

Standalone usage:
  python3 tools/skills/review_panel.py '{
    "skill_id": "review_panel",
    "inputs": {
      "task_ref": "mvp12-schema-review",
      "consolidation": "majority",
      "reviews": [
        {"reviewer": "alice", "role": "worker",    "verdict": "pass", "score": 0.9, "notes": ""},
        {"reviewer": "bob",   "role": "team_lead", "verdict": "warn", "score": 0.6, "notes": "Missing edge-case tests"},
        {"reviewer": "carol", "role": "judge",     "verdict": "pass", "score": 0.8, "notes": ""}
      ]
    }
  }'
"""

from __future__ import annotations

import json
import sys
from collections import Counter

# --------------------------------------------------------------------------- #
# Constants                                                                     #
# --------------------------------------------------------------------------- #

ROLE_WEIGHTS: dict[str, float] = {
    "worker": 0.3,
    "team_lead": 0.5,
    "judge": 0.2,
}

# Tie-break severity (higher = wins on tie)
VERDICT_SEVERITY: dict[str, int] = {
    "fail": 2,
    "warn": 1,
    "pass": 0,
}

WEIGHTED_PASS_THRESHOLD = 0.6
WEIGHTED_WARN_THRESHOLD = 0.4


# --------------------------------------------------------------------------- #
# Consolidation strategies                                                      #
# --------------------------------------------------------------------------- #

def _consolidate_majority(reviews: list[dict]) -> tuple[str, float]:
    """Most common verdict wins; ties resolved by severity (fail > warn > pass).

    Returns (final_verdict, confidence).
    confidence = fraction of reviewers agreeing with final verdict.
    """
    if not reviews:
        return "warn", 0.0

    counts: Counter = Counter(r["verdict"] for r in reviews)
    max_count = max(counts.values())
    # All verdicts that share the max count
    candidates = [v for v, c in counts.items() if c == max_count]
    # Pick the most severe among tied candidates
    final = max(candidates, key=lambda v: VERDICT_SEVERITY.get(v, 0))
    confidence = round(max_count / len(reviews), 4)
    return final, confidence


def _consolidate_unanimous(reviews: list[dict]) -> tuple[str, float]:
    """pass only if all reviewers say pass; any warn → warn; any fail → fail.

    Returns (final_verdict, confidence).
    confidence = fraction of reviewers in agreement (all pass or all fail).
    """
    if not reviews:
        return "warn", 0.0

    verdicts = [r["verdict"] for r in reviews]
    if all(v == "pass" for v in verdicts):
        return "pass", 1.0
    if any(v == "fail" for v in verdicts):
        final = "fail"
    else:
        final = "warn"
    agreeing = sum(1 for v in verdicts if v == final)
    confidence = round(agreeing / len(reviews), 4)
    return final, confidence


def _consolidate_weighted(reviews: list[dict]) -> tuple[str, float]:
    """Weighted average score; thresholds: >=0.6 pass, 0.4–0.6 warn, <0.4 fail.

    Unknown roles receive weight 0.3 (same as worker).
    Returns (final_verdict, confidence = weighted_score).
    """
    if not reviews:
        return "warn", 0.0

    total_weight = 0.0
    weighted_score = 0.0

    for r in reviews:
        w = ROLE_WEIGHTS.get(r.get("role", ""), 0.3)
        score = float(r.get("score", 0.5))
        # Clamp score to [0.0, 1.0]
        score = max(0.0, min(1.0, score))
        weighted_score += w * score
        total_weight += w

    if total_weight == 0:
        return "warn", 0.0

    normalized = weighted_score / total_weight
    normalized = round(normalized, 4)

    if normalized >= WEIGHTED_PASS_THRESHOLD:
        verdict = "pass"
    elif normalized >= WEIGHTED_WARN_THRESHOLD:
        verdict = "warn"
    else:
        verdict = "fail"

    return verdict, normalized


# --------------------------------------------------------------------------- #
# Core logic                                                                    #
# --------------------------------------------------------------------------- #

def _normalize_review(raw: dict) -> dict:
    """Ensure review has all expected fields with sensible defaults."""
    verdict = str(raw.get("verdict", "warn")).lower()
    if verdict not in ("pass", "warn", "fail"):
        verdict = "warn"
    score = raw.get("score")
    try:
        score = max(0.0, min(1.0, float(score))) if score is not None else 0.5
    except (TypeError, ValueError):
        score = 0.5
    return {
        "reviewer": str(raw.get("reviewer", "")),
        "role": str(raw.get("role", "worker")).lower(),
        "verdict": verdict,
        "score": round(score, 4),
        "notes": str(raw.get("notes", "")),
    }


def _panel(
    reviews_raw: list[dict],
    task_ref: str,
    consolidation: str,
) -> dict:
    reviews = [_normalize_review(r) for r in reviews_raw]

    # Choose consolidation strategy
    strategy = consolidation.lower()
    if strategy == "majority":
        final_verdict, confidence = _consolidate_majority(reviews)
    elif strategy == "unanimous":
        final_verdict, confidence = _consolidate_unanimous(reviews)
    elif strategy == "weighted":
        final_verdict, confidence = _consolidate_weighted(reviews)
    else:
        # Unknown strategy: fall back to majority
        final_verdict, confidence = _consolidate_majority(reviews)

    # Find dissenting reviewers (those whose verdict differs from final)
    dissenting = [r["reviewer"] for r in reviews if r["verdict"] != final_verdict]

    # Collect recommendations from warn/fail reviewer notes
    recommendations: list[str] = []
    for r in reviews:
        if r["verdict"] in ("warn", "fail") and r["notes"].strip():
            note = r["notes"].strip()
            if note not in recommendations:
                recommendations.append(note)

    return {
        "type": "review_panel_result",
        "task_ref": task_ref,
        "final_verdict": final_verdict,
        "confidence": confidence,
        "individual_reviews": reviews,
        "dissenting": dissenting,
        "recommendations": recommendations,
        "status": "ok",
    }


# --------------------------------------------------------------------------- #
# Skill entrypoint                                                               #
# --------------------------------------------------------------------------- #

def run(req: dict) -> dict:
    """Skill entrypoint — called by skill_runner.py."""
    inputs = req.get("inputs") or {}
    reviews_raw = list(inputs.get("reviews", []))
    task_ref = str(inputs.get("task_ref", ""))
    consolidation = str(inputs.get("consolidation", "majority"))

    try:
        result = _panel(
            reviews_raw=reviews_raw,
            task_ref=task_ref,
            consolidation=consolidation,
        )
    except Exception as exc:  # noqa: BLE001
        result = {
            "type": "review_panel_result",
            "task_ref": task_ref,
            "final_verdict": "fail",
            "confidence": 0.0,
            "individual_reviews": [],
            "dissenting": [],
            "recommendations": [],
            "status": "error",
            "error": str(exc),
        }

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "review_panel",
        "status": result["status"],
        "outputs": result,
        "errors": [result.get("error", "")] if result["status"] == "error" else [],
        "warnings": [],
        "metrics": {
            "review_count": len(result.get("individual_reviews", [])),
            "dissenting_count": len(result.get("dissenting", [])),
            "final_verdict": result["final_verdict"],
            "confidence": result["confidence"],
        },
    }


# --------------------------------------------------------------------------- #
# Standalone CLI                                                                 #
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    if len(sys.argv) < 2:
        req_data: dict = {}
    else:
        try:
            req_data = json.loads(sys.argv[1])
        except (json.JSONDecodeError, ValueError) as e:
            print(json.dumps({"status": "error", "error": f"Invalid JSON input: {e}"}))
            sys.exit(1)

    output = run(req_data)
    print(json.dumps(output, indent=2, ensure_ascii=False))
