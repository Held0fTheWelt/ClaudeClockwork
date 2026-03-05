"""
telemetry_writer.py — Minimal, stdlib-only telemetry writer for Clockwork runs.

Appends a single JSONL event line to:
  .claude-performance/events/<run_id>.jsonl

Each line schema:
  {
    "ts":                "<ISO8601>",
    "run_id":            "<str>",
    "role":              "<str>",      # e.g. worker, teamlead, judge
    "model":             "<str>",      # e.g. claude-sonnet-4-6
    "task":              "<str>",      # short task label
    "prompt_tokens":     <int>,
    "completion_tokens": <int>,
    "total_tokens":      <int>
  }

CLI usage:
  python telemetry_writer.py <run_id> <role> <model> <task> <prompt_tokens> <completion_tokens>

Example:
  python telemetry_writer.py mvp06 worker claude-sonnet-4-6 "implement telemetry" 1200 400
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Default output root, relative to this file's location (repo root is two levels up).
_DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / ".claude-performance" / "events"


def write_event(
    run_id: str,
    role: str,
    model: str,
    task: str,
    prompt_tokens: int,
    completion_tokens: int,
    output_dir: Path | None = None,
) -> Path:
    """Append a single telemetry event to the run's JSONL file.

    Parameters
    ----------
    run_id:            Identifier for the run (used as filename stem).
    role:              Agent role (e.g. 'worker', 'teamlead', 'judge').
    model:             Model identifier string.
    task:              Short, human-readable task label.
    prompt_tokens:     Number of prompt/input tokens consumed.
    completion_tokens: Number of completion/output tokens produced.
    output_dir:        Directory to write JSONL files into.
                       Defaults to .claude-performance/events/ relative to repo root.

    Returns
    -------
    Path to the JSONL file that was written.
    """
    if output_dir is None:
        output_dir = _DEFAULT_OUTPUT_DIR

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "role": role,
        "model": model,
        "task": task,
        "prompt_tokens": int(prompt_tokens),
        "completion_tokens": int(completion_tokens),
        "total_tokens": int(prompt_tokens) + int(completion_tokens),
    }

    target = output_dir / f"{run_id}.jsonl"
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")

    return target


def _parse_args(argv: list[str]) -> dict:
    """Parse and validate CLI arguments."""
    usage = (
        "Usage: python telemetry_writer.py "
        "<run_id> <role> <model> <task> <prompt_tokens> <completion_tokens>"
    )
    if len(argv) != 7:
        print(usage, file=sys.stderr)
        sys.exit(1)

    _, run_id, role, model, task, raw_prompt, raw_completion = argv
    try:
        prompt_tokens = int(raw_prompt)
        completion_tokens = int(raw_completion)
    except ValueError:
        print(
            f"Error: prompt_tokens and completion_tokens must be integers, "
            f"got {raw_prompt!r} and {raw_completion!r}",
            file=sys.stderr,
        )
        sys.exit(1)

    return {
        "run_id": run_id,
        "role": role,
        "model": model,
        "task": task,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }


if __name__ == "__main__":
    kwargs = _parse_args(sys.argv)
    written_to = write_event(**kwargs)
    print(f"Event written to: {written_to}")
