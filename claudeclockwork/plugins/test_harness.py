"""Phase 40 — Plugin test harness: smoke + policy; reject missing tests in strict mode."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def has_smoke_test(manifest: dict[str, Any], plugin_dir: Path | str) -> bool:
    """True if plugin declares and has smoke test, or has test_smoke.py / tests/."""
    d = Path(plugin_dir).resolve()
    if (d / "test_smoke.py").exists() or (d / "tests").is_dir():
        return True
    smoke = manifest.get("smoke_test") or (manifest.get("test") or {}).get("smoke") if isinstance(manifest.get("test"), dict) else None
    if not smoke:
        return False
    path = smoke.get("path") if isinstance(smoke, dict) else (smoke if isinstance(smoke, str) else None)
    return bool(path and (d / path).exists())


def run_smoke(plugin_dir: Path | str) -> dict[str, Any]:
    """Run smoke test if present. Returns {passed, output}."""
    d = Path(plugin_dir).resolve()
    test_file = d / "test_smoke.py"
    if not test_file.exists():
        return {"passed": False, "output": "no smoke test"}
    import subprocess
    r = subprocess.run(
        ["python", "-m", "pytest", str(test_file), "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=d,
    )
    return {"passed": r.returncode == 0, "output": r.stdout + r.stderr}
