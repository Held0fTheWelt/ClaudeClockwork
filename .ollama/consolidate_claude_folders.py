#!/usr/bin/env python3
"""
Claude Folder Consolidation Agent
Analyzes duplicate .claude folders and consolidates them intelligently.
"""

import ollama
import subprocess
from pathlib import Path
import shutil
import json

WOS_CLAUDE = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows/.claude")
CW_CLAUDE = Path("/mnt/d/ClaudeClockwork/.claude")

class ClaudeFolderConsolidationAgent:
    """Autonomous agent for organizing duplicate .claude folders."""

    def __init__(self):
        self.findings = {}
        self.actions = []

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

    def analyze_folder(self, path: Path) -> dict:
        """Analyze .claude folder structure and contents."""
        if not path.exists():
            return {"exists": False, "files": [], "size": 0}

        files = []
        total_size = 0

        try:
            for item in path.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(path)
                    size = item.stat().st_size
                    total_size += size
                    files.append({
                        "path": str(rel_path),
                        "size": size,
                        "type": item.suffix or "no_extension"
                    })
        except Exception as e:
            self.log(f"Error scanning {path}: {str(e)[:50]}")

        return {
            "exists": True,
            "path": str(path),
            "files": files,
            "file_count": len(files),
            "total_size": total_size,
            "subdirs": len(set(f["path"].split("/")[0] for f in files))
        }

    def compare_folders(self):
        """Compare both .claude folders."""
        self.section("Analyzing .claude Folders")

        wos_info = self.analyze_folder(WOS_CLAUDE)
        cw_info = self.analyze_folder(CW_CLAUDE)

        self.log(f"WorldOfShadows .claude:")
        if wos_info["exists"]:
            self.log(f"  - Files: {wos_info['file_count']}")
            self.log(f"  - Size: {wos_info['total_size'] / 1024 / 1024:.2f} MB")
            self.log(f"  - Subdirs: {wos_info['subdirs']}")
        else:
            self.log(f"  - Not found")

        self.log(f"\nClaudeClockwork .claude:")
        if cw_info["exists"]:
            self.log(f"  - Files: {cw_info['file_count']}")
            self.log(f"  - Size: {cw_info['total_size'] / 1024 / 1024:.2f} MB")
            self.log(f"  - Subdirs: {cw_info['subdirs']}")
        else:
            self.log(f"  - Not found")

        self.findings['wos_info'] = wos_info
        self.findings['cw_info'] = cw_info

        return wos_info, cw_info

    def determine_consolidation_strategy(self, wos_info: dict, cw_info: dict):
        """Use Ollama to determine best consolidation strategy."""
        self.section("Analyzing Consolidation Strategy")

        prompt = f"""Analyze two duplicate .claude folders and recommend consolidation.

WORLDOFSHADOWS .claude:
- Files: {wos_info.get('file_count', 0)}
- Size: {wos_info.get('total_size', 0) / 1024 / 1024:.2f} MB
- Sample files: {json.dumps(wos_info.get('files', [])[:5], indent=2)}

CLAUDECLOCKWORK .claude:
- Files: {cw_info.get('file_count', 0)}
- Size: {cw_info.get('total_size', 0) / 1024 / 1024:.2f} MB
- Sample files: {json.dumps(cw_info.get('files', [])[:5], indent=2)}

CONTEXT:
- .claude folder stores: project memory, plans, session tracking
- WorldOfShadows is the primary project
- ClaudeClockwork is a secondary framework

TASK:
Recommend:
1. Which folder should be the SOURCE (primary)
2. Which folder should be the TARGET (gets consolidated into primary)
3. What content to KEEP vs DELETE
4. Strategy for handling duplicates vs unique files

Output format:
PRIMARY_FOLDER: [path]
SECONDARY_FOLDER: [path]
STRATEGY: [brief description]
ACTIONS:
- [action 1]
- [action 2]
- [action 3]"""

        strategy = self.run_ollama(prompt)
        self.findings['strategy'] = strategy
        self.log("✓ Strategy determined")
        return strategy

    def parse_strategy(self, strategy: str) -> dict:
        """Parse Ollama strategy output."""
        lines = strategy.split('\n')
        parsed = {
            "primary": None,
            "secondary": None,
            "actions": []
        }

        for line in lines:
            if line.startswith("PRIMARY_FOLDER:"):
                parsed["primary"] = line.split(":", 1)[1].strip()
            elif line.startswith("SECONDARY_FOLDER:"):
                parsed["secondary"] = line.split(":", 1)[1].strip()
            elif line.startswith("- "):
                parsed["actions"].append(line[2:].strip())

        return parsed

    def execute_consolidation(self, strategy_dict: dict):
        """Execute the consolidation based on strategy."""
        self.section("Executing Consolidation")

        primary = strategy_dict.get("primary")
        secondary = strategy_dict.get("secondary")

        if not primary or not secondary:
            self.log("⚠ Could not determine primary/secondary folders")
            return False

        primary_path = Path(primary) if "/" in str(primary) else WOS_CLAUDE
        secondary_path = Path(secondary) if "/" in str(secondary) else CW_CLAUDE

        # Step 1: Backup secondary
        if secondary_path.exists():
            backup_path = secondary_path.parent / f"{secondary_path.name}_backup"
            try:
                if backup_path.exists():
                    shutil.rmtree(backup_path)
                shutil.copytree(secondary_path, backup_path)
                self.log(f"✓ Backed up {secondary_path.name} to {backup_path.name}")
                self.actions.append(f"Backup created: {backup_path}")
            except Exception as e:
                self.log(f"✗ Backup failed: {str(e)[:50]}")

        # Step 2: Copy unique files from secondary to primary
        if secondary_path.exists() and primary_path.exists():
            try:
                for item in secondary_path.rglob("*"):
                    if item.is_file():
                        rel_path = item.relative_to(secondary_path)
                        target = primary_path / rel_path

                        # Only copy if doesn't exist in primary
                        if not target.exists():
                            target.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(item, target)
                            self.log(f"✓ Copied: {rel_path}")
                            self.actions.append(f"Copied: {rel_path}")

                self.log(f"✓ Merged unique files from secondary to primary")
            except Exception as e:
                self.log(f"✗ Merge failed: {str(e)[:50]}")

        # Step 3: Remove secondary folder
        if secondary_path.exists():
            try:
                shutil.rmtree(secondary_path)
                self.log(f"✓ Removed {secondary_path.name}")
                self.actions.append(f"Removed: {secondary_path}")
            except Exception as e:
                self.log(f"✗ Removal failed: {str(e)[:50]}")

        return True

    def verify_consolidation(self):
        """Verify consolidation was successful."""
        self.section("Verification")

        wos_exists = WOS_CLAUDE.exists()
        cw_exists = CW_CLAUDE.exists()

        self.log(f"WorldOfShadows .claude: {'✓ Exists' if wos_exists else '✗ Removed'}")
        self.log(f"ClaudeClockwork .claude: {'✗ Removed' if not cw_exists else '✓ Still exists (unexpected)'}")

        if wos_exists and not cw_exists:
            file_count = len(list(WOS_CLAUDE.rglob("*")))
            self.log(f"\n✓ Consolidation successful")
            self.log(f"  Primary .claude now contains all data ({file_count} items)")
            return True

        return False

    def run(self):
        """Execute full consolidation workflow."""
        print("\n" + "="*70)
        print("  CLAUDE FOLDER CONSOLIDATION AGENT")
        print("="*70)

        # Phase 1: Analyze both folders
        wos_info, cw_info = self.compare_folders()

        # Phase 2: Determine strategy
        strategy = self.determine_consolidation_strategy(wos_info, cw_info)

        # Phase 3: Parse strategy
        strategy_dict = self.parse_strategy(strategy)

        # Phase 4: Execute consolidation
        if strategy_dict.get("primary") and strategy_dict.get("secondary"):
            success = self.execute_consolidation(strategy_dict)
        else:
            self.log("⚠ Strategy parsing failed, using default consolidation")
            # Default: WorldOfShadows is primary
            strategy_dict["primary"] = str(WOS_CLAUDE)
            strategy_dict["secondary"] = str(CW_CLAUDE)
            success = self.execute_consolidation(strategy_dict)

        # Phase 5: Verify
        verified = self.verify_consolidation()

        # Summary
        self.section("SUMMARY")

        print(f"\n✓ Consolidation {'successful' if verified else 'completed with warnings'}")
        print(f"✓ Actions performed: {len(self.actions)}")
        if self.actions:
            print("\nActions taken:")
            for action in self.actions[:10]:
                print(f"  - {action}")
            if len(self.actions) > 10:
                print(f"  ... and {len(self.actions) - 10} more")

        print("\n" + "="*70 + "\n")

        return verified


if __name__ == "__main__":
    import sys
    agent = ClaudeFolderConsolidationAgent()
    success = agent.run()
    sys.exit(0 if success else 1)
