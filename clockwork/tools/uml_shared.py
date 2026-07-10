from __future__ import annotations

import ast
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

SUPPORTED_SUFFIXES = {
    ".py": "python",
    ".pyi": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c": "c",
    ".hpp": "cpp",
    ".hh": "cpp",
    ".h": "c",
    ".go": "go",
    ".rs": "rust",
    ".php": "php",
}

EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    "dist",
    "build",
    "Binaries",
    "Intermediate",
    "Saved",
    "DerivedDataCache",
}

MAX_TEXT_BYTES = 1_500_000
MAX_DIAGRAM_NODES = 42
MAX_CLASS_NODES = 28
MAX_METHODS_PER_CLASS = 8

IMPORT_RE = re.compile(r"(?:import|from|using|use|include)\s+[<\"]?([A-Za-z0-9_./\\:-]+)")
JS_IMPORT_RE = re.compile(r"import\s+.*?from\s+[\"']([^\"']+)[\"']")
CPP_INCLUDE_RE = re.compile(r"#include\s+[<\"]([^>\"]+)[>\"]")
PY_RELATIVE_RE = re.compile(r"^\.+")
CLASS_RE = re.compile(
    r"(?m)^\s*(?:export\s+)?(?:abstract\s+)?(class|struct|interface|enum)\s+([A-Za-z_][A-Za-z0-9_]*)"
    r"(?:\s+(?:extends|implements|:|public)\s+([^\{\n]+))?"
)


@dataclass(slots=True)
class ClassInfo:
    name: str
    module_id: str
    file_path: str
    language: str
    kind: str = "class"
    bases: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ModuleInfo:
    module_id: str
    file_path: str
    language: str
    relative_dir: str
    imports: list[str] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    function_count: int = 0
    line_count: int = 0
    internal_dependencies: list[str] = field(default_factory=list)
    reverse_dependencies: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RepoScan:
    repo_root: str
    module_count: int
    class_count: int
    languages: dict[str, int]
    modules: list[ModuleInfo]
    generated_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "repo_root": self.repo_root,
            "module_count": self.module_count,
            "class_count": self.class_count,
            "languages": self.languages,
            "modules": [
                {
                    **asdict(module),
                    "classes": [asdict(item) for item in module.classes],
                }
                for module in self.modules
            ],
            "generated_notes": list(self.generated_notes),
        }


class UmlSkillError(RuntimeError):
    pass


class PythonImportCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.imports: list[str] = []
        self.function_count = 0

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if node.level:
            prefix = "." * node.level
            self.imports.append(f"{prefix}{module}" if module else prefix)
        elif module:
            self.imports.append(module)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.function_count += 1
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.function_count += 1
        self.generic_visit(node)


class PythonClassCollector(ast.NodeVisitor):
    def __init__(self, module_id: str, file_path: str) -> None:
        self.module_id = module_id
        self.file_path = file_path
        self.classes: list[ClassInfo] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        bases = [_expr_to_name(base) for base in node.bases if _expr_to_name(base)]
        methods: list[str] = []
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(child.name)
        self.classes.append(
            ClassInfo(
                name=node.name,
                module_id=self.module_id,
                file_path=self.file_path,
                language="python",
                kind="class",
                bases=bases,
                methods=methods[:MAX_METHODS_PER_CLASS],
            )
        )
        self.generic_visit(node)


def _expr_to_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parts: list[str] = []
        current: ast.AST | None = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))
    if isinstance(node, ast.Subscript):
        return _expr_to_name(node.value)
    if isinstance(node, ast.Call):
        return _expr_to_name(node.func)
    return ""


def sanitize_alias(text: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_]+", "_", text).strip("_")
    return safe or "scope"


def should_skip_path(path: Path, repo_root: Path, include_tests: bool = False) -> bool:
    rel = path.relative_to(repo_root)
    if any(part in EXCLUDED_DIRS for part in rel.parts[:-1]):
        return True
    if not include_tests and any(part.lower() in {"tests", "test"} for part in rel.parts[:-1]):
        return True
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        return True
    if path.stat().st_size > MAX_TEXT_BYTES:
        return True
    return False


