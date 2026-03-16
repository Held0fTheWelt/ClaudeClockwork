# Paths and Placeholders

To keep this ruleset portable across machines (Windows/WSL/Linux/macOS), documents must not hardcode absolute paths.

## Placeholder
Use this placeholder in docs and examples:
- `<PROJECT_ROOT>`: the root of your repository checkout (where `.claude/` lives)

Examples:
- `python3 .claude/tools/test_ollama.py`
- `python3 <PROJECT_ROOT>/src/main.py --task "test ollama"`

Avoid:
- `/mnt/d/...`
- `/mnt/c/...`
