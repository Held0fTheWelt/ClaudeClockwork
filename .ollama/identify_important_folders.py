#!/usr/bin/env python3
"""
Identify Important Folders Agent
Determines which .claude subfolders are ACTUALLY USED and matter.
"""

import ollama
from pathlib import Path
from datetime import datetime
import json

CW = Path("/mnt/d/ClaudeClockwork")
WOS = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

class IdentifyImportantFolders:
    """Analyze which folders are actively used."""

    def __init__(self):
        self.findings = {}

    def log(self, msg: str):
        print(f"  {msg}")

    def section(self, title: str):
        print(f"\n{'─'*70}")
        print(f"  {title}")
        print(f"{'─'*70}")

    def analyze_subfolders(self, claude_path: Path) -> dict:
        """Analyze immediate subfolders of .claude."""
        if not claude_path.exists():
            return {}

        subfolders = {}

        for item in claude_path.iterdir():
            if item.is_dir():
                name = item.name

                # Get stats
                files = list(item.rglob("*"))
                file_count = len([f for f in files if f.is_file()])
                dir_count = len([f for f in files if f.is_dir()])
                size = sum(f.stat().st_size for f in files if f.is_file()) / 1024 / 1024

                # Get latest modification
                latest = 0
                latest_file = None
                for f in files:
                    if f.is_file() and f.stat().st_mtime > latest:
                        latest = f.stat().st_mtime
                        latest_file = str(f.relative_to(item))

                latest_date = datetime.fromtimestamp(latest).isoformat() if latest else "N/A"

                subfolders[name] = {
                    "files": file_count,
                    "dirs": dir_count,
                    "size_mb": size,
                    "latest_modified": latest_date,
                    "latest_file": latest_file,
                }

        return subfolders

    def investigate(self):
        """Investigate both .claude folders."""
        self.section("Subfolder Analysis")

        wos_claude = WOS / ".claude"
        cw_claude = CW / ".claude"

        self.log("\nWorldOfShadows .claude subfolders:\n")
        wos_subs = self.analyze_subfolders(wos_claude)
        for name, stats in sorted(wos_subs.items()):
            self.log(f"{name}:")
            self.log(f"  Files: {stats['files']}, Size: {stats['size_mb']:.2f} MB")
            self.log(f"  Latest: {stats['latest_modified']}")
            if stats['latest_file']:
                self.log(f"  File: {stats['latest_file']}")

        self.log(f"\nClaudeClockwork .claude subfolders:\n")
        cw_subs = self.analyze_subfolders(cw_claude)
        for name, stats in sorted(cw_subs.items()):
            self.log(f"{name}:")
            self.log(f"  Files: {stats['files']}, Size: {stats['size_mb']:.2f} MB")
            self.log(f"  Latest: {stats['latest_modified']}")
            if stats['latest_file']:
                self.log(f"  File: {stats['latest_file']}")

        self.findings['wos'] = wos_subs
        self.findings['cw'] = cw_subs

        return wos_subs, cw_subs

    def analyze_importance(self, wos_subs: dict, cw_subs: dict):
        """Use Ollama to determine which folders matter."""
        self.section("Importance Analysis")

        prompt = f"""Analyze which .claude subfolders are IMPORTANT and actively used.

WORLDOFSHADOWS .claude subfolders:
{json.dumps(wos_subs, indent=2)}

CLAUDECLOCKWORK .claude subfolders:
{json.dumps(cw_subs, indent=2)}

Criteria for importance:
1. Recently modified (active use)
2. Large size (significant content)
3. High file count (material data)
4. Type of folder (purpose):
   - "memory/" = Session memory (CRITICAL)
   - "projects/" = Project tracking (IMPORTANT)
   - "plans/" = Implementation plans (IMPORTANT)
   - "addons/" = Extensions (USEFUL)
   - "agents/" = Agent configs (USEFUL)
   - "worktrees/" = Git worktrees (OPTIONAL)
   - "changelog/" = Historical (REFERENCE)

Task:
For EACH folder, rate importance: CRITICAL / IMPORTANT / USEFUL / OPTIONAL / IGNORE

Then list:
1. CRITICAL folders - must keep
2. IMPORTANT folders - actively used
3. USEFUL folders - good to have
4. OPTIONAL folders - rarely needed
5. IGNORE folders - not used

Format:
CRITICAL: [list]
IMPORTANT: [list]
USEFUL: [list]
OPTIONAL: [list]
IGNORE: [list]

SUMMARY: [Which folders actually matter for active work]"""

        analysis = self.run_ollama(prompt)
        return analysis

    def run_ollama(self, prompt: str) -> str:
        """Call Ollama."""
        try:
            response = ollama.generate(
                model="gemma3:latest",
                prompt=prompt,
                stream=False,
            )
            return response.get("response", "").strip()
        except Exception as e:
            return f"[ERROR: {str(e)[:100]}]"

    def run(self):
        """Execute importance analysis."""
        print("\n" + "="*70)
        print("  IDENTIFY IMPORTANT FOLDERS")
        print("  Which .claude subfolders actually matter?")
        print("="*70)

        # Phase 1: Investigate
        wos_subs, cw_subs = self.investigate()

        # Phase 2: Analyze importance
        analysis = self.analyze_importance(wos_subs, cw_subs)

        # Phase 3: Display
        self.section("Folder Importance Rating")
        print("\n" + analysis)

        print("\n" + "="*70)
        print("  RECOMMENDATION")
        print("="*70)
        print("""
Based on importance levels:

KEEP (Essential):
  → CRITICAL folders (must preserve)
  → IMPORTANT folders (actively used)

REVIEW (Nice to have):
  → USEFUL folders (consider keeping for reference)

CAN REMOVE/ARCHIVE (Not needed):
  → OPTIONAL folders
  → IGNORE folders

For cleanup: Archive OPTIONAL/IGNORE folders rather than deleting
(preserves history, per your _DEPRECATED policy)
""")

        print("="*70 + "\n")


if __name__ == "__main__":
    agent = IdentifyImportantFolders()
    agent.run()