def build_module_id(repo_root: Path, file_path: Path) -> str:
    rel = file_path.relative_to(repo_root)
    no_suffix = rel.with_suffix("")
    if no_suffix.name == "__init__":
        no_suffix = no_suffix.parent
    if not str(no_suffix):
        return file_path.stem
    if file_path.suffix in {".py", ".pyi"}:
        parts = [part for part in no_suffix.parts if part]
        return ".".join(parts)
    return no_suffix.as_posix()


def parse_python_module(file_path: Path, module_id: str) -> tuple[list[str], list[ClassInfo], int, int, list[str]]:
    notes: list[str] = []
    try:
        text = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        notes.append(f"Ignored decoding issues in {file_path.name}.")
    line_count = text.count("\n") + 1
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        notes.append(f"Syntax parse skipped for {file_path.name}: {exc.msg}.")
        return [], [], 0, line_count, notes
    import_collector = PythonImportCollector()
    import_collector.visit(tree)
    class_collector = PythonClassCollector(module_id, str(file_path))
    class_collector.visit(tree)
    return import_collector.imports, class_collector.classes, import_collector.function_count, line_count, notes


def parse_generic_module(file_path: Path, module_id: str, language: str) -> tuple[list[str], list[ClassInfo], int, int, list[str]]:
    notes: list[str] = []
    try:
        text = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        notes.append(f"Ignored decoding issues in {file_path.name}.")
    line_count = text.count("\n") + 1
    imports: list[str] = []
    imports.extend(JS_IMPORT_RE.findall(text))
    imports.extend(CPP_INCLUDE_RE.findall(text))
    imports.extend(match.group(1) for match in IMPORT_RE.finditer(text))
    classes: list[ClassInfo] = []
    for kind, name, bases_blob in CLASS_RE.findall(text):
        bases = []
        if bases_blob:
            cleaned = bases_blob.replace("public", " ").replace("private", " ").replace("protected", " ")
            bases = [part.strip().split()[-1] for part in cleaned.split(",") if part.strip()]
        methods = _extract_method_names(text, name)
        classes.append(
            ClassInfo(
                name=name,
                module_id=module_id,
                file_path=str(file_path),
                language=language,
                kind=kind,
                bases=bases,
                methods=methods[:MAX_METHODS_PER_CLASS],
            )
        )
    function_count = len(_extract_top_level_functions(text, language))
    return imports, classes, function_count, line_count, notes


def _extract_method_names(text: str, class_name: str) -> list[str]:
    pattern = re.compile(rf"\b(?:virtual\s+)?(?:static\s+)?[A-Za-z_][A-Za-z0-9_:<>*&\s]*\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^;\n\)]*\)\s*(?:const\s*)?(?:\{{|;)" )
    names = []
    for match in pattern.finditer(text):
        method = match.group(1)
        if method != class_name and method not in names:
            names.append(method)
        if len(names) >= MAX_METHODS_PER_CLASS:
            break
    return names


def _extract_top_level_functions(text: str, language: str) -> list[str]:
    if language in {"javascript", "typescript"}:
        pattern = re.compile(r"(?m)^\s*(?:export\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)")
    elif language in {"cpp", "c", "java", "csharp", "go", "rust", "php"}:
        pattern = re.compile(r"(?m)^\s*[A-Za-z_][A-Za-z0-9_:<>*&\s]*\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^;\n\)]*\)\s*(?:\{|=>)")
    else:
        return []
    return [match.group(1) for match in pattern.finditer(text)]


def scan_repository(repo_root: Path, include_tests: bool = False) -> RepoScan:
    repo_root = repo_root.resolve()
    modules: list[ModuleInfo] = []
    notes: list[str] = []
    for file_path in sorted(repo_root.rglob("*")):
        if not file_path.is_file():
            continue
        if should_skip_path(file_path, repo_root, include_tests=include_tests):
            continue
        language = SUPPORTED_SUFFIXES[file_path.suffix.lower()]
        module_id = build_module_id(repo_root, file_path)
        if not module_id:
            module_id = file_path.stem
        relative_dir = file_path.relative_to(repo_root).parent.as_posix()
        if language == "python":
            imports, classes, function_count, line_count, local_notes = parse_python_module(file_path, module_id)
        else:
            imports, classes, function_count, line_count, local_notes = parse_generic_module(file_path, module_id, language)
        notes.extend(local_notes)
        modules.append(
            ModuleInfo(
                module_id=module_id,
                file_path=file_path.relative_to(repo_root).as_posix(),
                language=language,
                relative_dir=relative_dir,
                imports=_dedupe_keep_order(imports),
                classes=classes,
                function_count=function_count,
                line_count=line_count,
            )
        )
    resolve_internal_dependencies(modules)
    languages = Counter(module.language for module in modules)
    class_count = sum(len(module.classes) for module in modules)
    return RepoScan(
        repo_root=str(repo_root),
        module_count=len(modules),
        class_count=class_count,
        languages=dict(sorted(languages.items())),
        modules=modules,
        generated_notes=_dedupe_keep_order(notes),
    )


