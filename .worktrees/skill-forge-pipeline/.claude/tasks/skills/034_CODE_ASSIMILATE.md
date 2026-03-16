    # Task: Assimilieren von Code

    ## Run (SkillRequestSpec)
    ```json
    {
      "type": "skill_request_spec",
      "request_id": "req-code_assimilate-001",
      "skill_id": "code_assimilate",
      "inputs": {
  "foreign_root": "../foreign",
  "host_root": ".",
  "output_path": "docs/integration/plan.md"
}
    }
    ```

    Execute:
    `python .claude/tools/skills/skill_runner.py --in request.json`
