# ClaudeClockwork Development Guide

This is the **primary development environment** for autonomous Ollama agent framework.

## Structure

```
ClaudeClockwork/
├── .ollama/                    # Autonomous agent scripts (primary development)
│   ├── master_*.py            # Master orchestrator agents
│   ├── *_agent.py             # Specialized task agents
│   └── *.py                   # Utility and correction agents
├── claudeclockwork/           # Agent framework (BaseAgent, Orchestrator, Config)
│   ├── agents/               # Core agent classes
│   ├── agents/implementations/ # Example agents
│   ├── config/               # Configuration
│   └── utils/                # Utilities
└── DEVELOPMENT.md            # This file
```

## Usage

All Ollama agent development happens in `.ollama/`:

### Create a New Agent

```python
#!/usr/bin/env python3
from claudeclockwork.agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__()

    def run(self):
        self.section("My Task")
        self.log("✓ Agent working")
        return True

if __name__ == "__main__":
    agent = MyAgent()
    agent.run()
```

### Run Agent

```bash
cd /mnt/d/ClaudeClockwork
python .ollama/my_agent.py
```

## Key Agents

- **master_corrective_agent_v3.py** - Fix bugs & documentation
- **implement_taskexecutor_integration.py** - Integrate features
- **consolidate_claude_folders.py** - Organize project structure
- **validate_claudeclockwork_patterns.py** - Pattern validation

## Framework

All agents inherit from `BaseAgent`:
- `log()` - Logging
- `section()` - Formatted output
- `read_file()` / `write_file()` - File operations
- `run_ollama()` - Ollama integration
- `git_add()` / `git_commit()` - Version control

## References

- **WorldOfShadows**: Consumer project (uses agents)
- **.claude**: Unified session memory (shared between projects)