def _dedupe_keep_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        value = item.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def resolve_internal_dependencies(modules: list[ModuleInfo]) -> None:
    by_module_id = {module.module_id: module for module in modules}
    by_path = {module.file_path: module for module in modules}
    by_stem: dict[str, list[ModuleInfo]] = defaultdict(list)
    by_name: dict[str, list[ModuleInfo]] = defaultdict(list)
    for module in modules:
        stem = Path(module.file_path).stem
        by_stem[stem].append(module)
        by_name[module.module_id.split(".")[-1].split("/")[-1]].append(module)
    for module in modules:
        resolved: list[str] = []
        for item in module.imports:
            target = resolve_reference(item, module, by_module_id, by_path, by_stem, by_name)
            if target and target != module.module_id:
                resolved.append(target)
        module.internal_dependencies = sorted(set(resolved))
    reverse: dict[str, set[str]] = defaultdict(set)
    for module in modules:
        for dep in module.internal_dependencies:
            reverse[dep].add(module.module_id)
    for module in modules:
        module.reverse_dependencies = sorted(reverse.get(module.module_id, set()))


def resolve_reference(
    ref: str,
    module: ModuleInfo,
    by_module_id: dict[str, ModuleInfo],
    by_path: dict[str, ModuleInfo],
    by_stem: dict[str, list[ModuleInfo]],
    by_name: dict[str, list[ModuleInfo]],
) -> str | None:
    candidate = ref.strip().strip("\"'")
    if not candidate:
        return None
    candidate = candidate.replace("\\", "/")
    if candidate in by_module_id:
        return candidate
    if candidate in by_path:
        return by_path[candidate].module_id

    if module.language == "python":
        relative_match = PY_RELATIVE_RE.match(candidate)
        if relative_match:
            dots = len(relative_match.group(0))
            suffix = candidate[dots:]
            current_parts = module.module_id.split(".")
            if module.file_path.endswith("__init__.py"):
                base_parts = current_parts[:-max(dots - 1, 0)]
            else:
                base_parts = current_parts[:-dots]
            if suffix:
                base_parts += [part for part in suffix.split(".") if part]
            resolved = ".".join(base_parts)
            if resolved in by_module_id:
                return resolved
        else:
            parts = candidate.split(".")
            for i in range(len(parts), 0, -1):
                probe = ".".join(parts[:i])
                if probe in by_module_id:
                    return probe

    path_like = candidate.replace(".", "/")
    path_candidates = [candidate, path_like, f"{path_like}.py", f"{candidate}.py", f"{candidate}.ts", f"{candidate}.js"]
    for path_candidate in path_candidates:
        path_candidate = path_candidate.lstrip("./")
        if path_candidate in by_path:
            return by_path[path_candidate].module_id

    stem = Path(candidate).stem
    if stem in by_stem and len(by_stem[stem]) == 1:
        return by_stem[stem][0].module_id
    name = candidate.split("/")[-1].split(".")[-1]
    if name in by_name and len(by_name[name]) == 1:
        return by_name[name][0].module_id
    return None


def rank_directories(scan: RepoScan, scope_prefix: str = "") -> list[dict[str, int | str]]:
    counts: dict[str, dict[str, int]] = defaultdict(lambda: {"module_count": 0, "class_count": 0, "line_count": 0})
    for module in scan.modules:
        rel_dir = module.relative_dir or "."
        if scope_prefix and not rel_dir.startswith(scope_prefix):
            continue
        key = rel_dir.split("/")[0] if rel_dir != "." else "."
        counts[key]["module_count"] += 1
        counts[key]["class_count"] += len(module.classes)
        counts[key]["line_count"] += module.line_count
    rows = [{"path": key, **value} for key, value in counts.items()]
    rows.sort(key=lambda item: (-item["module_count"], -item["class_count"], str(item["path"])))
    return rows


