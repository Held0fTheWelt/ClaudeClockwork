# Task: Skill Gap + Forge (Autodiscovery → Scaffold → Use)

## Goal
If skills don't exist, scaffold a new one (contract-first) and immediately use it.

## Step 1) Gap detect
```json
{
  "type": "skill_request_spec",
  "request_id": "req-gap-001",
  "skill_id": "skill_gap_detect",
  "inputs": { "intent": "<describe the recurring task>" }
}
```

## Step 2) Scaffold (dry-run first)
```json
{
  "type": "skill_request_spec",
  "request_id": "req-scaffold-dry-001",
  "skill_id": "skill_scaffold",
  "inputs": {
    "skill_name": "<snake_case_name>",
    "description": "<one sentence>",
    "dry_run": true
  }
}
```

## Step 3) Scaffold (write)
Same request, but `"dry_run": false`.

## Step 4) Validate immediately
Run the newly created tool once on a small sample (create a SkillRequestSpec for it).

## Output
- New skill files + registry entry
- First validation report
