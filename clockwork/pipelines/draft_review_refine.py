"""Draft -> review -> refine LangGraph pipeline over the local backend."""

from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from clockwork.pipelines.runtime import OllamaClient


class PipelineState(TypedDict, total=False):
    task: str
    model: str | None
    draft: str
    review: str
    refined: str


def _build_graph(client: OllamaClient):
    def draft_node(state: PipelineState) -> dict:
        prompt = f"Draft a solution for the following task:\n{state['task']}"
        return {"draft": client.generate(prompt, model=state.get("model"))}

    def review_node(state: PipelineState) -> dict:
        prompt = (
            "Review this draft critically. List concrete defects and "
            f"improvements.\n\nTask:\n{state['task']}\n\nDraft:\n{state['draft']}"
        )
        return {"review": client.generate(prompt, model=state.get("model"))}

    def refine_node(state: PipelineState) -> dict:
        prompt = (
            "Rewrite the draft applying the review feedback. Return only the "
            f"improved result.\n\nDraft:\n{state['draft']}\n\nReview:\n{state['review']}"
        )
        return {"refined": client.generate(prompt, model=state.get("model"))}

    graph = StateGraph(PipelineState)
    graph.add_node("draft", draft_node)
    graph.add_node("review", review_node)
    graph.add_node("refine", refine_node)
    graph.add_edge(START, "draft")
    graph.add_edge("draft", "review")
    graph.add_edge("review", "refine")
    graph.add_edge("refine", END)
    return graph.compile()


def run_draft_review_refine(
    task: str, model: str | None = None, client: OllamaClient | None = None
) -> dict:
    client = client or OllamaClient()
    if not client.is_available():
        return {"status": "local_backend_unavailable", "task": task}
    app = _build_graph(client)
    result = app.invoke({"task": task, "model": model})
    return {
        "status": "ok",
        "task": task,
        "draft": result["draft"],
        "review": result["review"],
        "refined": result["refined"],
    }
