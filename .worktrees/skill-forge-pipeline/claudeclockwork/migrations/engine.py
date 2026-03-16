"""Phase 54 — Migration registry and engine. Deterministic."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

MigrationFn = Callable[[dict[str, Any]], dict[str, Any]]


class MigrationRegistry:
    """Registry of (from_version, to_version) -> migrator function."""

    def __init__(self) -> None:
        self._migrations: list[tuple[int, int, MigrationFn]] = []

    def register(self, from_ver: int, to_ver: int, fn: MigrationFn) -> None:
        self._migrations.append((from_ver, to_ver, fn))

    def migrate(self, data: dict[str, Any], from_ver: int, to_ver: int) -> dict[str, Any]:
        """Apply migrations from from_ver to to_ver in order."""
        current = dict(data)
        for f, t, fn in sorted(self._migrations):
            if f == from_ver and t <= to_ver:
                current = fn(current)
                from_ver = t
        return current


def run_migrations(
    config_path: Path | str,
    registry: MigrationRegistry,
    target_version: int = 2,
    dry_run: bool = True,
) -> dict[str, Any]:
    """
    Load config, detect schema_version, run migrations to target_version.
    If not dry_run, write back. Returns { applied: [...], final_version, written: bool }.
    """
    path = Path(config_path).resolve()
    if not path.is_file():
        return {"applied": [], "final_version": None, "written": False, "error": "file not found"}
    import json
    data = json.loads(path.read_text(encoding="utf-8"))
    current = data.get("schema_version", 1)
    if not isinstance(current, int):
        current = 1
    applied = []
    if current < target_version:
        result = registry.migrate(data, current, target_version)
        result["schema_version"] = target_version
        applied.append((current, target_version))
        if not dry_run:
            path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return {"applied": applied, "final_version": target_version, "written": not dry_run}
    return {"applied": [], "final_version": current, "written": False}
