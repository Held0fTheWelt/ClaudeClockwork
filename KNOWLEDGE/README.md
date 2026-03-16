# ClaudeClockwork Knowledge Base

This is the **authoritative source** for autonomous agent patterns and practices.
All knowledge flows FROM this directory TO WorldOfShadows projects.

## Contents

### 1. Agent Framework
- **BaseAgent**: Core autonomous agent class with Ollama integration
- **TaskOrchestrator**: Multi-agent task execution and management
- **OllamaRouter**: Intelligent model routing (L0-L5 escalation)

### 2. Agent Patterns

#### Core Patterns
- Hybrid Python + Ollama approach
- Iterative generation (1 task per Ollama call)
- Error handling and recovery
- File I/O operations
- Git integration (commit, stage)

#### Specialized Patterns
- Corrective agents (fix bugs, code issues)
- Integration agents (add features)
- Validation agents (verify patterns)
- Consolidation agents (organize files)
- Migration agents (move/refactor projects)

### 3. Best Practices

#### Task Design
- Small, focused tasks (1 function per task)
- Avoid bulk generation (causes timeouts)
- Decompose large requirements
- Iterative validation

#### Ollama Usage
- Model selection by escalation level (L0-L5)
- Timeout handling with retries
- Graceful fallback to Claude API
- Proper error messages

#### Code Quality
- Proper indentation and structure
- Remove markdown code block wrappers
- Validate Python compilation
- Test imports before deployment

### 4. Common Agents & Use Cases

#### Bug Fixes
- `master_corrective_agent_v3.py` — Fix bugs, docs, code

#### Integration
- `implement_taskexecutor_integration.py` — Add features to backend
- `add_missing_methods.py` — Enhance classes

#### Organization
- `consolidate_claude_folders.py` — Organize project structure
- `migrate_to_claudeclockwork.py` — Move development projects

#### Validation
- `validate_claudeclockwork_patterns.py` — Verify agent patterns
- `final_validation_report.py` — Check readiness

### 5. Troubleshooting

#### Ollama Timeouts
**Problem**: Agent takes too long or times out
**Solution**: Use iterative generation (1 item per call, not bulk)
**Example**: Generate 1 test per agent call, not 25 at once

#### Markdown Wrapper Issues
**Problem**: Ollama wraps code in ```python markers
**Solution**: Use `fix_markdown_wraps.py` agent
**Prevention**: Request "Output ONLY the [code|file|content]"

#### Import Errors
**Problem**: ModuleNotFoundError in generated code
**Solution**: Verify import paths match project structure
**Pattern**: Use absolute imports (app.services, not ..services)

#### Permission Errors
**Problem**: Cannot move/delete files
**Solution**: Use shutil.copy + remove pattern
**Alternative**: Create symlinks for backward compatibility

### 6. Agent Creation Template

```python
#!/usr/bin/env python3
from claudeclockwork.agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.results = {}

    def log(self, msg):
        print(f"  {msg}")

    def section(self, title):
        print(f"\n{'─'*70}\n  {title}\n{'─'*70}")

    def run(self):
        self.section("My Task")

        # Read input
        content = self.read_file("path/to/file")

        # Use Ollama
        prompt = f"Analyze: {content[:500]}"
        result = self.run_ollama(prompt)

        # Write output
        self.write_file("output.txt", result)

        # Commit
        self.git_add(["output.txt"])
        self.git_commit("feat: task completed")

        self.log("✓ Complete")
        return True

if __name__ == "__main__":
    agent = MyAgent()
    agent.run()
```

### 7. References

- **BaseAgent**: `claudeclockwork/agents/base_agent.py`
- **Orchestrator**: `claudeclockwork/agents/orchestrator.py`
- **Config**: `claudeclockwork/config/ollama_config.py`
- **Agents**: `.ollama/*.py` (all scripts)

---

**This knowledge base is the source of truth for all agent-related patterns.
WorldOfShadows and other projects consume knowledge FROM here, not vice versa.**
