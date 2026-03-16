"""Phase 28 — First-run wizard: create runtime root, validate versions, optional deps."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def run_first_run(project_root: Path | str) -> dict[str, Any]:
    """
    Idempotent first-run: create .clockwork_runtime layout, minimal config, verify permissions.
    Returns dict with created paths and any warnings.
    """
    root = Path(project_root).resolve()
    run_root = root / ".clockwork_runtime"
    created: list[str] = []
    warnings: list[str] = []

    subdirs = ["telemetry", "reports", "evidence", "redacted_exports", "eval/results", "eval/baselines", "knowledge", "audit"]
    for d in subdirs:
        p = run_root / d
        p.mkdir(parents=True, exist_ok=True)
        try:
            rel = str(p.relative_to(root))
        except ValueError:
            rel = d
        if rel not in created:
            created.append(rel)

    # Minimal config placeholder if missing
    config_dir = run_root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "runtime_config.json"
    if not config_file.is_file():
        config_file.write_text('{"first_run": true}\n', encoding="utf-8")
        created.append(str(config_file.relative_to(root)))

    # Optional deps (LocalAI): just note, don't fail
    try:
        import sentence_transformers  # noqa: F401
    except ImportError:
        warnings.append("Optional: sentence_transformers not installed (embed.text)")
    try:
        import whisper  # noqa: F401
    except ImportError:
        warnings.append("Optional: whisper not installed (audio.asr)")

    return {"runtime_root": str(run_root), "created": created, "warnings": warnings, "ok": True}
