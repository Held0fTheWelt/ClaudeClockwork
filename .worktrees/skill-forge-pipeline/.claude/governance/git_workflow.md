# Git & Version Control

## Commits

- Create commits only on explicit user request
- Format commit message via HEREDOC
- Co-author line: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
- Always create NEW commits — never amend (unless explicitly requested)
- On pre-commit hook error: Fix, re-stage, NEW commit (no amend — amend would modify previous commit)
- Stage specific files instead of `git add -A` or `git add .` (prevents accidentally committing sensitive files)
- Don't commit sensitive files (.env, credentials) — warn user if explicitly requested

## Forbidden Actions (Without Explicit Request)

- `push --force` — never on main/deve/master; warn user if requested
- `reset --hard`
- `checkout .` / `restore .` / `clean -f`
- `branch -D`
- `--no-verify` / `--no-gpg-sign` (don't skip hooks)
- Interactive flags (`-i`) on rebase, add, etc.
- `--no-edit` on rebase
- Change git config

## Push

- Don't push automatically — only on explicit request
- One-time consent does not count as general authorization for future pushes

## Pull Requests

- `gh pr create` with HEREDOC body
- Title under 70 characters
- Body format:
  ```
  ## Summary
  <1-3 bullet points>

  ## Test plan
  [Bulleted markdown checklist of TODOs for testing]

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  ```
- Before PR creation: analyze git status, git diff, git log

## Destructive Actions

Always obtain user confirmation before:
- Deleting files or branches
- Force-push, reset --hard
- Actions visible to others (push, PR, commenting on issues, releases)

## Unknown State

For unknown files, branches, or configuration: investigate first, then act.
- Merge conflicts: resolve instead of discarding
- Lock files: investigate process instead of deleting
- Unknown branches: don't delete without asking