def build_catalog(scan: RepoScan) -> dict:
    classes = [class_info for module in scan.modules for class_info in module.classes]
    class_rows = [
        {
            "name": class_info.name,
            "module_id": class_info.module_id,
            "file_path": class_info.file_path,
            "language": class_info.language,
            "bases": class_info.bases,
            "method_count": len(class_info.methods),
        }
        for class_info in sorted(classes, key=lambda item: (item.module_id, item.name))
    ]
    module_rows = [
        {
            "module_id": module.module_id,
            "file_path": module.file_path,
            "language": module.language,
            "relative_dir": module.relative_dir,
            "imports": module.imports,
            "internal_dependencies": module.internal_dependencies,
            "reverse_dependencies": module.reverse_dependencies,
            "class_count": len(module.classes),
            "function_count": module.function_count,
            "line_count": module.line_count,
        }
        for module in scan.modules
    ]
    return {
        "summary": {
            "repo_root": scan.repo_root,
            "module_count": scan.module_count,
            "class_count": scan.class_count,
            "languages": scan.languages,
        },
        "directories": rank_directories(scan),
        "modules": module_rows,
        "classes": class_rows,
        "notes": scan.generated_notes,
    }


def find_scope_modules(scan: RepoScan, scope_kind: str, target: str | None) -> list[ModuleInfo]:
    if scope_kind == "repo" or not target:
        return list(scan.modules)

    target = target.strip().strip("/")
    if scope_kind == "directory":
        prefix = target.rstrip("/")
        return [module for module in scan.modules if module.file_path.startswith(prefix) or module.relative_dir.startswith(prefix)]

    if scope_kind == "module":
        normalized = target.replace("\\", "/")
        hits = [module for module in scan.modules if module.module_id == target or module.file_path == normalized]
        if hits:
            return hits
        return [module for module in scan.modules if module.module_id.endswith(target) or module.file_path.endswith(normalized)]

    if scope_kind == "symbol":
        symbol = target.split("::")[-1].split(".")[-1]
        hits = [module for module in scan.modules if any(class_info.name == symbol for class_info in module.classes)]
        if hits:
            return hits
        return [module for module in scan.modules if module.module_id.endswith(target)]

    raise UmlSkillError(f"Unknown scope_kind: {scope_kind}")


def expand_focus_modules(scan: RepoScan, base_modules: list[ModuleInfo], depth: int = 1) -> list[ModuleInfo]:
    by_module_id = {module.module_id: module for module in scan.modules}
    selected = {module.module_id for module in base_modules}
    frontier = set(selected)
    for _ in range(max(depth, 0)):
        next_frontier: set[str] = set()
        for module_id in frontier:
            module = by_module_id.get(module_id)
            if module is None:
                continue
            next_frontier.update(module.internal_dependencies)
            next_frontier.update(module.reverse_dependencies)
        next_frontier -= selected
        if not next_frontier:
            break
        selected.update(next_frontier)
        frontier = next_frontier
    return [by_module_id[module_id] for module_id in sorted(selected) if module_id in by_module_id]


def aggregate_groups(modules: list[ModuleInfo], group_by: str = "topdir") -> tuple[list[str], list[tuple[str, str, int]]]:
    membership: dict[str, str] = {}
    for module in modules:
        if group_by == "directory":
            key = module.relative_dir or "."
        else:
            rel_dir = module.relative_dir or "."
            key = rel_dir.split("/")[0] if rel_dir != "." else "."
        membership[module.module_id] = key
    groups = sorted(set(membership.values()))[:MAX_DIAGRAM_NODES]
    edge_counter: Counter[tuple[str, str]] = Counter()
    allowed = set(groups)
    for module in modules:
        source = membership[module.module_id]
        if source not in allowed:
            continue
        for dep in module.internal_dependencies:
            target = membership.get(dep)
            if target and target in allowed and target != source:
                edge_counter[(source, target)] += 1
    edges = [(src, dst, count) for (src, dst), count in sorted(edge_counter.items())]
    return groups, edges


