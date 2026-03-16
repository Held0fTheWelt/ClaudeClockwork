#!/usr/bin/env python3
from __future__ import annotations
import re

def _score(headline: str, constraints: list[str]) -> int:
    h = headline.lower()
    score = 50
    # Reward tool-first, determinism, cost-saving, validation
    for kw, pts in [("tool",10),("determin",10),("skill",8),("cheap",6),("cost",6),("validate",8),("evidence",6)]:
        if kw in h:
            score += pts
    # Penalize risky/huge
    for kw, pts in [("rewrite",-12),("massive",-10),("everything",-10),("overhaul",-10)]:
        if kw in h:
            score += pts
    # Constraint matching reward
    for c in constraints:
        c = c.lower()
        if "tool" in c and "tool" in h:
            score += 6
        if "max" in c and "task" in c and "plan" in h:
            score += 4
    return max(0, min(100, score))

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    ideas = inputs.get("ideas", [])
    constraints = inputs.get("constraints", [])
    if not isinstance(ideas, list) or not ideas:
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),
                "skill_id":"idea_scoring","status":"fail","outputs":{},
                "metrics":{}, "errors":["inputs.ideas must be a non-empty list"], "warnings":[]}

    scored=[]
    for i, idea in enumerate(ideas):
        headline = idea.get("headline") if isinstance(idea, dict) else str(idea)
        s = _score(headline, constraints if isinstance(constraints,list) else [])
        scored.append({"index": i, "headline": headline, "score": s})
    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[:inputs.get("top_n", 5)]
    return {"type":"skill_result_spec","request_id":req.get("request_id",""),
            "skill_id":"idea_scoring","status":"ok",
            "outputs":{"top": top, "all_count": len(scored)},
            "metrics":{"all": len(scored), "top": len(top)},
            "errors":[], "warnings":[]}
