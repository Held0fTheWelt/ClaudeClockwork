#!/usr/bin/env python3
"""
Migration Agent: Move Ollama development to ClaudeClockwork
Relocates .ollama folder and updates project structure.
"""

import shutil
import subprocess
from pathlib import Path
import json

WOS = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")
CW = Path("/mnt/d/ClaudeClockwork")

class MigrationAgent:
    """Autonomous agent for migrating development to ClaudeClockwork."""

    def __init__(self):
        self.actions = []
        self.status = {}

    def log(self, msg: str):
        print(f"  {msg}")

    def section(self, title: str):
        print(f"\n{'─'*70}")
        print(f"  {title}")
        print(f"{'─'*70}")

    def move_ollama_folder(self):
        """Move .ollama folder from WorldOfShadows to ClaudeClockwork."""
        self.section("Step 1: Move .ollama Folder")

        wos_ollama = WOS / ".ollama"
        cw_ollama = CW / ".ollama"

        if not wos_ollama.exists():
            self.log("✗ .ollama folder not found in WorldOfShadows")
            return False

        # Backup if .ollama already exists in CW
        if cw_ollama.exists():
            backup = CW / ".ollama_old"
            try:
                if backup.exists():
                    shutil.rmtree(backup)
                shutil.move(str(cw_ollama), str(backup))
                self.log(f"✓ Backed up existing .ollama to .ollama_old")
                self.actions.append("Backed up existing CW/.ollama to .ollama_old")
            except Exception as e:
                self.log(f"⚠ Could not backup: {str(e)[:50]}")

        # Move folder
        try:
            shutil.move(str(wos_ollama), str(cw_ollama))
            self.log(f"✓ Moved .ollama folder to ClaudeClockwork")
            self.actions.append("Moved WOS/.ollama → CW/.ollama")
            self.status['ollama_moved'] = True
            return True
        except Exception as e:
            self.log(f"✗ Move failed: {str(e)[:50]}")
            return False

    def move_claudeclockwork_folder(self):
        """Move claudeclockwork folder if in WOS to CW."""
        self.section("Step 2: Check claudeclockwork Framework")

        wos_cw = WOS / "claudeclockwork"
        cw_cw = CW / "claudeclockwork"

        if wos_cw.exists():
            self.log("ℹ Found claudeclockwork in WorldOfShadows")

            if not cw_cw.exists():
                try:
                    shutil.move(str(wos_cw), str(cw_cw))
                    self.log("✓ Moved claudeclockwork to ClaudeClockwork")
                    self.actions.append("Moved WOS/claudeclockwork → CW/claudeclockwork")
                    self.status['cw_moved'] = True
                except Exception as e:
                    self.log(f"⚠ Could not move: {str(e)[:50]}")
            else:
                self.log("✓ claudeclockwork already in ClaudeClockwork")
                self.status['cw_moved'] = True
        else:
            self.log("✓ No claudeclockwork in WorldOfShadows (already in CW)")
            self.status['cw_moved'] = True

        return self.status.get('cw_moved', False)

    def create_symlink_in_wos(self):
        """Create symlink in WorldOfShadows pointing to ClaudeClockwork .ollama."""
        self.section("Step 3: Create Symlink for Access")

        wos_ollama = WOS / ".ollama"
        cw_ollama = CW / ".ollama"

        if not cw_ollama.exists():
            self.log("⚠ ClaudeClockwork .ollama doesn't exist, skipping symlink")
            return False

        if wos_ollama.exists():
            self.log("✗ .ollama still exists in WorldOfShadows")
            return False

        try:
            # Create symlink for backward compatibility
            wos_ollama.symlink_to(cw_ollama)
            self.log("✓ Created symlink: WOS/.ollama → CW/.ollama")
            self.actions.append("Created symlink for backward compatibility")
            return True
        except Exception as e:
            self.log(f"⚠ Symlink creation failed: {str(e)[:50]}")
            self.log("  (Not critical - WOS can still access via full path)")
            return False

    def update_gitignore(self):
        """Update .gitignore files."""
        self.section("Step 4: Update .gitignore")

        # WorldOfShadows .gitignore - should ignore .ollama symbolic link
        wos_gitignore = WOS / ".gitignore"
        if wos_gitignore.exists():
            content = wos_gitignore.read_text()
            if ".ollama" not in content:
                # Don't add - .ollama is now in CW which has its own .gitignore
                self.log("✓ WOS/.gitignore: .ollama removal handled by relocation")
            else:
                self.log("✓ WOS/.gitignore already configured")
        else:
            self.log("⚠ No .gitignore in WorldOfShadows")

        # ClaudeClockwork .gitignore - verify .ollama is ignored
        cw_gitignore = CW / ".gitignore"
        if cw_gitignore.exists():
            content = cw_gitignore.read_text()
            if ".ollama/" in content or ".ollama" in content:
                self.log("✓ CW/.gitignore: .ollama already ignored")
            else:
                self.log("⚠ CW/.gitignore should ignore .ollama")
        else:
            self.log("ℹ No .gitignore in ClaudeClockwork")

        return True

    def verify_migration(self):
        """Verify migration success."""
        self.section("Step 5: Verification")

        wos_has_ollama = (WOS / ".ollama").exists()
        cw_has_ollama = (CW / ".ollama").exists()
        wos_ollama_symlink = (WOS / ".ollama").is_symlink()

        self.log(f"WorldOfShadows .ollama:")
        if wos_has_ollama:
            if wos_ollama_symlink:
                self.log(f"  → ✓ Symlink (points to {(WOS / '.ollama').resolve()})")
            else:
                self.log(f"  ✗ Still exists (should be moved)")
                return False
        else:
            self.log(f"  ✗ Missing (expected after move)")

        self.log(f"\nClaudeClockwork .ollama:")
        if cw_has_ollama:
            count = len(list((CW / ".ollama").rglob("*.py")))
            self.log(f"  ✓ Exists with {count} agent scripts")
        else:
            self.log(f"  ✗ Not found")
            return False

        return cw_has_ollama

    def create_readme(self):
        """Create README for ClaudeClockwork development."""
        self.section("Step 6: Create Development Documentation")

        readme = CW / "DEVELOPMENT.md"

        content = """# ClaudeClockwork Development Guide

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
"""

        try:
            readme.write_text(content)
            self.log("✓ Created DEVELOPMENT.md")
            self.actions.append("Created CW/DEVELOPMENT.md")
            return True
        except Exception as e:
            self.log(f"⚠ Could not create README: {str(e)[:50]}")
            return False

    def run(self):
        """Execute full migration."""
        print("\n" + "="*70)
        print("  MIGRATION AGENT: Move Development to ClaudeClockwork")
        print("="*70)

        # Execute migration steps
        r1 = self.move_ollama_folder()
        r2 = self.move_claudeclockwork_folder()
        r3 = self.create_symlink_in_wos()
        r4 = self.update_gitignore()
        r5 = self.verify_migration()
        r6 = self.create_readme()

        # Summary
        self.section("MIGRATION SUMMARY")

        print(f"\n✓ Migration Status: {'Complete' if r5 else 'Incomplete'}")
        print(f"✓ Actions performed: {len(self.actions)}\n")

        for action in self.actions:
            print(f"  ✓ {action}")

        print("\n" + "-"*70)
        print("  New Structure")
        print("-"*70)

        print(f"\nClaudeClockwork (DEVELOPMENT):")
        print(f"  ✓ .ollama/               - {len(list((CW / '.ollama').glob('*.py')))} agent scripts")
        print(f"  ✓ claudeclockwork/       - Framework")
        print(f"  ✓ DEVELOPMENT.md         - Documentation")

        print(f"\nWorldOfShadows (CONSUMER):")
        if (WOS / ".ollama").is_symlink():
            print(f"  → .ollama -> ../ClaudeClockwork/.ollama (symlink)")
        else:
            print(f"  → Uses agents from ClaudeClockwork")

        print("\n" + "="*70)
        print("  READY FOR DEVELOPMENT")
        print("="*70 + "\n")

        return r5


if __name__ == "__main__":
    import sys
    agent = MigrationAgent()
    success = agent.run()
    sys.exit(0 if success else 1)
