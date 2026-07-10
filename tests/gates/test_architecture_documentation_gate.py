from pathlib import Path

from clockwork.tools.gates import check_architecture_docs

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_architecture_documentation_gate():
    violations = check_architecture_docs(REPO_ROOT)
    assert violations == [], "\n".join(violations)
