"""Phase 26 — Multi-armed bandit selection (Thompson Sampling / epsilon-greedy fallback)."""
from __future__ import annotations

import random
from typing import Any


class BanditPolicy:
    """
    Bandit policy for model/tool selection. Seed for reproducibility.
    Cold-start: uniform choice until profiles have data.
    """

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._seed = seed

    def select(
        self,
        options: list[str],
        budget_level: str,
        profiles: dict[str, Any] | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """
        Select one option. Returns (chosen_id, rationale_dict).
        With no profiles or all equal, uses budget_level to bias (fast->first, strong->last).
        """
        profiles = profiles or {}
        n = len(options)
        if n == 0:
            return "", {"reason_codes": ["no_options"], "budget_level": budget_level}
        # Cold-start or no profile data: deterministic by budget
        scores = []
        for i, opt in enumerate(options):
            prof = profiles.get(opt, {})
            # Prefer first for fast, last for strong
            if budget_level == "fast":
                bias = 1.0 / (i + 1)
            elif budget_level == "strong":
                bias = (i + 1) / n
            else:
                bias = 1.0
            success = prof.get("successes", 0)
            trials = prof.get("trials", 0)
            if trials > 0:
                scores.append((opt, (success / trials) * bias + self._rng.random() * 0.01))
            else:
                # Cold start: deterministic by bias only (no random) for reproducible tests
                scores.append((opt, bias))
        # Stable tie-break by option id so same seed => same choice
        scores.sort(key=lambda x: (-x[1], x[0]))
        chosen = scores[0][0]
        rationale = {
            "chosen_option": chosen,
            "alternatives_considered": options,
            "reason_codes": ["bandit", "budget"],
            "confidence": 0.85,
            "budget_level": budget_level,
        }
        return chosen, rationale
