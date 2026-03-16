# ClaudeClockwork Agent Framework

Autonomous agent framework for executing development tasks using Ollama.

## Setup

1. Ensure Ollama is running: `ollama serve`
2. Python 3.9+
3. Install: `pip install ollama`

## Usage

```python
from pathlib import Path
from claudeclockwork.agents.base_agent import BaseAgent
from claudeclockwork.agents.orchestrator import TaskOrchestrator

# Create orchestrator
orchestrator = TaskOrchestrator(Path.cwd())

# Define small task
task = {
    "id": "task-1",
    "description": "Generate unit tests",
    "agent_type": "test_generator",
    "files": ["src/module.py"],
}

# Execute
result = orchestrator.execute_task(task)
print(result)
```

## Key Principles

1. **Small Tasks Only**: Each task must be atomic (1 function, 1 file, single concern)
2. **Fast Models**: Use `gemma3:latest` by default
3. **Hybrid Execution**: Python for structure, Ollama for content
4. **Autonomous**: No human decision gates
5. **Self-Committing**: Agents commit their own work

## Agent Types

- `test_generator`: Generate unit tests
- `doc_fixer`: Fix documentation
- `code_fixer`: Fix bugs in code
- `test_runner`: Execute tests and report

## Configuration

Edit `claudeclockwork/config/ollama_config.py` to:
- Change model selection
- Set Ollama host/port
- Configure timeout
- Enable/disable decomposition

## Examples

See `examples/` folder for working agent implementations.
