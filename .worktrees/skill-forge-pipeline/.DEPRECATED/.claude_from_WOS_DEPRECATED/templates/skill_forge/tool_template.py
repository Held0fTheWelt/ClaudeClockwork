"""Skill Tool: <skill_name>

<one_line_description>

Deterministic local-file tool. No network.
"""

from __future__ import annotations

import os
from typing import Any, Dict

def _write_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def run(spec: Dict[str, Any]) -> Dict[str, Any]:
    output_path = spec.get("output_path")
    if output_path:
        _write_text(output_path, "# Report\n\nTODO\n")
    return {"ok": True, "spec": spec, "output_path": output_path}
