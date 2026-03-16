    # Task: Logs standardisieren

    ## Run (SkillRequestSpec)
    ```json
    {
      "type": "skill_request_spec",
      "request_id": "req-log_standardize-001",
      "skill_id": "log_standardize",
      "inputs": {
  "root": ".",
  "output_path": "docs/log_standard.md"
}
    }
    ```

    Execute:
    `python .claude/tools/skills/skill_runner.py --in request.json`
