"""
Phase 15 — dead_file_scan: classify files that have lost their context.

Never deletes files. Always dry-run. Returns candidate list with confidence levels.
Governance rule: .claude/governance/file_lifecycle.md
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult

# Files in these sets are never flagged regardless of heuristic matches
_ALWAYS_ACTIVE_NAMES = {
    "CLAUDE.md",
    "execution_protocol.md",
    "file_lifecycle.md",
    "file_ownership.md",
    "decision_policy.md",
    "escalation_matrix.md",
    "workflow_triggers.md",
    "git_workflow.md",
    "mvp_development_standard.md",
    "rule_discovery.md",
    "self_improvement.md",
}

_DEFAULT_SCAN_PATHS = [
    "Docs/",
    "roadmaps/",
    "mvps/",
    ".claude-development/",
]

_TEXT_EXTENSIONS = {
    ".md", ".txt", ".yaml", ".yml", ".json", ".py", ".csv", ".rst",
}

# Matches markdown-style path references: [text](path), `path`, or bare path-like tokens
_PATH_REF_RE = re.compile(
    r'\[.*?\]\(([^)#\s]+\.[a-zA-Z]{1,6})\)'   # [label](path.ext)
    r'|`([^`]+\.[a-zA-Z]{1,6})`'               # `path.ext`
    r'|(?<!\w)([\w./\-]+\.[a-zA-Z]{2,6})(?!\w)' # bare path.ext (word-boundary guarded)
)


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _extract_path_refs(text: str, root: Path) -> list[Path]:
    """Return resolved Paths for non-URL references found in text."""
    refs: list[Path] = []
    for m in _PATH_REF_RE.finditer(text):
        candidate = m.group(1) or m.group(2) or m.group(3)
        if not candidate:
            continue
        if candidate.startswith(("http://", "https://", "ftp://")):
            continue
        # Skip things that look like domain names (e.g. example.com)
        if re.match(r'^[a-zA-Z0-9\-]+\.[a-zA-Z]{2,6}$', candidate):
            continue
        refs.append((root / candidate).resolve())
    return refs


def _collect_files(scan_paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for sp in scan_paths:
        if sp.is_dir():
            files.extend(f for f in sp.rglob("*") if f.is_file())
        elif sp.is_file():
            files.append(sp)
    return [f for f in files if f.suffix.lower() in _TEXT_EXTENSIONS]


class DeadFileScanSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        # Safety guard: this skill never deletes files
        if not kwargs.get("dry_run", True):
            return SkillResult(
                False,
                "dead_file_scan",
                error="dry_run=false is not permitted. This skill only reports; it never deletes files.",
            )

        root = Path(kwargs.get("root", context.working_directory)).resolve()
        scan_path_strs: list[str] = kwargs.get("scan_paths", _DEFAULT_SCAN_PATHS)
        scan_paths = [(root / p) for p in scan_path_strs]

        files = _collect_files(scan_paths)

        # Build SHA256 → [paths] index for duplicate detection
        sha_index: dict[str, list[Path]] = {}
        file_contents: dict[Path, bytes] = {}
        file_texts: dict[Path, str] = {}

        for f in files:
            try:
                raw = f.read_bytes()
                h = _sha256(raw)
                sha_index.setdefault(h, []).append(f)
                file_contents[f] = raw
                file_texts[f] = raw.decode("utf-8", errors="replace")
            except Exception:
                pass

        candidates: list[dict] = []

        for f in files:
            if f.name in _ALWAYS_ACTIVE_NAMES:
                continue

            text = file_texts.get(f, "")
            raw = file_contents.get(f, b"")
            if not text:
                continue

            reason: str | None = None
            confidence = "low"

            # Heuristic 1: Superseded / archived header comment
            if re.search(
                r"<!--\s*SUPERSEDED|>\s*SUPERSEDED:|>\s*ARCHIVED|>\s*RETIRED:",
                text,
                re.IGNORECASE,
            ):
                reason = "superseded_header"
                confidence = "high"

            # Heuristic 2: Exact content duplicate of another file
            elif len(sha_index.get(_sha256(raw), [])) > 1:
                duplicates = [
                    str(p) for p in sha_index[_sha256(raw)] if p != f
                ]
                reason = f"duplicate_content:{duplicates[0]}"
                confidence = "high"

            # Heuristic 3: Orphaned pointer stub (≤5 non-empty lines, only → or > refs)
            elif (
                sum(1 for line in text.splitlines() if line.strip()) <= 5
                and re.search(r"[→>]\s*\S+", text)
            ):
                reason = "orphaned_pointer"
                confidence = "medium"

            # Heuristic 4: Dead references (>50% of path refs point to missing files)
            else:
                refs = _extract_path_refs(text, root)
                if refs:
                    broken = [r for r in refs if not r.exists()]
                    ratio = len(broken) / len(refs)
                    if ratio > 0.5:
                        reason = f"dead_references:{len(broken)}/{len(refs)}"
                        confidence = "medium" if ratio < 0.8 else "high"

            if reason:
                candidates.append({
                    "path": str(f.relative_to(root)),
                    "reason": reason,
                    "confidence": confidence,
                })

        high_count = sum(1 for c in candidates if c["confidence"] == "high")

        return SkillResult(
            True,
            "dead_file_scan",
            data={
                "candidates": candidates,
                "candidate_count": len(candidates),
                "high_confidence_count": high_count,
            },
        )
