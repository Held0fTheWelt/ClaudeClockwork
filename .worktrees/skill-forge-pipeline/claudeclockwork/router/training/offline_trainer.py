"""Phase 31 — Offline trainer: read feedback/telemetry, update profiles, write snapshot. Guardrails block banned choices."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BANNED_CAPABILITIES: set[str] = set()  # Extend from capability policy (Phase 24)


def run_offline_training(
    runtime_root: Path | str,
    banned: set[str] | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    """
    Read feedback.jsonl and router_feedback.jsonl, aggregate success/trials per option.
    Apply guardrails: exclude banned capabilities from profile updates.
    Write new profile snapshot with version and timestamp. Deterministic when seed is set.
    """
    root = Path(runtime_root).resolve()
    banned = banned or BANNED_CAPABILITIES
    profiles: dict[str, dict[str, Any]] = {}

    # Router feedback (Phase 26)
    router_feedback = root / "router_feedback.jsonl"
    if router_feedback.is_file():
        with open(router_feedback, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                    oid = r.get("option_id", "")
                    if oid in banned:
                        continue
                    if oid not in profiles:
                        profiles[oid] = {"successes": 0, "trials": 0}
                    profiles[oid]["trials"] += 1
                    if r.get("success"):
                        profiles[oid]["successes"] += 1
                except json.JSONDecodeError:
                    pass

    # Telemetry feedback
    feedback_path = root / "telemetry" / "feedback.jsonl"
    if feedback_path.is_file():
        with open(feedback_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                    oid = r.get("option_id", "")
                    if oid in banned:
                        continue
                    if oid not in profiles:
                        profiles[oid] = {"successes": 0, "trials": 0}
                    profiles[oid]["trials"] += 1
                    if r.get("success"):
                        profiles[oid]["successes"] += 1
                except json.JSONDecodeError:
                    pass

    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot = {
        "version": "1",
        "timestamp": ts,
        "profiles": profiles,
        "seed": seed,
    }
    out_path = root / "router_profiles_snapshot.json"
    root.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    # Also update router_profiles.json for runtime use
    (root / "router_profiles.json").write_text(json.dumps(profiles, indent=2) + "\n", encoding="utf-8")
    return {"snapshot_path": str(out_path), "profile_count": len(profiles), "timestamp": ts}
