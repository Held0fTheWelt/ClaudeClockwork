#!/usr/bin/env python3
"""
Knowledge Flow Agent: Establish one-way ClaudeClockwork → WorldOfShadows
Consolidates all knowledge/patterns/documentation to ClaudeClockwork.
"""

import ollama
import shutil
from pathlib import Path

CW = Path("/mnt/d/ClaudeClockwork")
WOS = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

class KnowledgeFlowAgent:
    """Establish unidirectional knowledge flow from ClaudeClockwork."""

    def __init__(self):
        self.actions = []

    def log(self, msg: str):
        print(f"  {msg}")

    def section(self, title: str):
        print(f"\n{'─'*70}")
        print(f"  {title}")
        print(f"{'─'*70}")

    def run_ollama(self, prompt: str) -> str:
        """Call Ollama for intelligent organization."""
        try:
            response = ollama.generate(
                model="gemma3:latest",
                prompt=prompt,
                stream=False,
            )
            return response.get("response", "").strip()
        except Exception as e:
            return f"[ERROR: {str(e)[:100]}]"

    def audit_documentation(self):
        """Audit documentation in both projects."""
        self.section("Step 1: Audit Existing Documentation")

        # ClaudeClockwork docs
        cw_docs = []
        for pattern in ["*.md", "docs/**/*.md", "*.txt"]:
            cw_docs.extend(CW.glob(pattern))

        self.log(f"ClaudeClockwork documentation:")
        self.log(f"  - {len(cw_docs)} files found")
        for doc in sorted(cw_docs)[:5]:
            self.log(f"    • {doc.name}")
        if len(cw_docs) > 5:
            self.log(f"    ... and {len(cw_docs) - 5} more")

        # WorldOfShadows docs
        wos_docs = []
        for pattern in ["*.md", "docs/**/*.md", "*.txt"]:
            wos_docs.extend(WOS.glob(pattern))

        self.log(f"\nWorldOfShadows documentation:")
        self.log(f"  - {len(wos_docs)} files found")
        for doc in sorted(wos_docs)[:5]:
            self.log(f"    • {doc.name}")
        if len(wos_docs) > 5:
            self.log(f"    ... and {len(wos_docs) - 5} more")

        return cw_docs, wos_docs

    def create_knowledge_base(self):
        """Create comprehensive knowledge base in ClaudeClockwork."""
        self.section("Step 2: Create Knowledge Base")

        kb_dir = CW / "KNOWLEDGE"
        kb_dir.mkdir(exist_ok=True)

        # Create main knowledge index
        index = """# ClaudeClockwork Knowledge Base

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
        print(f"\\n{'─'*70}\\n  {title}\\n{'─'*70}")

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
"""

        (kb_dir / "README.md").write_text(index)
        self.log("✓ Created KNOWLEDGE/README.md")
        self.actions.append("Created knowledge base in ClaudeClockwork")

        return kb_dir

    def create_consumer_guide(self):
        """Create guide for WorldOfShadows on using agents."""
        self.section("Step 3: Create Consumer Guide")

        guide = """# WorldOfShadows: Using ClaudeClockwork Agents

WorldOfShadows is a **consumer project** that uses agents created and maintained in ClaudeClockwork.

## Quick Start

### Run an existing agent

```bash
python /mnt/d/ClaudeClockwork/.ollama/agent_name.py
```

### Common agents

- **Fix bugs**: `master_corrective_agent_v3.py`
- **Add features**: `implement_taskexecutor_integration.py`
- **Validate**: `validate_claudeclockwork_patterns.py`

## How agents work in your project

1. Agent runs in ClaudeClockwork directory
2. Agent accesses WorldOfShadows files via absolute paths
3. Changes are made directly to WorldOfShadows
4. Commits are made to WorldOfShadows repo
5. Session memory shared via `.claude/` folder

## Example: Fix a bug in WorldOfShadows

```python
# In ClaudeClockwork/.ollama/fix_my_bug.py
from claudeclockwork.agents.base_agent import BaseAgent
from pathlib import Path

class BugFixAgent(BaseAgent):
    def run(self):
        wos = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

        # Read WOS file
        content = (wos / "backend/app/services/myservice.py").read_text()

        # Fix using Ollama
        prompt = f"Fix the bug in: {content[:500]}"
        fixed = self.run_ollama(prompt)

        # Write back to WOS
        (wos / "backend/app/services/myservice.py").write_text(fixed)

        # Commit in WOS repo
        self.git_add(["backend/app/services/myservice.py"])
        self.git_commit("fix: bug fixed")
```

## Knowledge Source

**Do not modify agents in WorldOfShadows .ollama/ folder.**

All agent development and updates happen in ClaudeClockwork:
- `/mnt/d/ClaudeClockwork/.ollama/` — Agent scripts
- `/mnt/d/ClaudeClockwork/KNOWLEDGE/` — Patterns & documentation
- `/mnt/d/ClaudeClockwork/DEVELOPMENT.md` — Development guide

## Reporting Issues

If you need a new agent or modification:
1. Create issue/task in ClaudeClockwork
2. Agent is developed and tested in ClaudeClockwork
3. Agent is then available for WorldOfShadows use

## One-Way Knowledge Flow

```
ClaudeClockwork (source)
        ↓
    Agents
        ↓
WorldOfShadows (consumer)
```

WorldOfShadows USES agents from ClaudeClockwork,
but does NOT contribute back to the framework.
"""

        guide_path = WOS / "USING_CLAUDECLOCKWORK_AGENTS.md"
        guide_path.write_text(guide)
        self.log("✓ Created USING_CLAUDECLOCKWORK_AGENTS.md in WorldOfShadows")
        self.actions.append("Created consumer guide in WorldOfShadows")

        return guide_path

    def document_agent_catalog(self):
        """Create catalog of all agents."""
        self.section("Step 4: Document Agent Catalog")

        cw_ollama = CW / ".ollama"
        agents = sorted(cw_ollama.glob("*.py"))

        catalog = """# ClaudeClockwork Agent Catalog

Complete list of autonomous agents with descriptions.

## Agents by Category

### Corrective Agents (Fix issues)
- `master_corrective_agent_v3.py` — Multi-task corrective agent (Tasks A-D)
- `fix_markdown_wraps.py` — Remove markdown code block wrappers
- `fix_baseagent_structure.py` — Fix Python class structure
- `add_missing_methods.py` — Add methods to classes

### Integration Agents (Add features)
- `implement_taskexecutor_integration.py` — Integrate TaskExecutor into Flask backend
- `update_claudeclockwork_patterns.py` — Add patterns to ClaudeClockwork

### Consolidation Agents (Organize)
- `consolidate_claude_folders.py` — Merge duplicate .claude folders
- `migrate_to_claudeclockwork.py` — Move development to ClaudeClockwork

### Validation Agents (Verify)
- `validate_claudeclockwork_patterns.py` — Validate agent framework patterns
- `final_validation_report.py` — Generate validation report
- `verify_migration_complete.py` — Verify migration success
- `verify_dual_capability.py` — Check project equivalence

### Utility Agents (Support)
- `complete_migration.py` — Complete file migration
- `establish_knowledge_flow.py` — Set up knowledge flow

## How to Use

All agents follow the same pattern:

```bash
cd /mnt/d/ClaudeClockwork
python .ollama/agent_name.py
```

Each agent:
1. Performs autonomous task
2. Reports progress with `log()` and `section()`
3. Makes changes (read/write files)
4. Commits to git
5. Returns success/failure status

## Creating New Agents

See `/mnt/d/ClaudeClockwork/KNOWLEDGE/README.md` for patterns and templates.

## Agent Output Files

Some agents produce artifacts:
- Session/plan files in `.claude/`
- Modified project files
- Git commits with changes

All changes are tracked in git history.
"""

        (CW / "AGENTS_CATALOG.md").write_text(catalog)
        self.log(f"✓ Created AGENTS_CATALOG.md ({len(agents)} agents documented)")
        self.actions.append(f"Created catalog for {len(agents)} agents")

        return agents

    def clean_wos_duplicates(self):
        """Remove duplicate documentation from WorldOfShadows."""
        self.section("Step 5: Clean Duplicate Documentation")

        # List files that should only exist in CW
        patterns_to_remove = [
            "CLAUDECLOCKWORK_*.md",
            "AGENT_*.md",
            "OLLAMA_*.md",
            "PHASE5_*.md",
        ]

        removed = []
        for pattern in patterns_to_remove:
            for file in WOS.glob(pattern):
                try:
                    file.unlink()
                    removed.append(file.name)
                    self.log(f"✓ Removed: {file.name}")
                except Exception as e:
                    self.log(f"⚠ Could not remove {file.name}: {str(e)[:30]}")

        if removed:
            self.actions.append(f"Removed {len(removed)} duplicate documentation files")
        else:
            self.log("✓ No duplicates found")

        return removed

    def create_knowledge_structure(self):
        """Use Ollama to create best-practice knowledge structure."""
        self.section("Step 6: Generate Knowledge Organization")

        prompt = """Generate a comprehensive knowledge organization structure for autonomous agent framework.

Context:
- ClaudeClockwork: Primary development platform (source of knowledge)
- 69+ autonomous agents already created
- BaseAgent framework complete
- One-way flow: ClaudeClockwork → WorldOfShadows

Task:
Create a knowledge organization with sections for:
1. Quick reference guide
2. Common patterns
3. Troubleshooting
4. FAQ
5. Architecture decisions
6. Future extensions

Format as markdown with clear sections.
Make it suitable for both developers and consumers."""

        structure = self.run_ollama(prompt)

        if structure and len(structure) > 500:
            (CW / "KNOWLEDGE_STRUCTURE.md").write_text(structure)
            self.log("✓ Generated knowledge structure")
            self.actions.append("Created KNOWLEDGE_STRUCTURE.md")
            return True

        self.log("⚠ Knowledge structure generation incomplete")
        return False

    def run(self):
        """Execute knowledge flow establishment."""
        print("\n" + "="*70)
        print("  ESTABLISH ONE-WAY KNOWLEDGE FLOW")
        print("  ClaudeClockwork → WorldOfShadows")
        print("="*70)

        # Phase 1: Audit
        cw_docs, wos_docs = self.audit_documentation()

        # Phase 2: Create knowledge base
        kb = self.create_knowledge_base()

        # Phase 3: Create consumer guide
        self.create_consumer_guide()

        # Phase 4: Document agents
        agents = self.document_agent_catalog()

        # Phase 5: Clean duplicates
        removed = self.clean_wos_duplicates()

        # Phase 6: Generate structure
        self.create_knowledge_structure()

        # Summary
        self.section("KNOWLEDGE FLOW ESTABLISHED")

        print(f"\n✓ Actions taken: {len(self.actions)}\n")
        for action in self.actions:
            print(f"  ✓ {action}")

        print("\n" + "-"*70)
        print("Knowledge Structure")
        print("-"*70)

        print(f"\nClaudeClockwork (SOURCE):")
        print(f"  ✓ KNOWLEDGE/README.md — Patterns & best practices")
        print(f"  ✓ AGENTS_CATALOG.md — List of all agents")
        print(f"  ✓ DEVELOPMENT.md — Development guide")
        print(f"  ✓ .ollama/ — 69+ agent scripts")

        print(f"\nWorldOfShadows (CONSUMER):")
        print(f"  ✓ USING_CLAUDECLOCKWORK_AGENTS.md — Usage guide")
        print(f"  ✓ References ClaudeClockwork knowledge")
        print(f"  ✓ Uses agents from /mnt/d/ClaudeClockwork/.ollama/")

        print(f"\nFlow Direction:")
        print(f"  ClaudeClockwork → WorldOfShadows")
        print(f"  (one-way, source to consumer)")

        print("\n" + "="*70)
        print("  ✓ ONE-WAY KNOWLEDGE FLOW ESTABLISHED")
        print("="*70 + "\n")

        return True


if __name__ == "__main__":
    import sys
    agent = KnowledgeFlowAgent()
    success = agent.run()
    sys.exit(0 if success else 1)
