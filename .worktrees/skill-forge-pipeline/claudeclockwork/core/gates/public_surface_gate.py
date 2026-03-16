"""
Phase 44 — Public surface gate.

Fails when the declared public surface (Docs/public_api.md, claudeclockwork.__all__)
is expanded or changed without proper versioning/deprecation. Used in CI to enforce
SemVer discipline.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path


# Allowed top-level public symbols (must match Docs/public_api.md and __init__.py)
ALLOWED_PUBLIC = frozenset({"__version__"})


def _project_root() -> Path:
    """Resolve repo root (parent of claudeclockwork package)."""
    p = Path(__file__).resolve()
    # core/gates/public_surface_gate.py -> repo root
    for _ in range(5):
        if (p / "claudeclockwork" / "__init__.py").is_file():
            return p
        p = p.parent
    return Path.cwd()


def _get_package_exports() -> set[str]:
    """Read claudeclockwork/__init__.py and return the set of names in __all__."""
    root = _project_root()
    init_path = root / "claudeclockwork" / "__init__.py"
    if not init_path.is_file():
        return set()
    try:
        tree = ast.parse(init_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "__all__":
                    v = node.value
                    if isinstance(v, (ast.List, ast.Tuple)):
                        return {elt.value for elt in v.elts if isinstance(elt, ast.Constant)}
    return set()


def run_public_surface_gate(project_root: Path | str | None = None) -> dict:
    """
    Run public surface gate. Returns dict: pass (bool), errors (list).
    Fails if __all__ contains symbols not in the allowed set.
    """
    root = Path(project_root).resolve() if project_root else _project_root()
    errors = []

    exports = _get_package_exports()
    disallowed = exports - ALLOWED_PUBLIC
    if disallowed:
        errors.append(
            f"Public surface expansion: __all__ contains {sorted(disallowed)}. "
            "Allowed: {}. Update Docs/public_api.md and SemVer policy or remove from __all__.".format(
                sorted(ALLOWED_PUBLIC)
            )
        )

    # Contract files must exist
    for name in ("cli_contract.md", "public_api.md", "semver_policy.md", "deprecations.md"):
        if not (root / "Docs" / name).is_file():
            errors.append(f"Missing contract doc: Docs/{name}")

    return {"pass": len(errors) == 0, "errors": errors}


def main() -> int:
    result = run_public_surface_gate()
    if not result["pass"]:
        for e in result["errors"]:
            print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
