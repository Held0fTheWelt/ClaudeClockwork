"""
Phase 65 — Runtime root gate: enforce .clockwork_runtime/ as single runtime root.

Fails if:
- .llama_runtime/ contains non-stub files (anything beyond README.md + .gitkeep)
- Code references .llama_runtime
- Docs reference .llama_runtime (except in deprecation notes)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def _project_root() -> Path:
    """Locate project root from module location."""
    p = Path(__file__).resolve()
    for _ in range(5):
        if (p / "claudeclockwork" / "__init__.py").is_file():
            return p
        p = p.parent
    return Path.cwd()


def _check_llama_runtime_stub(project_root: Path) -> list[str]:
    """
    Verify .llama_runtime/ is empty except for stub files (README.md, .gitkeep).
    Return list of violations.
    """
    llama_rt = project_root / ".llama_runtime"
    if not llama_rt.is_dir():
        return []

    allowed_files = {"README.md", ".gitkeep"}
    violations = []

    for item in llama_rt.iterdir():
        if item.name not in allowed_files:
            violations.append(f".llama_runtime/{item.name}: non-stub file present (must be removed)")
        # Ensure allowed files have correct content
        if item.name == "README.md":
            content = item.read_text(encoding="utf-8", errors="ignore")
            if "DEPRECATED" not in content and "deprecated" not in content:
                violations.append(f".llama_runtime/README.md: missing deprecation notice")

    return violations


def _check_code_references(project_root: Path) -> list[str]:
    """
    Scan active code for references to .llama_runtime.
    Exclude: legacy design docs, MVP phase docs, migration scripts.
    Return list of violations.
    """
    violations = []

    # Folders to check (active code)
    check_paths = [
        project_root / "claudeclockwork",
        project_root / "tests",
    ]

    # Patterns to match (literal .llama_runtime reference)
    pattern = re.compile(r"\.llama_runtime")

    excluded_prefixes = (
        ".claude-development",
        "scripts/migrate_runtime_root.py",
        "mvps/MVP_Phase19",
        ".project/Docs/References",
        "tests/test_runtime_root_gate.py",  # Gate test legitimately references .llama_runtime
        "claudeclockwork/core/gates/runtime_root_gate.py",  # Gate itself mentions .llama_runtime
    )

    for check_path in check_paths:
        if not check_path.is_dir():
            continue

        for py_file in check_path.rglob("*.py"):
            rel = py_file.relative_to(project_root)

            # Skip excluded paths
            if any(str(rel).startswith(ex) for ex in excluded_prefixes):
                continue

            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                for line_no, line in enumerate(content.split("\n"), 1):
                    if pattern.search(line):
                        violations.append(
                            f"{rel}:{line_no}: code references .llama_runtime (use .clockwork_runtime)"
                        )
            except Exception:
                pass

    return violations


def _check_doc_references(project_root: Path) -> list[str]:
    """
    Scan active docs for references to .llama_runtime (except deprecation notes).
    Check: .project/Docs/*, .claude/skills/*, Docs/ (legacy, for completeness).
    Return list of violations.
    """
    violations = []

    check_paths = [
        project_root / ".project" / "Docs",
    ]

    pattern = re.compile(r"\.llama_runtime")

    # Paths to always skip (legacy, read-only, or phase docs)
    # Note: skip_patterns use substring matching, so "Docs/" would match ".project/Docs/";
    # to match only root Docs/, use explicit startswith check below
    skip_patterns = [
        "Ref_RuntimeMigrationLlamaToClockwork",
        "MVP_Phase65",
        "MVP_Phase19",
        "Review_VERIFY",  # Legacy review docs
    ]

    for check_path in check_paths:
        if not check_path.is_dir():
            continue

        for md_file in check_path.rglob("*.md"):
            try:
                # Skip if path matches skip pattern
                rel_path = str(md_file.relative_to(project_root))

                # Skip legacy Docs/ root folder (pre-v18)
                if rel_path.startswith("Docs/"):
                    continue

                if any(skip in rel_path for skip in skip_patterns):
                    continue

                content = md_file.read_text(encoding="utf-8", errors="ignore")

                for line_no, line in enumerate(content.split("\n"), 1):
                    if pattern.search(line):
                        # Allow only if it's in a deprecation context
                        if "deprecat" not in line.lower() and "legacy" not in line.lower():
                            violations.append(
                                f"{md_file.relative_to(project_root)}:{line_no}: "
                                f"doc references .llama_runtime (use .clockwork_runtime)"
                            )
            except Exception:
                pass

    return violations


def run_runtime_root_gate(project_root: Path | str | None = None) -> dict:
    """
    Run runtime root gate. Enforce .clockwork_runtime as sole runtime root.
    Returns dict: pass (bool), violations (list), message (str).
    """
    root = Path(project_root).resolve() if project_root else _project_root()
    all_violations = []

    # Check 1: .llama_runtime stub constraint
    stub_violations = _check_llama_runtime_stub(root)
    all_violations.extend(stub_violations)

    # Check 2: Code references
    code_violations = _check_code_references(root)
    all_violations.extend(code_violations)

    # Check 3: Doc references
    doc_violations = _check_doc_references(root)
    all_violations.extend(doc_violations)

    passed = len(all_violations) == 0
    message = "All checks passed: .llama_runtime is stubbed, no code/doc references." if passed else (
        f"Runtime root gate FAILED: {len(all_violations)} violation(s) detected."
    )

    return {
        "pass": passed,
        "violations": all_violations,
        "message": message,
        "total_violations": len(all_violations),
    }


def main() -> int:
    """CLI entry point."""
    result = run_runtime_root_gate()
    if not result["pass"]:
        print(f"FAIL: {result['message']}", file=sys.stderr)
        for v in result["violations"]:
            print(f"  - {v}", file=sys.stderr)
        return 1
    print(result["message"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
