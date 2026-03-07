"""Phase 29 — Plugin discovery and load with schema validation and compatibility."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Try schema validation
def _validate_schema(data: dict[str, Any], schema_path: Path) -> tuple[bool, list[str]]:
    if not schema_path.is_file():
        return True, []
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        import jsonschema
        jsonschema.validate(instance=data, schema=schema)
        return True, []
    except Exception as e:
        return False, [str(e)]


def _parse_version(v: str) -> tuple[int, ...]:
    """Simple version tuple from string (e.g. 17.7.0 -> (17, 7, 0))."""
    parts = []
    for s in v.strip().replace("-", ".").split("."):
        try:
            parts.append(int(s))
        except ValueError:
            break
    return tuple(parts) if parts else (0,)


def _compatible(compat_range: str | None, current: str) -> bool:
    if not compat_range or not compat_range.strip():
        return True
    cur = _parse_version(current)
    # Minimal: support ">=17" or ">=17,<19"
    for part in compat_range.split(","):
        part = part.strip()
        if part.startswith(">="):
            want = _parse_version(part[2:].strip())
            if cur < want:
                return False
        elif part.startswith("<"):
            want = _parse_version(part[1:].strip())
            if cur >= want:
                return False
    return True


class PluginLoader:
    """Discover plugins from plugins/ or .clockwork_plugins/; validate schema and compatibility."""

    def __init__(self, project_root: Path | str, clockwork_version: str = "17.0") -> None:
        self._root = Path(project_root).resolve()
        self._version = clockwork_version
        self._schema_path = self._root / ".claude" / "contracts" / "schemas" / "plugin_manifest.schema.json"

    def discover(self) -> list[dict[str, Any]]:
        """Return list of validated plugin manifest dicts (deterministic order)."""
        results: list[dict[str, Any]] = []
        for base in ["plugins", ".clockwork_plugins"]:
            plug_root = self._root / base
            if not plug_root.is_dir():
                continue
            for manifest_file in sorted(plug_root.glob("*/plugin.json")):
                try:
                    data = json.loads(manifest_file.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if "id" not in data:
                    data["id"] = manifest_file.parent.name
                ok, errs = _validate_schema(data, self._schema_path)
                if not ok:
                    continue
                if not _compatible(data.get("clockwork_compat"), self._version):
                    continue
                results.append(data)
        return results

    def discover_strict(
        self,
        require_allowlist: bool = True,
        require_tests: bool = True,
    ) -> list[dict[str, Any]]:
        """Discover plugins; reject incompatible, unallowlisted (if require_allowlist), missing tests (if require_tests)."""
        from claudeclockwork.plugins.signing import is_allowlisted
        from claudeclockwork.plugins.test_harness import has_smoke_test
        results = []
        for base in ["plugins", ".clockwork_plugins"]:
            plug_root = self._root / base
            if not plug_root.is_dir():
                continue
            for manifest_file in sorted(plug_root.glob("*/plugin.json")):
                try:
                    data = json.loads(manifest_file.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if "id" not in data:
                    data["id"] = manifest_file.parent.name
                ok, _ = _validate_schema(data, self._schema_path)
                if not ok:
                    continue
                if not _compatible(data.get("clockwork_compat"), self._version):
                    continue
                plug_dir = manifest_file.parent
                pid = data.get("id", "")
                if require_allowlist:
                    allowed, _ = is_allowlisted(pid, plug_dir, self._root, strict=True)
                    if not allowed:
                        continue
                if require_tests and not has_smoke_test(data, plug_dir):
                    continue
                results.append(data)
        return results
