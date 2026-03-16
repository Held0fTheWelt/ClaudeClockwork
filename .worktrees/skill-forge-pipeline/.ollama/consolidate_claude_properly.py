#!/usr/bin/env python3
"""
Proper .claude Consolidation Agent
Investigates ALL .claude folders and nested structures to establish single source of truth.
"""

import ollama
from pathlib import Path
import json

CW = Path("/mnt/d/ClaudeClockwork")
WOS = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

class ProperClaudeConsolidationAgent:
    """Autonomous agent for proper .claude folder consolidation."""

    def __init__(self):
        self.findings = {}
        self.analysis = {}

    def log(self, msg: str):
        print(f"  {msg}")

    def section(self, title: str):
        print(f"\n{'─'*70}")
        print(f"  {title}")
        print(f"{'─'*70}")

    def run_ollama(self, prompt: str) -> str:
        """Call Ollama for intelligent analysis."""
        try:
            response = ollama.generate(
                model="gemma3:latest",
                prompt=prompt,
                stream=False,
            )
            return response.get("response", "").strip()
        except Exception as e:
            return f"[ERROR: {str(e)[:100]}]"

    def investigate_claude_folders(self):
        """Investigate all .claude folders and nested structures."""
        self.section("Investigation: .claude Folder Structure")

        locations_to_check = [
            ("WorldOfShadows .claude", WOS / ".claude"),
            ("ClaudeClockwork .claude", CW / ".claude"),
            ("ClaudeClockwork .claude_backup", CW / ".claude_backup"),
            ("Nested WOS .claude/.claude", WOS / ".claude" / ".claude"),
            ("Nested CW .claude/.claude", CW / ".claude" / ".claude"),
        ]

        for name, path in locations_to_check:
            self.log(f"\n{name}:")
            if path.exists():
                if path.is_dir():
                    items = list(path.iterdir())
                    size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / 1024 / 1024
                    self.log(f"  ✓ EXISTS")
                    self.log(f"    - Items: {len(items)}")
                    self.log(f"    - Size: {size:.2f} MB")

                    # List subdirectories
                    subdirs = [d.name for d in items if d.is_dir()]
                    if subdirs:
                        self.log(f"    - Subdirs: {', '.join(subdirs[:5])}")
                        if len(subdirs) > 5:
                            self.log(f"              ... and {len(subdirs) - 5} more")

                    self.findings[name] = {
                        "exists": True,
                        "path": str(path),
                        "items": len(items),
                        "size_mb": size,
                        "subdirs": subdirs
                    }
                else:
                    self.log(f"  → Symlink to {path.resolve()}")
                    self.findings[name] = {
                        "exists": True,
                        "is_symlink": True,
                        "target": str(path.resolve())
                    }
            else:
                self.log(f"  ✗ Does not exist")
                self.findings[name] = {"exists": False}

        return self.findings

    def analyze_with_ollama(self):
        """Use Ollama to analyze the findings."""
        self.section("Analysis: Single Source of Truth")

        findings_json = json.dumps(self.findings, indent=2)

        prompt = f"""Analyze the .claude folder structure and recommend consolidation strategy.

CURRENT STRUCTURE:
{findings_json}

CONTEXT:
- ClaudeClockwork is PRIMARY development platform
- WorldOfShadows is CONSUMER project
- Each project needs context tracking via .claude folder
- Goal: Single source of truth (not duplicate contexts)

TASK:
Recommend:
1. Should each project have its OWN .claude folder (separate contexts)?
   OR should they share ONE .claude folder (unified context)?

2. What about nested .claude/.claude folders? (These are errors)

3. If consolidating: which should be the source of truth?

4. What about .claude_backup? Keep or remove?

Answer with clear reasoning:
PRIMARY_SOLUTION: [one of: separate folders / unified folder]
REASONING: [why this is better]
BACKUP_HANDLING: [what to do with backups]
NESTED_FOLDERS: [remove nested duplicates]

Be specific about which folder should hold truth."""

        analysis = self.run_ollama(prompt)
        self.analysis['recommendation'] = analysis
        self.log("✓ Analysis complete")
        return analysis

    def print_findings_and_analysis(self):
        """Print detailed findings."""
        self.section("FINDINGS SUMMARY")

        print("\n.claude Locations Found:")
        for name, info in self.findings.items():
            if info.get("exists"):
                if info.get("is_symlink"):
                    print(f"\n  {name}:")
                    print(f"    → Symlink to: {info.get('target')}")
                else:
                    print(f"\n  {name}:")
                    print(f"    - Items: {info.get('items', 0)}")
                    print(f"    - Size: {info.get('size_mb', 0):.2f} MB")
            else:
                print(f"\n  {name}: (missing)")

        print("\n" + "-"*70)
        print("Ollama Recommendation:")
        print("-"*70)
        print(self.analysis.get('recommendation', 'No recommendation'))

    def display_options(self):
        """Display consolidation options."""
        self.section("CONSOLIDATION OPTIONS")

        print("""
Option 1: SEPARATE .claude FOLDERS (Recommended for primary development platforms)
  ├── /mnt/d/ClaudeClockwork/.claude/
  │   └── ClaudeClockwork development context
  │       (session history, agent development plans, framework evolution)
  └── /mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows/.claude/
      └── WorldOfShadows context
          (project plans, session history, consumer usage context)

  Pros: Separate concerns, independent development tracking
  Cons: Two folders to manage

Option 2: UNIFIED .claude FOLDER (Centralized knowledge)
  └── /mnt/d/ClaudeClockwork/.claude/
      └── Master context for BOTH projects
          (one source of truth, shared history)

  Pros: Single source of truth
  Cons: Mixed contexts (development + consumption)

Option 3: PRIMARY with SYMLINK (Hybrid)
  ├── /mnt/d/ClaudeClockwork/.claude/     (master, source of truth)
  └── /mnt/c/.../WorldOfShadows/.claude → symlink to CW/.claude
      (points to primary)

  Pros: Single source of truth, but accessible from both locations
  Cons: Symlink dependencies
""")

    def run(self):
        """Execute investigation and analysis."""
        print("\n" + "="*70)
        print("  PROPER .claude CONSOLIDATION INVESTIGATION")
        print("="*70)

        # Phase 1: Investigate
        findings = self.investigate_claude_folders()

        # Phase 2: Analyze with Ollama
        analysis = self.analyze_with_ollama()

        # Phase 3: Display results
        self.print_findings_and_analysis()

        # Phase 4: Show options
        self.display_options()

        self.section("NEXT STEPS")

        print("""
To properly consolidate:

1. VERIFY which consolidation option aligns with your requirements:
   - Separate folders? (independent project contexts)
   - Unified folder? (single source of truth)
   - Symlink hybrid? (one master, one pointer)

2. Verify nested .claude folders don't exist (they're errors)

3. Check .claude_backup contents (what needs to be kept vs removed)

4. Execute the chosen consolidation strategy

Current state:
- ClaudeClockwork is PRIMARY development platform
- WorldOfShadows is CONSUMER project
- Need clear role definition for .claude folders
""")

        print("\n" + "="*70 + "\n")

        return self.findings


if __name__ == "__main__":
    import sys
    agent = ProperClaudeConsolidationAgent()
    findings = agent.run()
    sys.exit(0)
