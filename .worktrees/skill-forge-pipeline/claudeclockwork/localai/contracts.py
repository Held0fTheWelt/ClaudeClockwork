"""Phase 20 — Local tool result contract validation."""
from __future__ import annotations

import json
from pathlib import Path


def _load_schema() -> dict:
    # Package-relative: claudeclockwork/localai -> repo root
    pkg_dir = Path(__file__).resolve().parent
    root = pkg_dir.parent.parent  # claudeclockwork -> repo
    schema_path = root / ".claude" / "contracts" / "schemas" / "local_tool_result.schema.json"
    if not schema_path.is_file():
        return {}
    return json.loads(schema_path.read_text(encoding="utf-8"))


def validate_local_tool_result(data: dict) -> tuple[bool, list[str]]:
    """
    Validate a result dict against local_tool_result schema.
    Returns (valid, list of error messages).
    """
    schema = _load_schema()
    if not schema:
        return True, []  # no schema in deploy
    try:
        import jsonschema
    except ImportError:
        return True, []
    try:
        jsonschema.validate(instance=data, schema=schema)
        return True, []
    except jsonschema.ValidationError as e:
        return False, [str(e)]
    except Exception as e:
        return False, [str(e)]
