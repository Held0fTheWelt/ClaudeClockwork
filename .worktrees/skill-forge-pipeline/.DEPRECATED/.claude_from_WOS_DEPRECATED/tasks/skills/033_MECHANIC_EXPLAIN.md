    # Task: Mechaniken verstehen

    ## Run (SkillRequestSpec)
    ```json
    {
      "type": "skill_request_spec",
      "request_id": "req-mechanic_explain-001",
      "skill_id": "mechanic_explain",
      "inputs": {
  "name": "<mechanic>",
  "evidence_paths": [
    "path/to/file"
  ],
  "output_path": "docs/mechanics/<mechanic>.md"
}
    }
    ```

    Execute:
    `python .claude/tools/skills/skill_runner.py --in request.json`
