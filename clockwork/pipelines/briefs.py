"""Single-step local brief with degradation-safe backend access."""

from __future__ import annotations

from clockwork.pipelines.runtime import OllamaClient

BRIEF_SYSTEM = (
    "You produce short, structured work briefs: goal, constraints, "
    "suggested steps. Be concrete and terse."
)


def run_brief(
    task: str, model: str | None = None, client: OllamaClient | None = None
) -> dict:
    client = client or OllamaClient()
    if not client.is_available():
        return {"status": "local_backend_unavailable", "task": task}
    brief = client.generate(task, model=model, system=BRIEF_SYSTEM)
    return {"status": "ok", "task": task, "brief": brief}
