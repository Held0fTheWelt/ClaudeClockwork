import pytest

from clockwork.pipelines.runtime import OllamaClient


@pytest.mark.integration
def test_live_generate_roundtrip():
    client = OllamaClient()
    if not client.is_available():
        pytest.skip("local Ollama backend not reachable")
    text = client.generate("Reply with exactly one word: pong")
    assert isinstance(text, str) and text.strip()
