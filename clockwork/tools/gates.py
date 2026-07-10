"""Architecture documentation gate shared by pytest and the MCP server."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

SAD_REQUIRED_KEYS = ("id", "status", "type", "owns-adrs", "uml-package")
ADR_REQUIRED_KEYS = ("id", "status", "date", "domain")
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
ADR_ID_PATTERN = re.compile(r"ADR-CW-\d{4}")


def _frontmatter(text: str) -> dict | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def _check_links(md_file: Path, repo_root: Path, violations: list[str]) -> None:
    text = md_file.read_text(encoding="utf-8")
    for target in LINK_PATTERN.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean = target.split("#", 1)[0]
        if not clean:
            continue
        resolved = (md_file.parent / clean).resolve()
        if not resolved.exists():
            violations.append(f"{md_file.relative_to(repo_root)}: broken link -> {target}")


def check_architecture_docs(repo_root: str | Path) -> list[str]:
    repo_root = Path(repo_root).resolve()
    violations: list[str] = []

    adr_dir = repo_root / "docs" / "ADR"
    catalog_file = adr_dir / "ADR-CATALOG.md"
    catalog_text = catalog_file.read_text(encoding="utf-8") if catalog_file.exists() else ""
    catalog_ids = set(ADR_ID_PATTERN.findall(catalog_text))

    adr_files = sorted(adr_dir.glob("adr-cw-*.md")) if adr_dir.exists() else []
    adr_ids_on_disk: set[str] = set()
    for adr in adr_files:
        text = adr.read_text(encoding="utf-8")
        meta = _frontmatter(text)
        if meta is None:
            violations.append(f"{adr.name}: missing or invalid YAML frontmatter")
            continue
        for key in ADR_REQUIRED_KEYS:
            if key not in meta:
                violations.append(f"{adr.name}: frontmatter missing key '{key}'")
        adr_id = str(meta.get("id", ""))
        if adr_id:
            adr_ids_on_disk.add(adr_id)
            if adr_id not in catalog_ids:
                violations.append(f"{adr.name}: {adr_id} not registered in catalog")
        if "```mermaid" not in text:
            violations.append(f"{adr.name}: no mermaid diagram")
        _check_links(adr, repo_root, violations)

    for cataloged in sorted(catalog_ids - adr_ids_on_disk):
        violations.append(f"ADR-CATALOG.md: {cataloged} listed but no ADR file found")

    arch_dir = repo_root / "docs" / "architecture"
    sad_files = sorted(arch_dir.rglob("architecture.md")) if arch_dir.exists() else []
    for sad in sad_files:
        text = sad.read_text(encoding="utf-8")
        meta = _frontmatter(text)
        rel = sad.relative_to(repo_root)
        if meta is None:
            violations.append(f"{rel}: missing or invalid YAML frontmatter")
            continue
        for key in SAD_REQUIRED_KEYS:
            if key not in meta:
                violations.append(f"{rel}: frontmatter missing key '{key}'")
        for owned in meta.get("owns-adrs") or []:
            if str(owned) not in catalog_ids:
                violations.append(f"{rel}: owns-adrs entry {owned} not in catalog")
        uml_package = str(meta.get("uml-package", ""))
        if uml_package and not (repo_root / uml_package).is_dir():
            violations.append(f"{rel}: uml-package '{uml_package}' does not exist")
        _check_links(sad, repo_root, violations)

    components_dir = repo_root / "UML" / "Components"
    if components_dir.exists():
        for package in sorted(p for p in components_dir.iterdir() if p.is_dir()):
            for required in ("README.md", "TRACEABILITY.md"):
                if not (package / required).exists():
                    violations.append(f"UML/Components/{package.name}: missing {required}")

    return violations
