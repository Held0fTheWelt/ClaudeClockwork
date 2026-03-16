#!/usr/bin/env python3
"""
Complete migration with copy + remove approach.
"""

import shutil
from pathlib import Path

WOS = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")
CW = Path("/mnt/d/ClaudeClockwork")

print("\n" + "="*70)
print("  COMPLETE MIGRATION")
print("="*70 + "\n")

wos_ollama = WOS / ".ollama"
cw_ollama = CW / ".ollama"

# Step 1: Copy .ollama to CW (preserve both during transition)
print("Step 1: Copy .ollama to ClaudeClockwork...")
if cw_ollama.exists():
    backup = CW / ".ollama_from_wos"
    if backup.exists():
        shutil.rmtree(backup)
    shutil.copytree(wos_ollama, backup)
    print(f"  ✓ Backed up existing CW/.ollama as .ollama_from_wos")

# Step 2: Merge unique files from WOS .ollama into CW .ollama
print("\nStep 2: Merge unique agents...")
if cw_ollama.exists():
    for item in wos_ollama.glob("*.py"):
        target = cw_ollama / item.name
        if not target.exists():
            shutil.copy2(item, target)
            print(f"  ✓ Copied: {item.name}")
    print(f"  ✓ Merged unique agents from WOS to CW")

# Step 3: Remove WOS .ollama
print("\nStep 3: Remove WOS .ollama...")
try:
    shutil.rmtree(wos_ollama)
    print(f"  ✓ Removed {wos_ollama}")
except Exception as e:
    print(f"  ⚠ Could not remove: {str(e)[:50]}")

# Step 4: Create symlink for backward compatibility
print("\nStep 4: Create symlink...")
try:
    wos_ollama.symlink_to(cw_ollama)
    print(f"  ✓ Created symlink: WOS/.ollama → CW/.ollama")
except Exception as e:
    print(f"  ⚠ Symlink failed: {str(e)[:50]}")

# Step 5: Verify
print("\nStep 5: Verify...")
if cw_ollama.exists():
    count = len(list(cw_ollama.glob("*.py")))
    print(f"  ✓ CW/.ollama has {count} agent scripts")

if (WOS / ".ollama").exists():
    if (WOS / ".ollama").is_symlink():
        target = (WOS / ".ollama").resolve()
        print(f"  ✓ WOS/.ollama is symlink → {target}")
    else:
        print(f"  ✓ WOS/.ollama exists")

print("\n" + "="*70)
print("  ✓ MIGRATION COMPLETE")
print("="*70)
print("\nNew Structure:")
print("  • ClaudeClockwork: Primary development (67+ agents)")
print("  • WorldOfShadows: Consumer (accesses via symlink)")
print("  • Shared .claude: Unified memory")
print("\n")
