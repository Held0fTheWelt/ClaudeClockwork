# Deprecated & Obsolete Items

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
