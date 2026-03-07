"""Phase 16 — dependency_graph: map run_manifest_skill() call chains."""
from __future__ import annotations

import re
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult

# Matches: run_manifest_skill("skill_id", ...) or run_manifest_skill({'skill_id': 'foo', ...})
_CALL_RE = re.compile(
    r'run_manifest_skill\s*\(\s*[{"\'].*?["\']skill_id["\']?\s*[:\s]+["\']([a-z_]+)["\']'
    r'|run_manifest_skill\s*\(\s*["\']([a-z_]+)["\']',
    re.DOTALL,
)


def _extract_calls(text: str) -> list[str]:
    results = []
    for m in _CALL_RE.finditer(text):
        skill_id = m.group(1) or m.group(2)
        if skill_id:
            results.append(skill_id)
    return results


def _scan_file(path: Path) -> list[tuple[str, str]]:
    """Return list of (caller_id, callee_id) pairs found in file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    callees = _extract_calls(text)
    if not callees:
        return []
    caller = path.stem
    return [(caller, callee) for callee in callees]


class DependencyGraphSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        root = Path(kwargs.get("root", context.working_directory)).resolve()
        fmt = str(kwargs.get("format", "json")).lower()

        scan_dirs = [
            root / ".claude" / "skills",
            root / ".claude" / "tasks",
        ]

        edges_raw: list[tuple[str, str, str]] = []  # (from, to, via)
        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
            for py_file in scan_dir.rglob("*.py"):
                pairs = _scan_file(py_file)
                for caller, callee in pairs:
                    via = str(py_file.relative_to(root))
                    edges_raw.append((caller, callee, via))

        nodes = sorted({e[0] for e in edges_raw} | {e[1] for e in edges_raw})
        edges = [{"from": e[0], "to": e[1], "via": e[2]} for e in edges_raw]

        data: dict = {
            "nodes": nodes,
            "edges": edges,
            "edge_count": len(edges),
        }

        if fmt == "markdown":
            from collections import defaultdict
            adj: dict[str, list[str]] = defaultdict(list)
            for e in edges_raw:
                adj[e[0]].append(e[1])
            lines = ["# Skill Dependency Graph", ""]
            for caller in sorted(adj):
                callees_str = ", ".join(sorted(set(adj[caller])))
                lines.append(f"- **{caller}** → {callees_str}")
            data["graph_text"] = "\n".join(lines) + "\n"

        return SkillResult(True, "dependency_graph", data=data)
