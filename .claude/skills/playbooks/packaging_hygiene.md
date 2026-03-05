# Packaging Hygiene (No Cache Artifacts in Archives)

Policy: archives MUST NOT contain cache artifacts such as:
- `__pycache__/`
- `*.pyc`
- `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- `.DS_Store`, `Thumbs.db`

## Enforced by
- `repo_clean_scan` (detects junk inside a repo checkout)
- `last_train_merge` (ignores junk in input zips and never includes it in combined output)

## Recommended pre-zip cleanup commands
Python projects:
- delete `__pycache__/`, `*.pyc`
- delete `.pytest_cache/` and other tool caches

## Notes
Some zip builders include compiled bytecode automatically. Always sanitize before publishing.
