from __future__ import annotations

from pathlib import Path
from typing import Iterable


def discover_manifest_paths(skills_roots: str | Path | Iterable[str | Path]) -> list[Path]:
    if isinstance(skills_roots, (str, Path)):
        roots = [skills_roots]
    else:
        roots = list(skills_roots)
    manifests: list[Path] = []
    for root_value in roots:
        root = Path(root_value)
        if not root.exists():
            continue
        manifests.extend(sorted(root.rglob("manifest.json")))
    return manifests
