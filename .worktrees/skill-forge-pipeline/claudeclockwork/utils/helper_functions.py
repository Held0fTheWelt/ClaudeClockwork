"""Helper functions for autonomous Ollama agents."""

import subprocess
import logging
from pathlib import Path
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(handler)


def write_file(path: str, content: str) -> bool:
    """Write content to file."""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        logger.info(f"✓ Wrote {len(content)} chars to {path}")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to write {path}: {e}")
        return False


def run_pytest(test_file: str, cov_threshold: int = 85) -> tuple:
    """Run pytest on test file."""
    try:
        result = subprocess.run(
            ["pytest", test_file, f"--cov=app", f"--cov-fail-under={cov_threshold}", "-v"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd="/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows/backend"
        )

        coverage_pct = _extract_coverage(result.stdout + result.stderr)
        passed = result.returncode == 0

        logger.info(f"{'✓' if passed else '✗'} pytest {test_file}: {coverage_pct}% coverage")
        if not passed:
            logger.info(f"Output:\n{result.stdout}\n{result.stderr}")

        return passed, coverage_pct
    except subprocess.TimeoutExpired:
        logger.error(f"✗ pytest timeout after 300s")
        return False, 0.0
    except Exception as e:
        logger.error(f"✗ pytest failed: {e}")
        return False, 0.0


def _extract_coverage(output: str) -> float:
    """Extract coverage percentage."""
    match = re.search(r'(\d+)%', output)
    if match:
        return float(match.group(1))
    return 0.0


def run_existing_tests() -> float:
    """Run existing tests, return baseline coverage."""
    try:
        result = subprocess.run(
            ["pytest", "tests/", "--cov=app", "-q"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd="/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows/backend"
        )
        coverage = _extract_coverage(result.stdout + result.stderr)
        logger.info(f"Baseline coverage: {coverage}%")
        return coverage
    except Exception as e:
        logger.warning(f"Could not run baseline tests: {e}")
        return 0.0


def verify_coverage(before: float, after: float) -> bool:
    """Verify coverage didn't decrease."""
    delta = after - before
    passed = delta >= -1  # Allow 1% wiggle room
    logger.info(f"Coverage delta: {delta:+.1f}% ({before:.1f}% → {after:.1f}%)")
    return passed


def git_commit(files: list, message: str) -> bool:
    """Commit files to git (force-add for .ollama/)."""
    try:
        # Stage files with -f to force-add from .gitignored directories
        subprocess.run(
            ["git", "add", "-f"] + files,
            capture_output=True,
            check=True,
            cwd="/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows"
        )

        # Commit
        subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            check=True,
            cwd="/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows"
        )

        logger.info(f"✓ Committed {len(files)} files")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ git commit failed: {e.stderr.decode()}")
        return False
    except Exception as e:
        logger.error(f"✗ git commit failed: {e}")
        return False
