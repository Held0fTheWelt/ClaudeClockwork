# Skill Task: repo_compare

Ziel: Zwei Repos/Folders deterministisch vergleichen und einen Report erzeugen.

## Compare Request

```json
{
  "type": "skill_request_spec",
  "request_id": "req-compare-001",
  "skill_id": "repo_compare",
  "inputs": {
    "project_root": ".",
    "left_root": "../ClaudeCode",
    "right_root": "../LlamaCode",
    "exclude_prefixes": [".git/", "__pycache__/", ".pytest_cache/"],
    "write_report": true
  }
}
```

Der Report wird standardmäßig unter `.llama_runtime/knowledge/writes/compare_reports/` geschrieben.
