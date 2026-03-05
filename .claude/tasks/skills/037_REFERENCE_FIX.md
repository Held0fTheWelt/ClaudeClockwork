    # Task: Reference broken error fix

    ## Run (SkillRequestSpec)
    ```json
    {
      "type": "skill_request_spec",
      "request_id": "req-reference_fix-001",
      "skill_id": "reference_fix",
      "inputs": {
  "root": ".",
  "docs_root": "docs",
  "dry_run": true,
  "output_path": "docs/broken_links.md"
}
    }
    ```

    Execute:
    `python .claude/tools/skills/skill_runner.py --in request.json`
