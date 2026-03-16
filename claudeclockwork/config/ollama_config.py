"""Ollama configuration for agents."""

# Model Selection
MODELS = {
    "fast": "gemma3:latest",           # 3.3GB - for fast generation
    "coding": "qwen2.5-coder-32b:coding",  # 33GB - for code
    "docs": "qwen3.5-35b:docs",        # 35GB - for documentation
    "reasoning": "qwen3.5-35b:reasoning",  # 35GB - for analysis
    "agent": "qwen2.5-72b:agent",      # 72GB - fallback heavy model
}

# Default model for simple tasks
DEFAULT_MODEL = MODELS["fast"]

# Ollama Server
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_TIMEOUT = 300  # seconds

# Task Execution
TASK_DECOMPOSITION = True  # Break large tasks into small ones
MAX_TASK_SIZE = "small"    # Only "small" tasks run autonomously
SERIALIZED_EXECUTION = True  # Run one task at a time
