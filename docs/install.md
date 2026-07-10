# Clockwork Installation (Phase 28)

## Supported installation

- **pip:** `pip install -e .` (editable from repo root). Requires Python 3.10+.
- **CLI entry point:** After install, run `clockwork --help` or `python -m claudeclockwork.cli --help`.

## First run

After installation, from your project root (where `.claude/` lives):

```bash
clockwork first-run
```

This creates `.clockwork_runtime/` and checks optional dependencies.

## Environment check

```bash
clockwork env-check
```

Exits 0 when healthy; non-zero with actionable errors (missing runtime root, Python version, etc.).

## Upgrade

Pull latest, then `pip install -e .` again. Align version markers per `Docs/versioning.md` and `Docs/upgrade_playbook.md`.

## Uninstall

`pip uninstall claudeclockwork`. Remove `.clockwork_runtime/` from project if desired.
