"""Phase 26 — Router profiles store (JSONL + snapshot under runtime root)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ProfilesStore:
    """Store and load routing profiles (successes, trials, latency) per option."""

    def __init__(self, runtime_root: Path | str) -> None:
        self._root = Path(runtime_root).resolve()
        self._profiles_path = self._root / "router_profiles.json"
        self._jsonl_path = self._root / "router_feedback.jsonl"

    def load_profiles(self) -> dict[str, Any]:
        """Load current profiles (option_id -> {successes, trials, ...})."""
        if not self._profiles_path.is_file():
            return {}
        try:
            return json.loads(self._profiles_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def save_profiles(self, profiles: dict[str, Any]) -> None:
        """Persist profiles snapshot."""
        self._root.mkdir(parents=True, exist_ok=True)
        self._profiles_path.write_text(json.dumps(profiles, indent=2) + "\n", encoding="utf-8")

    def append_feedback(self, option_id: str, success: bool, latency_ms: float | None = None) -> None:
        """Append one feedback event to JSONL for later aggregation."""
        self._root.mkdir(parents=True, exist_ok=True)
        record = {"option_id": option_id, "success": success, "latency_ms": latency_ms}
        with open(self._jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def update_from_feedback(self) -> dict[str, Any]:
        """Recompute profiles from JSONL and save snapshot. Returns new profiles."""
        profiles: dict[str, dict[str, Any]] = {}
        if self._jsonl_path.is_file():
            with open(self._jsonl_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        r = json.loads(line)
                        oid = r.get("option_id", "")
                        if oid not in profiles:
                            profiles[oid] = {"successes": 0, "trials": 0}
                        profiles[oid]["trials"] += 1
                        if r.get("success"):
                            profiles[oid]["successes"] += 1
                    except json.JSONDecodeError:
                        pass
        self.save_profiles(profiles)
        return profiles
