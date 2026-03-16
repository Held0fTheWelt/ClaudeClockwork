#!/usr/bin/env python3
"""
Analyze Active .claude Agent
Determines which .claude folder is CURRENTLY ACTIVE before consolidation.
"""

import ollama
from pathlib import Path
from datetime import datetime
import json

CW = Path("/mnt/d/ClaudeClockwork")
WOS = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

class AnalyzeActiveClaude:
    """Determine active .claude and consolidate only if safe."""

    def __init__(self):
        self.findings = {}

    def log(self, msg: str):
        print(f"  {msg}")

    def section(self, title: str):
        print(f"\n{'─'*70}")
        print(f"  {title}")
        print(f"{'─'*70}")

    def analyze_folder(self, path: Path) -> dict:
        """Deep analysis of .claude folder."""
        if not path.exists():
            return {"exists": False}

        stats = {
            "exists": True,
            "path": str(path),
            "size_mb": 0,
            "file_count": 0,
            "dir_count": 0,
            "latest_file": None,
            "latest_timestamp": None,
        }

        try:
            latest_time = 0
            latest_file = None

            for item in path.rglob("*"):
                if item.is_file():
                    stats["file_count"] += 1
                    stats["size_mb"] += item.stat().st_size / 1024 / 1024
                    mtime = item.stat().st_mtime

                    if mtime > latest_time:
                        latest_time = mtime
                        latest_file = str(item.relative_to(path))

                elif item.is_dir() and item.parent == path:
                    stats["dir_count"] += 1

            if latest_time:
                stats["latest_timestamp"] = datetime.fromtimestamp(latest_time).isoformat()
                stats["latest_file"] = latest_file

        except Exception as e:
            self.log(f"Error analyzing {path}: {str(e)[:50]}")

        return stats

    def investigate_all(self):
        """Investigate all .claude folders in both projects."""
        self.section("Investigation: Analyzing Active .claude")

        locations = [
            ("WOS .claude (root)", WOS / ".claude"),
            ("WOS .claude/.claude (nested)", WOS / ".claude" / ".claude"),
            ("WOS .claude/.claude/.claude (nested-nested)", WOS / ".claude" / ".claude" / ".claude"),
            ("CW .claude (root)", CW / ".claude"),
            ("CW .claude/.claude (nested)", CW / ".claude" / ".claude"),
        ]

        for name, path in locations:
            self.log(f"\n{name}:")
            stats = self.analyze_folder(path)

            if stats["exists"]:
                self.log(f"  ✓ Exists")
                self.log(f"    Files: {stats['file_count']}")
                self.log(f"    Size: {stats['size_mb']:.2f} MB")
                self.log(f"    Latest: {stats.get('latest_file', 'N/A')}")
                self.log(f"    Modified: {stats.get('latest_timestamp', 'N/A')}")
            else:
                self.log(f"  ✗ Does not exist")

            self.findings[name] = stats

        return self.findings

    def analyze_activity(self):
        """Use Ollama to analyze which folder is active."""
        self.section("Analysis: Determining Active .claude")

        findings_json = json.dumps(self.findings, indent=2)

        prompt = f"""Analyze which .claude folder is CURRENTLY ACTIVE based on file timestamps and content.

FINDINGS:
{findings_json}

TASK:
1. Which folder has the MOST RECENT modifications? (timestamp-based)
2. Which folder is LARGEST? (indicates more usage)
3. Which is the ACTIVE folder that drives current work?
4. Are there DUPLICATES of the active folder at different nesting levels?

Respond with:
ACTIVE_FOLDER: [path]
ACTIVITY_LEVEL: [high/medium/low - based on recency]
DUPLICATES: [list of duplicate paths]
DECISION: [keep root active, remove nested] or [keep nested active, consolidate differently]
RATIONALE: [why this is the active one]"""

        analysis = self.run_ollama(prompt)
        self.log("✓ Analysis complete")
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

    def display_recommendation(self, analysis: str):
        """Display Ollama's recommendation."""
        self.section("Recommendation")

        print("\n" + analysis)

        print("\n" + "-"*70)
        print("Next Steps:")
        print("-"*70)
        print("""
Based on the analysis above:

1. IDENTIFY: Which .claude is the active/current one?
   - Check timestamps of recent files
   - Compare sizes (larger = more usage)
   - Look for session data from THIS conversation

2. VERIFY: Is the active one at the root level?
   - If YES: Remove all nested duplicates (safe to consolidate)
   - If NO: Move active one to root, then remove duplicates

3. MERGE: Any unique content from nested folders?
   - Copy unique items up to active folder
   - Remove empty nested folders

Only proceed with elimination once you confirm:
✓ Active folder identified (by timestamp/size/content)
✓ Active folder is at root level
✓ No unique data loss from consolidation
""")

    def run(self):
        """Execute analysis."""
        print("\n" + "="*70)
        print("  ANALYZE ACTIVE .claude FOLDER")
        print("  Determine which is current before consolidation")
        print("="*70)

        # Phase 1: Investigate
        findings = self.investigate_all()

        # Phase 2: Analyze
        analysis = self.analyze_activity()

        # Phase 3: Display
        self.display_recommendation(analysis)

        print("\n" + "="*70)
        print("  AWAITING CONFIRMATION")
        print("="*70 + "\n")


if __name__ == "__main__":
    agent = AnalyzeActiveClaude()
    agent.run()
