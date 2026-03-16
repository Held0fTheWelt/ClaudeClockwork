    # Task: Copyrights standardisieren

    ## Run (SkillRequestSpec)
    ```json
    {
      "type": "skill_request_spec",
      "request_id": "req-copyright_standardize-001",
      "skill_id": "copyright_standardize",
      "inputs": {
  "root": ".",
  "output_path": "docs/copyright_report.md"
}
    }
    ```

    Execute:
    `python .claude/tools/skills/skill_runner.py --in request.json`
