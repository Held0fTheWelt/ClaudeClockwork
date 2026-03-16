#!/usr/bin/env python3
"""
telemetry_summarize.py — Aggregate and summarize telemetry events across all JSONL files.

Skill ID: telemetry_summarize
MVP:      CCW-MVP12 (Telemetry & Feedback Loop v1)

Inputs (via req["inputs"]):
  events_dir      str        Directory containing *.jsonl event files.
                             Default: ".claude-performance/events/"
  run_id_filter   str|null   If set, only include events where run_id == this value.
                             Default: None (all events included)
  group_by        list[str]  Fields to group by.
                             Default: ["role", "model"]
  top_n           int        Return top N groups (sorted by total_tokens desc).
                             Default: 10

Output:
  {
    "type": "telemetry_summary",
    "groups": [
      {
        "key": {"role": "...", "model": "..."},
        "total_tokens": N,
        "avg_tokens": N,
        "run_count": N,
        "total_cost_cents": N,
        "avg_quality_score": N   # null if no quality_score fields present
      }
    ],
    "totals": {
      "events": N,
      "total_tokens": N,
      "total_cost_cents": N
    },
    "period": {"from": "<iso>", "to": "<iso>"},
    "status": "ok" | "error",
    "error": "<message>"   # only on status: error
  }

Standalone usage:
  python3 tools/skills/telemetry_summarize.py '{
    "skill_id": "telemetry_summarize",
    "inputs": {
      "events_dir": ".claude-performance/events/",
      "group_by": ["role", "model"],
      "top_n": 10
    }
  }'
"""

from __future__ import annotations

import glob
import json
import sys
from collections import defaultdict
from datetime import timezone
from pathlib import Path

# --------------------------------------------------------------------------- #
# Helpers                                                                       #
# --------------------------------------------------------------------------- #

def _read_jsonl(path: Path) -> list[dict]:
    """Read a JSONL file, skipping malformed lines silently."""
    events = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return events
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except (json.JSONDecodeError, ValueError):
            continue
    return events


def _safe_number(value, default=0):
    """Coerce a value to a number; return default on failure."""
    if value is None:
        return default
    try:
        return type(default)(value)
    except (TypeError, ValueError):
        return default


def _group_key(event: dict, group_by: list[str]) -> tuple:
    """Build a hashable group key from an event's fields."""
    return tuple(str(event.get(field, "")) for field in group_by)


def _key_dict(key_tuple: tuple, group_by: list[str]) -> dict:
    """Reconstruct the key dict from a tuple and field names."""
    return dict(zip(group_by, key_tuple))


# --------------------------------------------------------------------------- #
# Core logic                                                                    #
# --------------------------------------------------------------------------- #

def _summarize(
    events_dir: str,
    run_id_filter: str | None,
    group_by: list[str],
    top_n: int,
) -> dict:
    events_path = Path(events_dir)

    # --- Collect all events ------------------------------------------------- #
    all_events: list[dict] = []
    pattern = str(events_path / "*.jsonl")
    for filepath in glob.glob(pattern):
        all_events.extend(_read_jsonl(Path(filepath)))

    # --- Filter by run_id --------------------------------------------------- #
    if run_id_filter:
        all_events = [e for e in all_events if str(e.get("run_id", "")) == run_id_filter]

    # --- Aggregate per group ------------------------------------------------ #
    # Accumulators: total_tokens, total_cost_cents, run_count, quality_scores
    group_tokens: dict[tuple, int] = defaultdict(int)
    group_cost_cents: dict[tuple, float] = defaultdict(float)
    group_run_count: dict[tuple, int] = defaultdict(int)
    group_quality: dict[tuple, list[float]] = defaultdict(list)

    timestamps: list[str] = []

    for event in all_events:
        ts = event.get("ts")
        if ts:
            timestamps.append(str(ts))

        key = _group_key(event, group_by)
        total_t = _safe_number(
            event.get("total_tokens",
                       _safe_number(event.get("prompt_tokens"), 0)
                       + _safe_number(event.get("completion_tokens"), 0)),
            default=0,
        )
        cost_c = _safe_number(event.get("estimated_cost_cents"), default=0.0)
        group_tokens[key] += total_t
        group_cost_cents[key] += cost_c
        group_run_count[key] += 1

        qs = event.get("quality_score")
        if qs is not None:
            try:
                group_quality[key].append(float(qs))
            except (TypeError, ValueError):
                pass

    # --- Build sorted group list -------------------------------------------- #
    all_keys = set(group_tokens.keys()) | set(group_run_count.keys())
    groups_raw = []
    for key in all_keys:
        rc = group_run_count[key]
        tt = group_tokens[key]
        avg_t = tt // rc if rc > 0 else 0
        cost = group_cost_cents[key]
        qs_list = group_quality.get(key, [])
        avg_qs = sum(qs_list) / len(qs_list) if qs_list else None
        groups_raw.append({
            "key": _key_dict(key, group_by),
            "total_tokens": tt,
            "avg_tokens": avg_t,
            "run_count": rc,
            "total_cost_cents": round(cost, 6),
            "avg_quality_score": round(avg_qs, 4) if avg_qs is not None else None,
        })

    # Sort by total_tokens descending, then take top_n
    groups_raw.sort(key=lambda g: g["total_tokens"], reverse=True)
    groups = groups_raw[:top_n]

    # --- Overall totals ----------------------------------------------------- #
    total_events = len(all_events)
    total_tokens_all = sum(g["total_tokens"] for g in groups_raw)
    total_cost_all = round(sum(g["total_cost_cents"] for g in groups_raw), 6)

    # --- Period ------------------------------------------------------------- #
    timestamps_sorted = sorted(timestamps)
    period = {
        "from": timestamps_sorted[0] if timestamps_sorted else "",
        "to": timestamps_sorted[-1] if timestamps_sorted else "",
    }

    return {
        "type": "telemetry_summary",
        "groups": groups,
        "totals": {
            "events": total_events,
            "total_tokens": total_tokens_all,
            "total_cost_cents": total_cost_all,
        },
        "period": period,
        "status": "ok",
    }


# --------------------------------------------------------------------------- #
# Skill entrypoint                                                               #
# --------------------------------------------------------------------------- #

def run(req: dict) -> dict:
    """Skill entrypoint — called by skill_runner.py."""
    inputs = req.get("inputs") or {}
    events_dir = str(inputs.get("events_dir", ".claude-performance/events/"))
    run_id_filter = inputs.get("run_id_filter") or None
    group_by = list(inputs.get("group_by", ["role", "model"]))
    top_n = int(inputs.get("top_n", 10))

    try:
        result = _summarize(
            events_dir=events_dir,
            run_id_filter=run_id_filter,
            group_by=group_by,
            top_n=top_n,
        )
    except Exception as exc:  # noqa: BLE001
        result = {
            "type": "telemetry_summary",
            "groups": [],
            "totals": {"events": 0, "total_tokens": 0, "total_cost_cents": 0},
            "period": {"from": "", "to": ""},
            "status": "error",
            "error": str(exc),
        }

    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": "telemetry_summarize",
        "status": result["status"],
        "outputs": result,
        "errors": [result.get("error", "")] if result["status"] == "error" else [],
        "warnings": [],
        "metrics": result.get("totals", {}),
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
