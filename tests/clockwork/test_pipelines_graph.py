from clockwork.pipelines.briefs import run_brief
from clockwork.pipelines.draft_review_refine import run_draft_review_refine


class FakeClient:
    def __init__(self, available: bool = True):
        self.available = available
        self.prompts: list[str] = []

    def is_available(self) -> bool:
        return self.available

    def generate(self, prompt, model=None, system=None) -> str:
        self.prompts.append(prompt)
        return f"out-{len(self.prompts)}"


def test_pipeline_runs_three_steps_in_order():
    client = FakeClient()
    result = run_draft_review_refine("build a parser", client=client)
    assert result["status"] == "ok"
    assert result["draft"] == "out-1"
    assert result["review"] == "out-2"
    assert result["refined"] == "out-3"
    assert "build a parser" in client.prompts[0]
    assert "out-1" in client.prompts[1]
    assert "out-2" in client.prompts[2]


def test_pipeline_degrades_without_backend():
    result = run_draft_review_refine("x", client=FakeClient(available=False))
    assert result == {"status": "local_backend_unavailable", "task": "x"}


def test_brief_roundtrip_and_degradation():
    ok = run_brief("summarize this repo", client=FakeClient())
    assert ok["status"] == "ok" and ok["brief"] == "out-1"
    down = run_brief("x", client=FakeClient(available=False))
    assert down["status"] == "local_backend_unavailable"
