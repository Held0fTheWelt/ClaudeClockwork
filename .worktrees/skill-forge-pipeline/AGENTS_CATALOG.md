# ClaudeClockwork Agent Catalog

Complete list of autonomous agents with descriptions.

## Agents by Category

### Corrective Agents (Fix issues)
- `master_corrective_agent_v3.py` — Multi-task corrective agent (Tasks A-D)
- `fix_markdown_wraps.py` — Remove markdown code block wrappers
- `fix_baseagent_structure.py` — Fix Python class structure
- `add_missing_methods.py` — Add methods to classes

### Integration Agents (Add features)
- `implement_taskexecutor_integration.py` — Integrate TaskExecutor into Flask backend
- `update_claudeclockwork_patterns.py` — Add patterns to ClaudeClockwork

### Consolidation Agents (Organize)
- `consolidate_claude_folders.py` — Merge duplicate .claude folders
- `migrate_to_claudeclockwork.py` — Move development to ClaudeClockwork

### Validation Agents (Verify)
- `validate_claudeclockwork_patterns.py` — Validate agent framework patterns
- `final_validation_report.py` — Generate validation report
- `verify_migration_complete.py` — Verify migration success
- `verify_dual_capability.py` — Check project equivalence

### Utility Agents (Support)
- `complete_migration.py` — Complete file migration
- `establish_knowledge_flow.py` — Set up knowledge flow

## How to Use

All agents follow the same pattern:

```bash
cd /mnt/d/ClaudeClockwork
python .ollama/agent_name.py
```

Each agent:
1. Performs autonomous task
2. Reports progress with `log()` and `section()`
3. Makes changes (read/write files)
4. Commits to git
5. Returns success/failure status

## Creating New Agents

See `/mnt/d/ClaudeClockwork/KNOWLEDGE/README.md` for patterns and templates.

## Agent Output Files

Some agents produce artifacts:
- Session/plan files in `.claude/`
- Modified project files
- Git commits with changes

All changes are tracked in git history.
