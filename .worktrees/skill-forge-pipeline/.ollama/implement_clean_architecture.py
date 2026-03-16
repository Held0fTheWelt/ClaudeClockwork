#!/usr/bin/env python3
"""
Clean Architecture Implementation Agent
Separates ClaudeClockwork (System) from WorldOfShadows (Project).
Only project-specific content remains in WorldOfShadows.
"""

import shutil
from pathlib import Path

CW = Path("/mnt/d/ClaudeClockwork")
WOS = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

class CleanArchitectureAgent:
    """Implement clean separation of system vs project."""

    def __init__(self):
        self.removed = []
        self.kept = []
        self.notes = []

    def log(self, msg: str):
        print(f"  {msg}")

    def section(self, title: str):
        print(f"\n{'─'*70}")
        print(f"  {title}")
        print(f"{'─'*70}")

    def cleanup_wos(self):
        """Remove ClaudeClockwork/system files from WorldOfShadows."""
        self.section("Step 1: Clean WorldOfShadows")

        # Files/folders to remove from WOS (ClaudeClockwork-related)
        to_remove = [
            (".ollama", "Agent scripts (now in ClaudeClockwork)"),
            (".claude", "Session memory (consolidate to ClaudeClockwork)"),
            ("USING_CLAUDECLOCKWORK_AGENTS.md", "Framework doc (belongs in CW)"),
        ]

        for item_name, reason in to_remove:
            item_path = WOS / item_name
            if item_path.exists():
                self.log(f"\n✓ {item_name}")
                self.log(f"  Reason: {reason}")

                if item_path.is_dir():
                    size = sum(f.stat().st_size for f in item_path.rglob("*") if f.is_file()) / 1024 / 1024
                    self.log(f"  Size: {size:.2f} MB")

                    # Move to CW .DEPRECATED instead of deleting
                    deprecated_name = f"{item_name}_from_WOS_DEPRECATED"
                    backup_path = CW / ".DEPRECATED" / deprecated_name

                    try:
                        backup_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(item_path), str(backup_path))
                        self.log(f"  → Moved to: .DEPRECATED/{deprecated_name}")
                        self.removed.append(item_name)
                    except Exception as e:
                        self.log(f"  ✗ Could not move: {str(e)[:40]}")
                        self.notes.append(f"Manual move needed for {item_name}")
                else:
                    # File - just move to deprecated
                    deprecated_path = CW / ".DEPRECATED" / f"{item_name}_DEPRECATED"
                    try:
                        deprecated_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(item_path), str(deprecated_path))
                        self.log(f"  → Moved to: .DEPRECATED/{item_name}_DEPRECATED")
                        self.removed.append(item_name)
                    except Exception as e:
                        self.log(f"  ✗ Could not move: {str(e)[:40]}")
            else:
                self.log(f"✓ {item_name} (already removed)")

    def verify_project_content(self):
        """Verify WorldOfShadows contains only project files."""
        self.section("Step 2: Verify Project Content")

        essential_dirs = [
            ("backend", "REST API & database"),
            ("administration-tool", "Public website & management UI"),
            ("docs", "Project documentation"),
        ]

        self.log("\nEssential project directories:")
        for dirname, purpose in essential_dirs:
            dirpath = WOS / dirname
            if dirpath.exists():
                self.log(f"  ✓ {dirname}/")
                self.log(f"    Purpose: {purpose}")
                self.kept.append(dirname)
            else:
                self.log(f"  ✗ {dirname}/ (missing)")

        # List what's in root
        self.log("\nRoot level files (project-specific):")
        for item in sorted(WOS.iterdir()):
            if item.is_file() and not item.name.startswith("."):
                self.log(f"  ✓ {item.name}")
                self.kept.append(item.name)

    def create_architecture_doc(self):
        """Create documentation of the new architecture."""
        self.section("Step 3: Create Architecture Documentation")

        arch_doc = """# Architecture: Clean Separation

## System vs Project

### ClaudeClockwork (SYSTEM)
The autonomous agent framework and management system.

**Location**: `/mnt/d/ClaudeClockwork/`

**Contains**:
- `.ollama/` — 70+ autonomous agent scripts
- `.claude/` — Unified session memory (master)
- `claudeclockwork/` — BaseAgent framework & orchestrator
- `KNOWLEDGE/` — Patterns, best practices, documentation
- `AGENTS_CATALOG.md` — Agent reference
- `DEVELOPMENT.md` — Development guide
- `.DEPRECATED/` — Obsolete but preserved items

**Manages**:
- Agent development and improvement
- Framework patterns and best practices
- Knowledge base for autonomous agents

### WorldOfShadows (PROJECT)
The actual application being developed.

**Location**: `/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows/`

**Contains**:
- `backend/` — REST API, database, business logic
- `administration-tool/` — Public website, admin interface
- `docs/` — Project-specific documentation
- `CLAUDE.md` — Project-specific Claude Code guidelines
- Project code, tests, configs

**Does NOT contain**:
- ✗ Agent framework files
- ✗ `.ollama/` folder
- ✗ ClaudeClockwork system files
- ✗ Framework documentation

## How They Work Together

```
ClaudeClockwork (Framework/System)
        ↓
    Agents & Tools
        ↓
WorldOfShadows (Project)
```

### Workflow

1. **Need to fix/improve WorldOfShadows**?
   - Create or use an agent from ClaudeClockwork
   - Agent runs in ClaudeClockwork context
   - Agent modifies WorldOfShadows files directly
   - Changes committed to WorldOfShadows repo

2. **Need to improve the agent framework**?
   - Work in ClaudeClockwork
   - Update agents, patterns, documentation
   - Available for all projects using the framework

3. **Session Memory** (`.claude`)?
   - Stored in ClaudeClockwork (master)
   - Tracks framework development
   - Accessible to agents working on any project

## Benefits

✓ **Clean separation of concerns**
- System code separate from project code
- Framework improvements don't pollute projects
- Each project stays focused on business logic

✓ **Reusable framework**
- ClaudeClockwork agents work on any project
- Patterns and practices documented in one place
- Framework improvements benefit all projects

✓ **Simplified project repos**
- WorldOfShadows contains only project files
- No framework clutter
- Easier to understand project structure
- Cleaner git history

✓ **Independent evolution**
- ClaudeClockwork can improve independently
- Projects can update framework version when ready
- No tight coupling

## For Developers

**Working on WorldOfShadows**?
→ Use agents from ClaudeClockwork

**Improving the agent framework**?
→ Work in ClaudeClockwork

**Adding project-specific agents**?
→ Create in ClaudeClockwork, tagged for this project

**Questions about patterns**?
→ See ClaudeClockwork/KNOWLEDGE/

---

This clean architecture enables:
- Autonomous agent framework (ClaudeClockwork)
- Multiple projects using the framework (WorldOfShadows, others)
- Clear separation of system vs application code
- Reusable, improvable framework
"""

        arch_path = WOS / "ARCHITECTURE.md"
        arch_path.write_text(arch_doc)
        self.log(f"✓ Created ARCHITECTURE.md")
        self.notes.append("Architecture documented in ARCHITECTURE.md")

    def create_reference_guide(self):
        """Create quick reference for using ClaudeClockwork."""
        self.section("Step 4: Create Quick Reference")

        ref_guide = """# Quick Reference: Using ClaudeClockwork

WorldOfShadows is now a pure project repository.
All autonomous agent work happens in ClaudeClockwork.

## Using Agents

To run an agent on WorldOfShadows:

```bash
cd /mnt/d/ClaudeClockwork
python .ollama/agent_name.py
```

Common agents:
- `master_corrective_agent_v3.py` — Fix bugs, code issues
- `implement_taskexecutor_integration.py` — Add features
- `consolidate_claude_folders.py` — Organize structure
- `validate_claudeclockwork_patterns.py` — Validate patterns

## Viewing Agent Catalog

```bash
cat /mnt/d/ClaudeClockwork/AGENTS_CATALOG.md
```

## Learning Patterns

See patterns and best practices:

```bash
cat /mnt/d/ClaudeClockwork/KNOWLEDGE/README.md
```

## Development Guidelines

For WorldOfShadows specific guidelines:
- See: `CLAUDE.md` (this repo, project-specific)

For agent/framework guidelines:
- See: `ClaudeClockwork/KNOWLEDGE/README.md`

## Creating New Agents

1. Create in: `/mnt/d/ClaudeClockwork/.ollama/`
2. Inherit from: `claudeclockwork.agents.base_agent.BaseAgent`
3. Reference: `ClaudeClockwork/DEVELOPMENT.md`

## File Organization

```
WorldOfShadows/                 # Project only
├── backend/
├── administration-tool/
├── docs/
├── CLAUDE.md                   # Project-specific
├── ARCHITECTURE.md             # This structure
└── QUICK_REFERENCE.md          # This file

ClaudeClockwork/                # System framework
├── .ollama/                    # Agents
├── .claude/                    # Session memory
├── claudeclockwork/            # Framework
├── KNOWLEDGE/                  # Patterns
└── [framework files]
```

## When Files Change

- `WorldOfShadows files` → commit to WorldOfShadows repo
- `ClaudeClockwork files` → agents handle automatically
- `Framework improvements` → available to all projects

---

Clean architecture = cleaner projects + better reusability
"""

        ref_path = WOS / "QUICK_REFERENCE.md"
        ref_path.write_text(ref_guide)
        self.log(f"✓ Created QUICK_REFERENCE.md")

    def update_claude_md(self):
        """Update CLAUDE.md to be project-specific only."""
        self.section("Step 5: Update CLAUDE.md")

        claude_path = WOS / "CLAUDE.md"
        if claude_path.exists():
            content = claude_path.read_text()

            # Add note about clean architecture
            note = """
## Using ClaudeClockwork Agents

This project uses the ClaudeClockwork autonomous agent framework.

**Important**: Framework management files have been moved to ClaudeClockwork.
This repo contains only WorldOfShadows project files.

For agent patterns, framework documentation, and agent catalog:
→ See: `/mnt/d/ClaudeClockwork/KNOWLEDGE/`
→ See: `/mnt/d/ClaudeClockwork/AGENTS_CATALOG.md`

For project-specific guidelines, continue reading this file.

---

"""
            if "Using ClaudeClockwork" not in content:
                # Add after overview section
                lines = content.split('\n')
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.startswith("## Repository Structure"):
                        insert_pos = i
                        break

                lines.insert(insert_pos, note)
                claude_path.write_text('\n'.join(lines))
                self.log(f"✓ Updated CLAUDE.md with architecture note")
            else:
                self.log(f"✓ CLAUDE.md already has framework reference")
        else:
            self.log(f"⚠ CLAUDE.md not found")

    def run(self):
        """Execute clean architecture implementation."""
        print("\n" + "="*70)
        print("  IMPLEMENT CLEAN ARCHITECTURE")
        print("  Separate ClaudeClockwork (System) from WorldOfShadows (Project)")
        print("="*70)

        # Phase 1: Cleanup WOS
        self.cleanup_wos()

        # Phase 2: Verify project content
        self.verify_project_content()

        # Phase 3: Documentation
        self.create_architecture_doc()
        self.create_reference_guide()
        self.update_claude_md()

        # Summary
        self.section("SUMMARY")

        print(f"\n✓ Removed from WorldOfShadows: {len(self.removed)} items")
        for item in self.removed:
            print(f"  - {item}")

        print(f"\n✓ Kept in WorldOfShadows: {len(self.kept)} items")
        for item in self.kept[:5]:
            print(f"  - {item}")
        if len(self.kept) > 5:
            print(f"  ... and {len(self.kept) - 5} more")

        print(f"\n✓ Documentation created:")
        print(f"  - ARCHITECTURE.md")
        print(f"  - QUICK_REFERENCE.md")
        print(f"  - Updated CLAUDE.md")

        if self.notes:
            print(f"\n⚠ Notes:")
            for note in self.notes:
                print(f"  - {note}")

        print("\n" + "="*70)
        print("  ✓✓✓ CLEAN ARCHITECTURE IMPLEMENTED")
        print("="*70)
        print("""
New Structure:
  ClaudeClockwork = System/Framework (agents, patterns, management)
  WorldOfShadows = Project (backend, frontend, project docs)

Benefits:
  ✓ Clean separation of concerns
  ✓ Reusable framework for multiple projects
  ✓ Simplified project repositories
  ✓ Independent evolution paths
  ✓ Clear responsibilities
""")
        print("="*70 + "\n")


if __name__ == "__main__":
    import sys
    agent = CleanArchitectureAgent()
    agent.run()
    sys.exit(0)
