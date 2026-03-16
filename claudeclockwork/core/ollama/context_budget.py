"""Bounded context assembly for Ollama: task-relevant context only, configurable budget."""
from __future__ import annotations

from typing import Literal

Strategy = Literal["truncate_tail", "truncate_head", "slice_lines", "reject"]

DEFAULT_STRATEGY: Strategy = "truncate_tail"


class ContextBudgetExceededError(Exception):
    """Raised when strategy is 'reject' and content exceeds budget."""


def apply_budget(
    content: str,
    budget_chars: int,
    strategy: Strategy | str = DEFAULT_STRATEGY,
    ellipsis: str = "\n\n[... truncated ...]",
) -> str:
    """
    Enforce a character budget on content. Oversized content is truncated, sliced, or rejected.

    Args:
        content: Full prompt or context string.
        budget_chars: Maximum allowed length (characters).
        strategy: How to apply budget:
            - truncate_tail: keep head, drop tail (default).
            - truncate_head: keep tail, drop head.
            - slice_lines: keep middle lines so total <= budget (best-effort).
            - reject: raise ContextBudgetExceededError if over budget.
        ellipsis: Inserted at cut point for truncate_* (only if something was cut).

    Returns:
        Content within budget, or unchanged if already within budget.
    """
    if budget_chars <= 0:
        if strategy == "reject" and len(content) > 0:
            raise ContextBudgetExceededError(
                f"Content length {len(content)} exceeds budget {budget_chars}"
            )
        return content[:0] if strategy != "reject" else content

    if len(content) <= budget_chars:
        return content

    if strategy == "reject":
        raise ContextBudgetExceededError(
            f"Content length {len(content)} exceeds budget {budget_chars} (strategy=reject)"
        )

    if strategy == "truncate_tail":
        keep = budget_chars - len(ellipsis)
        if keep <= 0:
            return ellipsis.strip()
        return content[:keep] + ellipsis

    if strategy == "truncate_head":
        keep = budget_chars - len(ellipsis)
        if keep <= 0:
            return ellipsis.strip()
        return ellipsis + content[-keep:]

    if strategy == "slice_lines":
        lines = content.split("\n")
        if not lines:
            return content[:budget_chars]
        total = 0
        result: list[str] = []
        half_budget = (budget_chars - len(ellipsis) * 2) // 2
        # Add lines from start until half budget
        for line in lines:
            if total + len(line) + 1 > half_budget:
                break
            result.append(line)
            total += len(line) + 1
        result.append(ellipsis.strip())
        total = 0
        tail: list[str] = []
        for line in reversed(lines):
            if total + len(line) + 1 > half_budget:
                break
            tail.append(line)
            total += len(line) + 1
        result.append("\n".join(reversed(tail)))
        out = "\n".join(result)
        if len(out) > budget_chars:
            return content[: budget_chars - len(ellipsis)] + ellipsis
        return out

    # fallback
    return content[: budget_chars - len(ellipsis)] + ellipsis
