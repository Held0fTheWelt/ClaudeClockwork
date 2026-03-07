"""Phase 20 — LocalAI capability registry (from YAML)."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def load_registry(project_root: Path | str) -> dict[str, Any]:
    """
    Load localai_registry.yaml. Returns dict with 'capabilities' key.
    If file missing, returns {"capabilities": {}}.
    """
    root = Path(project_root).resolve()
    paths = [
        root / ".claude" / "config" / "localai_registry.yaml",
        root / "localai_registry.yaml",
    ]
    for p in paths:
        if p.is_file():
            try:
                import yaml
                data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
                return {"capabilities": data.get("capabilities", {})}
            except Exception:
                pass
            break
    return {"capabilities": {}}
