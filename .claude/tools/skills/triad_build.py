#!/usr/bin/env python3
from __future__ import annotations
import json, hashlib, time
from pathlib import Path

def _now_id(prefix: str="triad") -> str:
    return f"{prefix}-{int(time.time())}"

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})
    source_text = inputs.get("source_text","")
    source_lang = inputs.get("source_lang","de")
    primary_agent = inputs.get("primary_agent","personaler")
    mode = inputs.get("mode","balanced")
    max_words = int(inputs.get("max_words", 350))
    # Optional tighter char budget (useful for very small tasks)
    max_chars = inputs.get("max_chars")
    max_chars = int(max_chars) if max_chars is not None else None
    # Adaptive tightening: if the source is short, keep the brief short too
    if len(source_text) < 800:
        max_words = min(max_words, 200)
        if max_chars is not None:
            max_chars = min(max_chars, 1200)
    if len(source_text) < 300:
        max_words = min(max_words, 120)
        if max_chars is not None:
            max_chars = min(max_chars, 600)


    if not source_text:
        return {"type":"skill_result_spec","request_id":req.get("request_id",""),
                "skill_id":"triad_build","status":"fail","outputs":{},
                "metrics":{}, "errors":["inputs.source_text is required"], "warnings":[]}

    triad_id = inputs.get("triad_id") or _now_id()
    triad = {
      "type":"message_triad_spec",
      "triad_id": triad_id,
      "source": {"author":"user", "lang": source_lang, "text": source_text, "attachments": inputs.get("attachments", [])},
      # Translation/work_brief are optional and may be filled by a local Oodle translator step
      "translation": inputs.get("translation", {}),
      "work_brief": inputs.get("work_brief", {}),
      "context_pack": inputs.get("context_pack", {}),
      "fallback_policy": inputs.get("fallback_policy", {
          "fallback_order":["work_brief","translation","source"],
          "when_to_escalate_context":["blocked","ambiguity","repeat_failures>=2"],
          "max_reread_budget": 1
      })
    }

    # If no work_brief provided, create a minimal placeholder to avoid empty routing
    if not triad.get("work_brief"):
        triad["work_brief"] = {
          "lang":"en",
          "audience":{"primary_agent": primary_agent, "secondary_agents":[]},
          "mode": mode,
          "budget":{"max_words": max_words, "max_chars": max_chars, "allow_deep_oodle": False, "no_llm": False},
          "brief":{
            "goal":"(missing) Please create an English work brief from source/translation.",
            "context":[],
            "constraints":["Use Message Triad Protocol","Keep under max_words"],
            "tasks":[],
            "acceptance":[]
          }
        }

    return {"type":"skill_result_spec","request_id":req.get("request_id",""),
            "skill_id":"triad_build","status":"ok",
            "outputs":{"triad": triad},
            "metrics":{"has_translation": bool(triad.get("translation",{}).get("text")),
                       "has_work_brief": bool(triad.get("work_brief",{}).get("brief",{}).get("goal"))},
            "errors":[], "warnings":[]}