def render_component_plantuml(title: str, modules: list[ModuleInfo], group_by: str = "topdir") -> str:
    groups, edges = aggregate_groups(modules, group_by=group_by)
    lines = ["@startuml", f"title {title}", "skinparam componentStyle rectangle"]
    if not groups:
        lines.append('component "empty scope" as empty_scope')
    else:
        for group in groups:
            alias = sanitize_alias(group)
            label = group or "."
            lines.append(f'component "{label}" as {alias}')
        for src, dst, count in edges:
            lines.append(f"{sanitize_alias(src)} --> {sanitize_alias(dst)} : {count}")
    lines.append("@enduml")
    return "\n".join(lines) + "\n"


def render_dependency_mermaid(title: str, modules: list[ModuleInfo]) -> str:
    limited_modules = sorted(modules, key=lambda item: (-len(item.internal_dependencies), item.module_id))[:MAX_DIAGRAM_NODES]
    allowed = {module.module_id for module in limited_modules}
    lines = [f"%% {title}", "flowchart LR"]
    if not limited_modules:
        lines.append("  empty_scope[empty scope]")
        return "\n".join(lines) + "\n"
    for module in limited_modules:
        alias = sanitize_alias(module.module_id)
        label = module.module_id.replace('"', "'")
        lines.append(f'  {alias}["{label}"]')
    for module in limited_modules:
        src = sanitize_alias(module.module_id)
        for dep in module.internal_dependencies:
            if dep in allowed:
                lines.append(f"  {src} --> {sanitize_alias(dep)}")
    return "\n".join(lines) + "\n"


def render_class_plantuml(title: str, modules: list[ModuleInfo], include_methods: bool = False) -> str:
    classes = [class_info for module in modules for class_info in module.classes]
    classes = sorted(classes, key=lambda item: (item.module_id, item.name))[:MAX_CLASS_NODES]
    class_names = {item.name for item in classes}
    lines = ["@startuml", f"title {title}", "hide empty members"]
    if not classes:
        lines.extend(['class "NoClassesFound"'])
    else:
        for class_info in classes:
            alias = sanitize_alias(f"{class_info.module_id}_{class_info.name}")
            header = class_info.kind if class_info.kind in {"interface", "enum"} else "class"
            lines.append(f'{header} "{class_info.name}" as {alias} {{')
            if include_methods:
                for method in class_info.methods[:MAX_METHODS_PER_CLASS]:
                    lines.append(f"  +{method}()")
            lines.append("}")
            lines.append(f'note right of {alias}\n{class_info.module_id}\nend note')
        by_name = {item.name: item for item in classes}
        for class_info in classes:
            src_alias = sanitize_alias(f"{class_info.module_id}_{class_info.name}")
            for base in class_info.bases:
                base_name = base.split(".")[-1]
                if base_name in by_name and base_name in class_names:
                    base_alias = sanitize_alias(f"{by_name[base_name].module_id}_{base_name}")
                    lines.append(f"{base_alias} <|-- {src_alias}")
    lines.append("@enduml")
    return "\n".join(lines) + "\n"


def build_scope_summary(scope_kind: str, target: str | None, modules: list[ModuleInfo]) -> dict:
    classes = sum(len(module.classes) for module in modules)
    return {
        "scope_kind": scope_kind,
        "target": target or "repo",
        "module_count": len(modules),
        "class_count": classes,
        "languages": dict(sorted(Counter(module.language for module in modules).items())),
        "modules": [module.module_id for module in modules],
    }


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def render_markdown_index(title: str, description: str, summary: dict, files: list[str], notes: list[str] | None = None) -> str:
    lines = [f"# {title}", "", description, "", "## Scope Summary", ""]
    for key, value in summary.items():
        if isinstance(value, list):
            lines.append(f"- **{key}**: {', '.join(str(item) for item in value[:20])}")
        else:
            lines.append(f"- **{key}**: {value}")
    lines.extend(["", "## Files", ""])
    for file_name in files:
        lines.append(f"- `{file_name}`")
    if notes:
        lines.extend(["", "## Notes", ""])
        for note in notes:
            lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)
