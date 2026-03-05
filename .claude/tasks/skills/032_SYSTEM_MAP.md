    # Task: Systeme erfassen

    ## Run (SkillRequestSpec)
    ```json
    {
      "type": "skill_request_spec",
      "request_id": "req-system_map-001",
      "skill_id": "system_map",
      "inputs": {
  "root": ".",
  "output_path": "docs/system_map.md"
}
    }
    ```

    Execute:
    `python .claude/tools/skills/skill_runner.py --in request.json`
