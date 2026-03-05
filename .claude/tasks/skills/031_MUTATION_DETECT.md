    # Task: Mutationen erkennen

    ## Run (SkillRequestSpec)
    ```json
    {
      "type": "skill_request_spec",
      "request_id": "req-mutation_detect-001",
      "skill_id": "mutation_detect",
      "inputs": {
  "left_root": "./snapshots/a",
  "right_root": "./snapshots/b",
  "output_path": "docs/mutation_report.md"
}
    }
    ```

    Execute:
    `python .claude/tools/skills/skill_runner.py --in request.json`
