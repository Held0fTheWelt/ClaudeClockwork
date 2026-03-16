#!/usr/bin/env python3
"""
Phase 19 — Migrate .llama_runtime/ to .clockwork_runtime/.

Copies contents of .llama_runtime/ into .clockwork_runtime/ (preserving structure).
Does not delete .llama_runtime/; remove manually if desired.
Run from repo root.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path


def main() -> int:
    root = Path.cwd()
    if not (root / ".claude").is_dir():
        print("Run from repo root (where .claude/ exists).", file=sys.stderr)
        return 1
    src = root / ".llama_runtime"
    dst = root / ".clockwork_runtime"
    if not src.is_dir():
        print("No .llama_runtime/ found; nothing to migrate.")
        dst.mkdir(parents=True, exist_ok=True)
        for sub in ("telemetry", "reports", "evidence", "redacted_exports", "eval", "knowledge", "brain", "writes"):
            (dst / sub).mkdir(parents=True, exist_ok=True)
        print("Created .clockwork_runtime/ layout.")
        return 0
    if dst.exists() and any(dst.iterdir()):
        print(".clockwork_runtime/ already has content; skipping copy.", file=sys.stderr)
        return 0
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        dest_item = dst / item.name
        if item.is_dir():
            shutil.copytree(item, dest_item, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest_item)
    print("Copied .llama_runtime/ -> .clockwork_runtime/. Remove .llama_runtime/ manually if desired.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
