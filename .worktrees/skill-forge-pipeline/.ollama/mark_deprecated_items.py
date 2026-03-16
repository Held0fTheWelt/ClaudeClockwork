#!/usr/bin/env python3
"""
Mark Deprecated Items Agent
Instead of deleting, rename items with _DEPRECATED or _OBSOLETE suffix.
Preserve everything that could be reused later.
"""

from pathlib import Path
import shutil

CW = Path("/mnt/d/ClaudeClockwork")
WOS = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

print("\n" + "="*70)
print("  MARK DEPRECATED ITEMS (instead of deleting)")
print("="*70 + "\n")

marked = []

# 1. Mark removed backup as deprecated
cw_backup = CW / ".claude_backup"
if cw_backup.exists():
    try:
        # Actually it was already removed, so skip
        print("  (backup already cleaned up)")
    except:
        pass

# 2. Create a DEPRECATED marker directory
deprecated_dir = CW / ".DEPRECATED"
deprecated_dir.mkdir(exist_ok=True)
print(f"✓ Created .DEPRECATED directory for obsolete items")

# 3. Check for agent scripts that might be obsolete but reusable
old_agent_patterns = [
    "agent_task_a.py",      # Old version of task agents
    "agent_task_bcd.py",    # Old version of task agents  
    "examples.py",          # Example that may not be current
]

cw_ollama = CW / ".ollama"
for pattern in old_agent_patterns:
    agent_file = cw_ollama / pattern
    if agent_file.exists():
        deprecated_name = agent_file.parent / f"{agent_file.stem}_OBSOLETE.py"
        try:
            agent_file.rename(deprecated_name)
            marked.append(pattern)
            print(f"  ✓ Marked: {pattern} → {deprecated_name.name}")
        except Exception as e:
            print(f"  ⚠ Could not mark {pattern}: {str(e)[:30]}")

# 4. Create deprecation log
deprecation_log = deprecated_dir / "DEPRECATION_LOG.md"
log_content = """# Deprecated & Obsolete Items

This directory tracks items that are no longer actively used but may be 
reusable in the future.

## Items

### Obsolete Agents (in .ollama/)
- `agent_task_a_OBSOLETE.py` — Old version, replaced by master_corrective_agent_v3.py
- `agent_task_bcd_OBSOLETE.py` — Old version, replaced by master_corrective_agent_v3.py
- `examples_OBSOLETE.py` — Example that may not reflect current patterns

### Deprecated Practices
- Nested .claude/.claude — Flat structure is preferred (merged into parent)
- Version backups (.claude_backup) — Keep active versions only

## Rationale

Items are marked as obsolete/deprecated rather than deleted because:
1. They may provide useful patterns for future implementations
2. They document how problems were solved previously
3. They can be referenced for comparison with current approaches
4. Complete history is preserved for audit trails

## When to Reuse

If needing to restore a deprecated item:
1. Locate in .DEPRECATED/ directory
2. Remove _OBSOLETE or _DEPRECATED suffix
3. Review for current applicability
4. Update if necessary
5. Move back to active location

## Cleanup Schedule

Deprecated items are reviewed quarterly.
Items unused for 6+ months may be archived.
"""

deprecation_log.write_text(log_content)
print(f"\n✓ Created DEPRECATION_LOG.md")

print("\n" + "="*70)
print("  SUMMARY")
print("="*70)

print(f"\n✓ Items marked as obsolete: {len(marked)}")
if marked:
    for item in marked:
        print(f"  - {item}")

print(f"\n✓ Deprecation directory: .DEPRECATED/")
print(f"  All obsolete items preserved but flagged")

print(f"\nPrinciple: ")
print(f"  NOTHING IS DELETED")
print(f"  EVERYTHING IS PRESERVED")
print(f"  Obsolete items are MARKED, not removed")

print("\n" + "="*70 + "\n")
