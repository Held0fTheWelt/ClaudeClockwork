#!/usr/bin/env python3
"""
run_agent_step.py

Unified "Agent Step Wrapper" to:
1) run an agent/action command
2) collect lightweight telemetry
3) append ONE token event line to `.claude-performance/events/<run_id>.jsonl`

It does NOT call LLMs. It only runs a command and logs.

Typical usage:
  python .claude/tools/run_agent_step.py \
    --run-id run-20260301-001 \
    --role Write \
    --model llama3.3:70b-instruct-q5_K_M \
    --task implement_budget_skill \
    --phase write \
    -- -- your-command --args

Token attribution options:
- Best: the command outputs token usage (prompt/completion/total) and we parse it.
- Or: provide --prompt-tokens/--completion-tokens/--total-tokens explicitly.
- Or: point --tokens-file to a JSON file that contains usage fields.

If performance budgeting is disabled via `.claude/config/performance_budgeting.yaml`, logging is skipped unless --force-log is used.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

TOKEN_RX = {
    "prompt_tokens": re.compile(r'(?i)\bprompt[_\s-]*tokens?\b\s*[:=]\s*(\d+)'),
    "completion_tokens": re.compile(r'(?i)\b(completion|output)[_\s-]*tokens?\b\s*[:=]\s*(\d+)'),
    "total_tokens": re.compile(r'(?i)\b(total|all)[_\s-]*tokens?\b\s*[:=]\s*(\d+)'),
    "tokens": re.compile(r'(?i)\btokens?\b\s*[:=]\s*(\d+)'),
}


# Patterns for Claude Code summary line:
# e.g. "Done (48 tool uses · 65.2k tokens · 4m 23s)"
TOOL_USES_RX = re.compile(r'(?i)\b(\d+)\s*tool\s+uses\b')
TOKENS_K_RX = re.compile(r'(?i)\b([0-9]+(?:\.[0-9]+)?)\s*([km])\s*tokens\b')
DURATION_RX = re.compile(r'(?i)\b(\d+)\s*m\s*(\d+)\s*s\b')

def _parse_claude_summary(text: str) -> tuple[int,int,float,str]:
    # returns (tool_uses, total_tokens, duration_sec, note)
    tu = 0
    tt = 0
    ds = 0.0
    note = ""
    m = TOOL_USES_RX.search(text)
    if m:
        tu = int(m.group(1))
    m = TOKENS_K_RX.search(text)
    if m:
        val = float(m.group(1))
        suf = m.group(2).lower()
        tt = int(val * (1000 if suf == "k" else 1_000_000))
    m = DURATION_RX.search(text)
    if m:
        mins = int(m.group(1))
        secs = int(m.group(2))
        ds = float(mins*60 + secs)
    if tu or tt or ds:
        note = "parsed_claude_summary"
    return tu, tt, ds, note

def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def _load_json_maybe(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None

def _load_perf_cfg(cfg_path: Path) -> dict:
    if not cfg_path.exists():
        return {"enabled": True, "include_self_costs": True}
    try:
        return json.loads(cfg_path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        # JSON-in-YAML expected; if parse fails, fail open but warn
        return {"enabled": True, "include_self_costs": True, "_parse_error": True}

def _import_event_logger(root: Path):
    """
    Import `.claude/tools/skills/_event_logger.py` by file path.
    """
    import importlib.util
    mod_path = (root / ".claude/tools/skills/_event_logger.py").resolve()
    spec = importlib.util.spec_from_file_location("_event_logger", mod_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod

def _resolve_run_id(run_id: Optional[str]) -> str:
    if run_id:
        return run_id
    # fallback: environment, else timestamp-based
    rid = os.getenv("CLOCKWORK_RUN_ID")
    if rid:
        return rid
    return "run-" + datetime.utcnow().strftime("%Y%m%d-%H%M%S")

def _parse_tokens_from_text(text: str) -> Tuple[int,int,int,str]:
    """
    Returns (prompt, completion, total, note)
    """
    pt = ct = tt = None

    m = TOKEN_RX["prompt_tokens"].search(text)
    if m:
        pt = int(m.group(1))

    m = TOKEN_RX["completion_tokens"].search(text)
    if m:
        # group can be 2 depending on regex
        ct = int(m.group(2)) if m.lastindex and m.lastindex >= 2 else int(m.group(1))

    m = TOKEN_RX["total_tokens"].search(text)
    if m:
        tt = int(m.group(2)) if m.lastindex and m.lastindex >= 2 else int(m.group(1))

    if tt is None:
        m = TOKEN_RX["tokens"].search(text)
        if m:
            tt = int(m.group(1))

    note = ""
    if pt is None and ct is None and tt is None:
        return 0, 0, 0, "tokens_unavailable"
    if tt is None:
        tt = (pt or 0) + (ct or 0)
        note = "total_tokens_derived"
    return pt or 0, ct or 0, tt, note

def _parse_tokens_from_obj(obj: Any) -> Tuple[int,int,int,str]:
    """
    Attempt to parse OpenAI/Claude-like usage objects.
    """
    if not isinstance(obj, dict):
        return 0,0,0,"tokens_unavailable"
    # common shapes
    usage = obj.get("usage") if isinstance(obj.get("usage"), dict) else obj
    pt = usage.get("prompt_tokens") or usage.get("input_tokens") or 0
    ct = usage.get("completion_tokens") or usage.get("output_tokens") or 0
    tt = usage.get("total_tokens") or usage.get("tokens") or 0
    try:
        pt = int(pt)
    except Exception:
        pt = 0
    try:
        ct = int(ct)
    except Exception:
        ct = 0
    try:
        tt = int(tt)
    except Exception:
        tt = pt + ct
        return pt, ct, tt, "total_tokens_derived"
    if tt == 0 and (pt or ct):
        tt = pt + ct
        return pt, ct, tt, "total_tokens_derived"
    if tt == 0 and pt == 0 and ct == 0:
        return 0,0,0,"tokens_unavailable"
    return pt, ct, tt, ""

def _write_step_artifacts(run_id: str, slug: str, stdout: str, stderr: str, meta: dict) -> Path:
    base = Path(".claude-performance/steps") / run_id / slug
    base.mkdir(parents=True, exist_ok=True)
    (base / "stdout.txt").write_text(stdout, encoding="utf-8", errors="ignore")
    (base / "stderr.txt").write_text(stderr, encoding="utf-8", errors="ignore")
    (base / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return base

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--role", default=os.getenv("CLOCKWORK_ROLE", "unknown"))
    ap.add_argument("--model", default=os.getenv("CLOCKWORK_MODEL", "unknown"))
    ap.add_argument("--task", default=os.getenv("CLOCKWORK_TASK", "unknown"))
    ap.add_argument("--phase", default=os.getenv("CLOCKWORK_PHASE", ""))
    ap.add_argument("--notes", default=os.getenv("CLOCKWORK_NOTES", ""))
    ap.add_argument("--config", default=".claude/config/performance_budgeting.yaml")
    ap.add_argument("--events-file", default=None)
    ap.add_argument("--tokens-file", default=None, help="Optional JSON file containing token usage fields.")
    ap.add_argument("--prompt-tokens", type=int, default=None)
    ap.add_argument("--completion-tokens", type=int, default=None)
    ap.add_argument("--total-tokens", type=int, default=None)
    ap.add_argument("--force-log", action="store_true", help="Log even if performance budgeting disabled.")
    ap.add_argument("--no-parse", action="store_true", help="Do not parse tokens from output.")
    ap.add_argument("--no-artifacts", action="store_true", help="Do not write stdout/stderr artifacts.")
    ap.add_argument("--timeout", type=int, default=None)
    ap.add_argument("--", dest="cmd_sep", action="store_true")  # placeholder
    ap.add_argument("cmd", nargs=argparse.REMAINDER)

    args = ap.parse_args()

    run_id = _resolve_run_id(args.run_id)
    cfg_path = Path(args.config).resolve()
    cfg = _load_perf_cfg(cfg_path)
    enabled = bool(cfg.get("enabled", True))
    include_self = bool(cfg.get("include_self_costs", True))

    # command after '--' might include leading '--'
    cmd = args.cmd
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        print("[run_agent_step] No command provided. Use: ... -- <command>", file=sys.stderr)
        return 2

    # run the command
    start = datetime.utcnow()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print("[run_agent_step] command timed out", file=sys.stderr)
        return 124

    end = datetime.utcnow()
    dur_ms = int((end - start).total_seconds() * 1000)

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    rc = int(proc.returncode)

    # tokens from explicit args first
    pt = args.prompt_tokens
    ct = args.completion_tokens
    tt = args.total_tokens
    token_note = ""

    if pt is None and ct is None and tt is None:
        # tokens file
        if args.tokens_file:
            obj = _load_json_maybe(Path(args.tokens_file).resolve())
            if obj is not None:
                pt2, ct2, tt2, note2 = _parse_tokens_from_obj(obj)
                pt, ct, tt, token_note = pt2, ct2, tt2, note2

    if pt is None and ct is None and tt is None and not args.no_parse:
        # parse output for tokens
        combined = stdout + "\n" + stderr
        pt2, ct2, tt2, note2 = _parse_tokens_from_text(combined)
        pt, ct, tt, token_note = pt2, ct2, tt2, note2

        # Also parse Claude Code summary line if present
        tu2, tt2, ds2, note2 = _parse_claude_summary(combined)
        if tu2:
            # store tool uses in notes (and later in event)
            pass
        if tt == 0 and tt2:
            tt = tt2
        if note2:
            args.notes = (args.notes + " | " if args.notes else "") + note2

    if pt is None: pt = 0
    if ct is None: ct = 0
    if tt is None: tt = pt + ct
    if token_note:
        args.notes = (args.notes + " | " if args.notes else "") + token_note

    # write artifacts (always helpful for traceability)
    slug = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    meta = {
        "run_id": run_id,
        "role": args.role,
        "model": args.model,
        "task": args.task,
        "phase": args.phase,
        "returncode": rc,
        "duration_ms": dur_ms,
        "cmd": cmd,
        "timestamp": _now_iso(),
    }
    artifacts_dir = None
    if not args.no_artifacts:
        artifacts_dir = _write_step_artifacts(run_id, slug, stdout, stderr, meta)

    # logging decision
    should_log = (enabled and include_self) or args.force_log
    if not should_log:
        # still print a short summary
        print(f"[run_agent_step] rc={rc} duration_ms={dur_ms} (budgeting disabled; no event logged)")
        if artifacts_dir:
            print(f"[run_agent_step] artifacts: {artifacts_dir}")
        # forward stdout/stderr to caller (optional)
        if stdout.strip():
            print(stdout)
        if stderr.strip():
            print(stderr, file=sys.stderr)
        return rc

    # append event
    try:
        root = Path(".").resolve()
        elog = _import_event_logger(root)
        events_file = elog.resolve_events_file(run_id, args.events_file)
        event = {
            "ts": _now_iso(),
            "run_id": run_id,
            "role": args.role,
            "model": args.model,
            "task": args.task,
            "phase": args.phase,
            "prompt_tokens": int(pt),
            "completion_tokens": int(ct),
            "total_tokens": int(tt),
            "tool_uses": int(tu2) if "tu2" in locals() else 0,
            "duration_sec": float(ds2) if "ds2" in locals() else float(dur_ms)/1000.0,
            "notes": args.notes,
        }
        elog.append_event(event, events_file)
        print(f"[run_agent_step] logged event -> {events_file} | role={args.role} task={args.task} tokens={tt} rc={rc} dur_ms={dur_ms}")
        if artifacts_dir:
            print(f"[run_agent_step] artifacts: {artifacts_dir}")
    except Exception as e:
        print(f"[run_agent_step] failed to log event: {e}", file=sys.stderr)

    # forward output
    if stdout.strip():
        print(stdout)
    if stderr.strip():
        print(stderr, file=sys.stderr)

    return rc

if __name__ == "__main__":
    raise SystemExit(main())
