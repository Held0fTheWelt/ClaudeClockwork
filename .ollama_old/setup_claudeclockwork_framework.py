#!/usr/bin/env python3
"""
ClaudeClockwork Framework Setup Agent
Autonomously installs the Ollama agent framework on D:\ClaudeClockwork
"""

import shutil
import os
from pathlib import Path
import subprocess

# Map D: drive to /mnt/d in WSL2
CLOCKWORK_ROOT = Path("/mnt/d/ClaudeClockwork")
WORLD_OF_SHADOWS = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

def log(msg: str):
    print(f"  {msg}")

def section(title: str):
    print(f"\n{'─'*70}")
    print(f"  {title}")
    print(f"{'─'*70}")

def setup_framework():
    """Autonomously set up the agent framework."""

    print("\n" + "="*70)
    print("  CLAUDECLOCKWORK FRAMEWORK SETUP AGENT")
    print("="*70)

    # Step 1: Verify paths
    section("Step 1: Verify Paths")

    if not WORLD_OF_SHADOWS.exists():
        log(f"✗ Source not found: {WORLD_OF_SHADOWS}")
        return False

    log(f"✓ Source exists: {WORLD_OF_SHADOWS}")

    if not CLOCKWORK_ROOT.exists():
        log(f"✗ Target not found: {CLOCKWORK_ROOT}")
        log("  Create D:\\ClaudeClockwork manually or check drive mapping")
        return False

    log(f"✓ Target exists: {CLOCKWORK_ROOT}")

    # Step 2: Create directory structure
    section("Step 2: Create Directory Structure")

    dirs = [
        "claudeclockwork/agents",
        "claudeclockwork/agents/implementations",
        "claudeclockwork/models",
        "claudeclockwork/config",
        "claudeclockwork/utils",
    ]

    for dir_path in dirs:
        full_path = CLOCKWORK_ROOT / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        log(f"✓ {dir_path}")

    # Step 3: Copy helper functions
    section("Step 3: Copy Core Utilities")

    helper_src = WORLD_OF_SHADOWS / ".ollama/helper_functions.py"
    helper_dst = CLOCKWORK_ROOT / "claudeclockwork/utils/helper_functions.py"

    if helper_src.exists():
        shutil.copy2(helper_src, helper_dst)
        log(f"✓ Copied helper_functions.py")
    else:
        log(f"⚠ helper_functions.py not found")

    # Step 4: Create base_agent.py
    section("Step 4: Create Base Agent Framework")

    base_agent = '''"""Base agent framework for autonomous task execution."""

import ollama
from pathlib import Path
import subprocess
import json

class BaseAgent:
    """Base class for autonomous agents."""

    def __init__(self, project_root: Path = None):
        self.root = project_root or Path.cwd()
        self.modified_files = []
        self.results = {}

    def log(self, msg: str):
        print(f"    {msg}")

    def read_file(self, path: str) -> str:
        """Read file content."""
        full_path = self.root / path
        if not full_path.exists():
            return ""
        return full_path.read_text()

    def write_file(self, path: str, content: str) -> bool:
        """Write file content."""
        full_path = self.root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        self.modified_files.append(path)
        return True

    def run_ollama(self, prompt: str, model: str = "gemma3:latest") -> str:
        """Call Ollama with prompt."""
        try:
            response = ollama.generate(
                model=model,
                prompt=prompt,
                stream=False,
            )
            return response.get("response", "").strip()
        except Exception as e:
            return f"[ERROR: {str(e)[:100]}]"

    def git_add(self, files: list = None) -> bool:
        """Stage files for commit."""
        files_to_add = files or self.modified_files
        if not files_to_add:
            return False
        try:
            subprocess.run(
                ["git", "add"] + files_to_add,
                cwd=str(self.root),
                capture_output=True,
                check=True,
            )
            return True
        except:
            return False

    def git_commit(self, message: str) -> bool:
        """Commit staged changes."""
        try:
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(self.root),
                capture_output=True,
                check=True,
            )
            return True
        except:
            return False

    def report(self):
        """Print results summary."""
        print(f"\\n{'─'*70}")
        print("  RESULTS")
        print(f"{'─'*70}")
        for key, val in self.results.items():
            print(f"  {key}: {val}")
        print(f"  Files modified: {len(self.modified_files)}")
'''

    (CLOCKWORK_ROOT / "claudeclockwork/agents/base_agent.py").write_text(base_agent)
    log("✓ Created base_agent.py")

    # Step 5: Create __init__.py files
    section("Step 5: Create Python Package Markers")

    init_files = [
        "claudeclockwork/__init__.py",
        "claudeclockwork/agents/__init__.py",
        "claudeclockwork/agents/implementations/__init__.py",
        "claudeclockwork/models/__init__.py",
        "claudeclockwork/config/__init__.py",
        "claudeclockwork/utils/__init__.py",
    ]

    for init_file in init_files:
        (CLOCKWORK_ROOT / init_file).write_text("# Auto-generated\n")
        log(f"✓ {init_file}")

    # Step 6: Create config
    section("Step 6: Create Configuration")

    config = '''"""Ollama configuration for agents."""

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
'''

    (CLOCKWORK_ROOT / "claudeclockwork/config/ollama_config.py").write_text(config)
    log("✓ Created ollama_config.py")

    # Step 7: Create orchestrator
    section("Step 7: Create Task Orchestrator")

    orchestrator = '''"""Task orchestrator for autonomous execution."""

from pathlib import Path
from .agents.base_agent import BaseAgent

class TaskOrchestrator:
    """Manages autonomous agent execution."""

    def __init__(self, project_root: Path):
        self.root = project_root
        self.agents = {}
        self.completed = []
        self.failed = []

    def register_agent(self, name: str, agent_class):
        """Register an agent type."""
        self.agents[name] = agent_class

    def execute_task(self, task):
        """Execute a small autonomous task."""
        agent_type = task.get("agent_type", "generic")

        if agent_type not in self.agents:
            return {"success": False, "error": f"Unknown agent: {agent_type}"}

        agent = self.agents[agent_type](self.root)

        try:
            result = agent.execute(task)
            if result.get("success"):
                self.completed.append(task["id"])
            else:
                self.failed.append(task["id"])
            return result
        except Exception as e:
            self.failed.append(task["id"])
            return {"success": False, "error": str(e)}

    def report(self):
        """Print execution summary."""
        print(f"\\nCompleted: {len(self.completed)}")
        print(f"Failed: {len(self.failed)}")
        return len(self.failed) == 0
'''

    (CLOCKWORK_ROOT / "claudeclockwork/agents/orchestrator.py").write_text(orchestrator)
    log("✓ Created orchestrator.py")

    # Step 8: Create README
    section("Step 8: Create Documentation")

    readme = '''# ClaudeClockwork Agent Framework

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
'''

    (CLOCKWORK_ROOT / "README.md").write_text(readme)
    log("✓ Created README.md")

    # Step 9: Create examples
    section("Step 9: Create Example Agents")

    example = '''"""Example agent: Simple task executor."""

from claudeclockwork.agents.base_agent import BaseAgent

class ExampleAgent(BaseAgent):
    """Example agent demonstrating autonomous execution."""

    def execute(self, task):
        """Execute the task."""
        print(f"\\n  Executing: {task['description']}")

        # Use Ollama to help
        prompt = task.get("prompt", "Hello")
        response = self.run_ollama(prompt)

        # Write result
        output_file = task.get("output", "output.txt")
        self.write_file(output_file, response)

        # Commit
        self.git_add([output_file])
        self.git_commit(f"feat: {task['description']}")

        return {
            "success": True,
            "task_id": task["id"],
            "output_file": output_file,
            "response_length": len(response),
        }
'''

    (CLOCKWORK_ROOT / "claudeclockwork/agents/implementations/example.py").write_text(example)
    log("✓ Created example agent")

    # Step 10: Summary
    section("Setup Complete")

    log(f"✓ Framework installed to: {CLOCKWORK_ROOT}")
    log("✓ Directory structure created")
    log("✓ Core classes implemented")
    log("✓ Configuration set up")
    log("✓ Documentation created")

    return True

def main():
    """Run setup."""
    success = setup_framework()

    print("\n" + "="*70)
    if success:
        print("  ✓✓✓ CLAUDECLOCKWORK FRAMEWORK INSTALLED ✓✓✓")
        print("="*70)
        print("\nNext steps:")
        print("  1. Ensure Ollama is running: ollama serve")
        print("  2. Create your first agent in claudeclockwork/agents/implementations/")
        print("  3. Import BaseAgent and extend it")
        print("  4. Register agent with TaskOrchestrator")
        print("  5. Execute tasks autonomously")
    else:
        print("  ✗ SETUP FAILED")
        print("="*70)

    print()

if __name__ == "__main__":
    main()
