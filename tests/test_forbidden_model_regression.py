import sys, json, pathlib
sys.path.insert(0, '/mnt/d/ClaudeClockwork')
from claudeclockwork.core.ollama.model_manager import OllamaModelManager
pathlib.Path('.claude/state/ollama_model_state.json').write_text('{"default_model": "qwen2.5-72b"}')
manager = OllamaModelManager(project_root='.')
model, source = manager.resolve_model()
print(f"Result: {model} ({source})")
assert model == "qwen2.5-72b"