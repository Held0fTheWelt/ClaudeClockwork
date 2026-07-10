import httpx
import pytest

from clockwork.pipelines.runtime import (
    ForbiddenModelError,
    OllamaClient,
    RuntimeConfig,
    load_runtime_config,
)


def test_defaults_without_config_file(tmp_path):
    config = load_runtime_config(tmp_path / "missing.yaml")
    assert config.base_url == "http://127.0.0.1:11434"
    assert config.default_model == "qwen3:8b"
    assert "llama3.3:70b" in config.forbidden_models


def test_yaml_overrides(tmp_path):
    cfg = tmp_path / "clockwork.yaml"
    cfg.write_text(
        "ollama:\n  default_model: phi4\n  timeouts:\n    request: 60\n",
        encoding="utf-8",
    )
    config = load_runtime_config(cfg)
    assert config.default_model == "phi4"
    assert config.request_timeout == 60
    assert config.base_url == "http://127.0.0.1:11434"


def test_forbidden_model_hard_fails():
    client = OllamaClient(RuntimeConfig())
    with pytest.raises(ForbiddenModelError):
        client.generate("hi", model="llama3.3:70b")


def test_is_available_false_on_connect_error(monkeypatch):
    def boom(*args, **kwargs):
        raise httpx.ConnectError("refused")

    monkeypatch.setattr(httpx, "get", boom)
    assert OllamaClient(RuntimeConfig()).is_available() is False


def test_generate_falls_back_on_404(monkeypatch):
    calls: list[str] = []

    class FakeResponse:
        def __init__(self, status_code, payload):
            self.status_code = status_code
            self._payload = payload

        def raise_for_status(self):
            if self.status_code >= 400:
                raise httpx.HTTPStatusError(
                    "err",
                    request=httpx.Request("POST", "http://x"),
                    response=httpx.Response(self.status_code),
                )

        def json(self):
            return self._payload

    def fake_post(url, json=None, timeout=None):
        calls.append(json["model"])
        if json["model"] == "qwen3:8b":
            return FakeResponse(404, {})
        return FakeResponse(200, {"response": "pong"})

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OllamaClient(RuntimeConfig())
    assert client.generate("ping") == "pong"
    assert calls == ["qwen3:8b", "phi4"]
