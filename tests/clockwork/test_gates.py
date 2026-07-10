from pathlib import Path

from clockwork.tools.gates import check_architecture_docs

ADR_OK = """---
id: ADR-CW-0001
status: accepted
date: 2026-07-10
domain: core
---

# ADR-CW-0001: Test

## Diagrams

```mermaid
flowchart LR
    A --> B
```
"""

SAD_OK = """---
id: SAD-CW-TEST
status: accepted
type: project-sad
owns-adrs:
  - ADR-CW-0001
uml-package: UML/Components/test-core
links:
  - ../../ADR/ADR-CATALOG.md
---

# Test Architecture
"""


def make_docs_repo(tmp_path: Path) -> Path:
    adr_dir = tmp_path / "docs" / "ADR"
    sad_dir = tmp_path / "docs" / "architecture" / "core"
    uml_dir = tmp_path / "UML" / "Components" / "test-core"
    adr_dir.mkdir(parents=True)
    sad_dir.mkdir(parents=True)
    uml_dir.mkdir(parents=True)
    (adr_dir / "ADR-CATALOG.md").write_text(
        "# ADR Catalog\n\n| ID | Title | Domain | Status | File |\n"
        "|---|---|---|---|---|\n"
        "| ADR-CW-0001 | Test | core | accepted | "
        "[adr-cw-0001-test.md](adr-cw-0001-test.md) |\n",
        encoding="utf-8",
    )
    (adr_dir / "adr-cw-0001-test.md").write_text(ADR_OK, encoding="utf-8")
    (sad_dir / "architecture.md").write_text(SAD_OK, encoding="utf-8")
    (uml_dir / "README.md").write_text("# test-core\n", encoding="utf-8")
    (uml_dir / "TRACEABILITY.md").write_text("# Traceability\n", encoding="utf-8")
    return tmp_path


def test_clean_docs_repo_has_no_violations(tmp_path):
    repo = make_docs_repo(tmp_path)
    assert check_architecture_docs(repo) == []


def test_uncataloged_adr_is_reported(tmp_path):
    repo = make_docs_repo(tmp_path)
    adr = repo / "docs" / "ADR" / "adr-cw-0002-extra.md"
    adr.write_text(ADR_OK.replace("ADR-CW-0001", "ADR-CW-0002"), encoding="utf-8")
    violations = check_architecture_docs(repo)
    assert any("ADR-CW-0002 not registered" in v for v in violations)


def test_adr_without_mermaid_is_reported(tmp_path):
    repo = make_docs_repo(tmp_path)
    adr = repo / "docs" / "ADR" / "adr-cw-0001-test.md"
    adr.write_text(ADR_OK.replace("```mermaid", "```text"), encoding="utf-8")
    violations = check_architecture_docs(repo)
    assert any("no mermaid diagram" in v for v in violations)


def test_sad_unknown_owned_adr_is_reported(tmp_path):
    repo = make_docs_repo(tmp_path)
    sad = repo / "docs" / "architecture" / "core" / "architecture.md"
    sad.write_text(SAD_OK.replace("ADR-CW-0001", "ADR-CW-9999"), encoding="utf-8")
    violations = check_architecture_docs(repo)
    assert any("ADR-CW-9999 not in catalog" in v for v in violations)


def test_broken_links_are_reported(tmp_path):
    repo = make_docs_repo(tmp_path)
    adr = repo / "docs" / "ADR" / "adr-cw-0001-test.md"
    adr.write_text(ADR_OK + "\nSee [missing](does-not-exist.md).\n", encoding="utf-8")
    violations = check_architecture_docs(repo)
    assert any("does-not-exist.md" in v for v in violations)


def test_sad_uml_package_must_exist(tmp_path):
    repo = make_docs_repo(tmp_path)
    sad = repo / "docs" / "architecture" / "core" / "architecture.md"
    sad.write_text(
        SAD_OK.replace("UML/Components/test-core", "UML/Components/ghost"),
        encoding="utf-8",
    )
    violations = check_architecture_docs(repo)
    assert any("uml-package" in v and "ghost" in v for v in violations)
