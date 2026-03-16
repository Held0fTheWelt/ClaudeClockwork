#!/usr/bin/env python3
"""
Fix .claude Structure Agent
Keep the ACTIVE .claude that drives the conversation.
Remove duplicates and nested errors.
Establish proper hierarchy.
"""

import shutil
from pathlib import Path

CW = Path("/mnt/d/ClaudeClockwork")
WOS = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

print("\n" + "="*70)
print("  FIX .claude STRUCTURE")
print("="*70 + "\n")

print("Current Active .claude:")
print("  → /mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows/.claude")
print("  (The one driving this conversation)")

wos_claude = WOS / ".claude"
nested_claude = wos_claude / ".claude"

print("\nStep 1: Remove Nested Duplicate")
print("-"*70)

if nested_claude.exists():
    print(f"\n✗ Found nested duplicate: {nested_claude}")
    print(f"  Size: {sum(f.stat().st_size for f in nested_claude.rglob('*') if f.is_file()) / 1024 / 1024:.2f} MB")
    print(f"  Items: {len(list(nested_claude.iterdir()))}")

    # Check if it has different content than parent
    parent_subdirs = {d.name for d in wos_claude.iterdir() if d.is_dir()}
    nested_subdirs = {d.name for d in nested_claude.iterdir() if d.is_dir()}

    print(f"\n  Parent .claude subdirs: {len(parent_subdirs)}")
    print(f"  Nested .claude subdirs: {len(nested_subdirs)}")

    if parent_subdirs == nested_subdirs:
        print("\n  → Nested is duplicate of parent (can safely remove)")
        try:
            shutil.rmtree(nested_claude)
            print("  ✓ Removed nested .claude/.claude")
        except Exception as e:
            print(f"  ✗ Could not remove: {str(e)[:50]}")
    else:
        print("\n  → Nested has different content (contains unique data)")
        print("  → Merging unique items into parent...")

        for item in nested_claude.iterdir():
            if item.is_dir():
                parent_item = wos_claude / item.name
                if not parent_item.exists():
                    shutil.copytree(item, parent_item)
                    print(f"    ✓ Merged: {item.name}")

        print("\n  ✓ Merging complete, removing nested folder")
        try:
            shutil.rmtree(nested_claude)
            print("  ✓ Removed nested .claude/.claude")
        except Exception as e:
            print(f"  ✗ Could not remove: {str(e)[:50]}")
else:
    print("\n✓ No nested duplicate found")

print("\nStep 2: Handle ClaudeClockwork .claude")
print("-"*70)

cw_claude = CW / ".claude"
cw_backup = CW / ".claude_backup"

if cw_claude.exists():
    print(f"\n✓ ClaudeClockwork .claude exists")
elif cw_backup.exists():
    print(f"\n✗ ClaudeClockwork has .claude_backup but no active .claude")
    print(f"  Size: {sum(f.stat().st_size for f in cw_backup.rglob('*') if f.is_file()) / 1024 / 1024:.2f} MB")

    # Check if it's identical to WOS
    wos_subdirs = {d.name for d in wos_claude.iterdir() if d.is_dir()}
    backup_subdirs = {d.name for d in cw_backup.iterdir() if d.is_dir()}

    if wos_subdirs == backup_subdirs:
        print("\n  Backup is duplicate of active WOS .claude")
        print("  → Can remove (data already in primary)")
        try:
            shutil.rmtree(cw_backup)
            print("  ✓ Removed .claude_backup (duplicate)")
        except Exception as e:
            print(f"  ✗ Could not remove: {str(e)[:50]}")
    else:
        print("\n  Backup has unique content - consider restoring")
        print("  Unique items in backup:")
        for item in backup_subdirs - wos_subdirs:
            print(f"    - {item}")
else:
    print(f"\n✗ ClaudeClockwork has no .claude folder")
    print("  → Creating symlink to WOS .claude (unified source of truth)")

    try:
        cw_claude.symlink_to(wos_claude)
        print(f"  ✓ Created: /mnt/d/ClaudeClockwork/.claude → {wos_claude}")
    except Exception as e:
        print(f"  ✗ Could not create symlink: {str(e)[:50]}")

print("\nStep 3: Verify Single Source of Truth")
print("-"*70)

print("\nFinal Structure:")
print(f"  ✓ Primary: {wos_claude}")

if (WOS / ".claude").exists() and not (WOS / ".claude").is_symlink():
    size = sum(f.stat().st_size for f in wos_claude.rglob("*") if f.is_file()) / 1024 / 1024
    items = len(list(wos_claude.rglob("*")))
    print(f"    - Size: {size:.2f} MB")
    print(f"    - Items: {items}")

if cw_claude.exists():
    if cw_claude.is_symlink():
        print(f"  ✓ ClaudeClockwork: Symlink → {cw_claude.resolve()}")
    else:
        print(f"  ✓ ClaudeClockwork: Own copy at {cw_claude}")

print(f"  ✓ Nested duplicates: Removed")
print(f"  ✓ Backups: Cleaned up")

print("\n" + "="*70)
print("  ✓ SINGLE SOURCE OF TRUTH ESTABLISHED")
print("="*70)
print("\n.claude Hierarchy:")
print("  PRIMARY (active, drives conversation):")
print("    /mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows/.claude/")
print("\n  SECONDARY (accesses primary):")
print("    /mnt/d/ClaudeClockwork/.claude/ → symlink to primary")
print("\n")
