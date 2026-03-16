#!/usr/bin/env python3
"""
Flatten .claude Folders Agent
Find ALL nested .claude folders at any depth and consolidate to root level only.
"""

import shutil
from pathlib import Path

CW = Path("/mnt/d/ClaudeClockwork")
WOS = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

class FlattenClaudeAgent:
    """Find and eliminate all nested .claude folders."""

    def __init__(self):
        self.removals = []
        self.merges = []

    def log(self, msg: str):
        print(f"  {msg}")

    def section(self, title: str):
        print(f"\n{'─'*70}")
        print(f"  {title}")
        print(f"{'─'*70}")

    def find_all_claude_folders(self, root: Path) -> list:
        """Recursively find ALL .claude folders at any depth."""
        found = []

        for item in root.rglob(".claude"):
            if item.is_dir():
                depth = len(item.relative_to(root).parts)
                found.append((item, depth))

        return sorted(found, key=lambda x: x[1], reverse=True)  # Deepest first

    def process_project(self, name: str, root: Path):
        """Process all .claude folders in a project."""
        self.section(f"Processing {name}")

        all_claudes = self.find_all_claude_folders(root)

        if not all_claudes:
            self.log(f"✓ No nested .claude folders found")
            return

        self.log(f"Found {len(all_claudes)} .claude folder(s):")

        for path, depth in all_claudes:
            rel_path = path.relative_to(root)
            self.log(f"  [{depth}] {rel_path}")

        # Find root level .claude
        root_claude = root / ".claude"
        nested_claudes = [p for p, d in all_claudes if d > 1]

        self.log(f"\nRoot level .claude: {root_claude.exists()}")
        self.log(f"Nested .claude folders: {len(nested_claudes)}")

        # Process nested folders from deepest to shallowest
        for nested_path, depth in sorted(all_claudes, key=lambda x: x[1], reverse=True):
            if nested_path == root_claude:
                # Skip root level
                continue

            self.log(f"\nProcessing: {nested_path.relative_to(root)}")

            # Check if it has unique content
            if root_claude.exists():
                parent_items = {d.name for d in root_claude.iterdir()}
                nested_items = {d.name for d in nested_path.iterdir()}
                unique = nested_items - parent_items

                if unique:
                    self.log(f"  ⚠ Has {len(unique)} unique item(s):")
                    for item in unique:
                        self.log(f"    • {item}")

                    # Merge unique items
                    self.log(f"  Merging unique items...")
                    for item_name in unique:
                        src = nested_path / item_name
                        dst = root_claude / item_name
                        try:
                            if src.is_dir():
                                shutil.copytree(src, dst)
                            else:
                                shutil.copy2(src, dst)
                            self.log(f"    ✓ Merged: {item_name}")
                            self.merges.append(f"{nested_path.relative_to(root)}/{item_name}")
                        except Exception as e:
                            self.log(f"    ✗ Failed: {str(e)[:40]}")
                else:
                    self.log(f"  ✓ No unique content (duplicate)")

            # Remove nested folder
            try:
                shutil.rmtree(nested_path)
                self.log(f"  ✓ Removed: {nested_path.relative_to(root)}")
                self.removals.append(str(nested_path.relative_to(root)))
            except Exception as e:
                self.log(f"  ✗ Could not remove: {str(e)[:40]}")

    def verify_structure(self, name: str, root: Path):
        """Verify final structure has only root-level .claude."""
        self.section(f"Verifying {name}")

        root_claude = root / ".claude"

        if root_claude.exists():
            self.log(f"✓ Root .claude exists")

            # Check for any remaining nested .claude
            nested = list(root_claude.rglob(".claude"))
            if nested:
                self.log(f"✗ ERROR: Found {len(nested)} nested .claude folder(s)!")
                for n in nested:
                    self.log(f"  {n.relative_to(root)}")
                return False
            else:
                self.log(f"✓ No nested .claude folders")

            # Stats
            size = sum(f.stat().st_size for f in root_claude.rglob("*") if f.is_file()) / 1024 / 1024
            items = len(list(root_claude.rglob("*")))
            self.log(f"  Size: {size:.2f} MB")
            self.log(f"  Items: {items}")
            return True
        else:
            self.log(f"✗ No .claude folder found!")
            return False

    def run(self):
        """Execute flattening."""
        print("\n" + "="*70)
        print("  FLATTEN .claude FOLDERS")
        print("  Remove ALL nesting - keep only ROOT level")
        print("="*70)

        # Process both projects
        self.process_project("WorldOfShadows", WOS)
        self.process_project("ClaudeClockwork", CW)

        # Verify
        self.section("VERIFICATION")

        wos_ok = self.verify_structure("WorldOfShadows", WOS)
        cw_ok = self.verify_structure("ClaudeClockwork", CW)

        # Summary
        self.section("SUMMARY")

        print(f"\n✓ Nested folders removed: {len(self.removals)}")
        for removal in self.removals:
            print(f"  - {removal}")

        print(f"\n✓ Unique items merged: {len(self.merges)}")
        for merge in self.merges[:5]:
            print(f"  - {merge}")
        if len(self.merges) > 5:
            print(f"  ... and {len(self.merges) - 5} more")

        print("\n" + "="*70)
        if wos_ok and cw_ok:
            print("  ✓✓✓ ALL .claude FOLDERS FLATTENED")
            print("  Only root-level .claude folders remain")
        else:
            print("  ⚠ Some issues remain - review above")
        print("="*70 + "\n")

        return wos_ok and cw_ok


if __name__ == "__main__":
    import sys
    agent = FlattenClaudeAgent()
    success = agent.run()
    sys.exit(0 if success else 1)
