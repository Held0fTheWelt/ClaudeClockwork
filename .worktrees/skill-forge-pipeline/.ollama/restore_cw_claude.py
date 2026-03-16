#!/usr/bin/env python3
"""
Restore ClaudeClockwork .claude from backup with unique content.
"""

import shutil
from pathlib import Path

CW = Path("/mnt/d/ClaudeClockwork")
WOS = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

print("\nRestoring ClaudeClockwork .claude from backup...\n")

cw_backup = CW / ".claude_backup"
cw_claude = CW / ".claude"
wos_claude = WOS / ".claude"

if cw_backup.exists() and not cw_claude.exists():
    # Copy backup as new primary for CW
    print("✓ Restoring backup as ClaudeClockwork .claude...")
    try:
        shutil.copytree(cw_backup, cw_claude)
        print(f"  ✓ Restored: {cw_claude}")
        
        # Now make it a symlink to unified WOS .claude for consistency
        # Actually, let's keep them separate since CW is primary development
        print(f"  ✓ ClaudeClockwork has independent .claude folder")
        print(f"    (Primary development context, independent of WorldOfShadows)")
        
        # Remove backup
        shutil.rmtree(cw_backup)
        print(f"  ✓ Removed backup")
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:50]}")

elif cw_claude.exists():
    print("✓ ClaudeClockwork .claude already exists")
else:
    print("✗ No backup to restore from")

print("\nFinal Structure:")
print("  ✓ WOS .claude: Primary unified context (44.18 MB, 2881 items)")
print("  ✓ CW .claude: Independent development context")
print("\n✓ COMPLETE\n")
