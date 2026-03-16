    # Task: Patterns erkennen

    ## Run (SkillRequestSpec)
    ```json
    {
      "type": "skill_request_spec",
      "request_id": "req-pattern_detect-001",
      "skill_id": "pattern_detect",
      "inputs": {
  "root": ".",
  "output_path": "docs/pattern_report.md"
}
    }
    ```

    Execute:
    `python .claude/tools/skills/skill_runner.py --in request.json`
