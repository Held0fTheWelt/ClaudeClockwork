from __future__ import annotations

import hashlib
import html
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from clockwork.tools.uml_shared import MAX_METHODS_PER_CLASS, RepoScan, sanitize_alias, write_json, write_text

MAX_LIST_ITEMS = 24
MAX_TOOLTIP_ITEMS = 5


def stable_slug(text: str) -> str:
    base = sanitize_alias(text).lower() or "item"
    digest = hashlib.md5(text.encode("utf-8")).hexdigest()[:8]
    return f"{base}-{digest}"



def tooltip_text(label: str, parts: Iterable[str]) -> str:
    compact = [str(part).strip() for part in parts if str(part).strip()]
    return label if not compact else f"{label} â€” " + " | ".join(compact[:MAX_TOOLTIP_ITEMS])



def infer_module_role(dep_count: int, inbound_count: int, class_count: int) -> str:
    if inbound_count >= 6 and dep_count >= 4:
        return "High-traffic coordination module with both fan-in and fan-out."
    if inbound_count >= 6:
        return "Shared dependency with strong fan-in from other modules."
    if dep_count >= 8:
        return "Orchestrator-like module with a broad dependency surface."
    if class_count >= 4:
        return "Model-heavy module with several class definitions."
    if dep_count == 0 and inbound_count == 0:
        return "Isolated leaf or utility module with little visible coupling."
    if dep_count == 0:
        return "Leaf implementation module without internal downstream dependencies."
    if inbound_count == 0:
        return "Entry-edge module with outward dependencies but little internal reuse."
    return "Connected implementation module inside the current dependency web."



def _expand_neighbors(scan: RepoScan, seed_ids: list[str], depth: int) -> list[str]:
    by_id = {module.module_id: module for module in scan.modules}
    selected = set(seed_ids)
    frontier = set(seed_ids)
    for _ in range(max(depth, 0)):
        next_frontier: set[str] = set()
        for module_id in frontier:
            module = by_id.get(module_id)
            if module is None:
                continue
            next_frontier.update(module.internal_dependencies)
            next_frontier.update(module.reverse_dependencies)
        next_frontier -= selected
        if not next_frontier:
            break
        selected.update(next_frontier)
        frontier = next_frontier
    return [item for item in sorted(selected) if item in by_id]



def _collect_symbol_derivations(scan: RepoScan) -> dict[str, list[str]]:
    base_to_children: dict[str, set[str]] = defaultdict(set)
    for module in scan.modules:
        for class_info in module.classes:
            key = f"{module.module_id}::{class_info.name}"
            for base in class_info.bases:
                base_to_children[base.split(".")[-1]].add(key)

    derived: dict[str, list[str]] = defaultdict(list)
    for module in scan.modules:
        for class_info in module.classes:
            current_key = f"{module.module_id}::{class_info.name}"
            for child in sorted(base_to_children.get(class_info.name, set())):
                if child != current_key:
                    derived[current_key].append(child)
    return {key: sorted(set(values)) for key, values in derived.items()}



def build_review_context(scan: RepoScan, neighbor_depth: int = 1, max_neighbors: int = 10) -> dict:
    modules_by_id = {module.module_id: module for module in scan.modules}
    derived = _collect_symbol_derivations(scan)

    directories_raw: dict[str, dict] = {}
    for module in scan.modules:
        path = module.relative_dir or "."
        payload = directories_raw.setdefault(
            path,
            {
                "path": path,
                "slug": stable_slug(f"directory::{path}"),
                "modules": [],
                "module_count": 0,
                "class_count": 0,
                "function_count": 0,
                "line_count": 0,
                "languages": Counter(),
            },
        )
        payload["modules"].append(module.module_id)
        payload["module_count"] += 1
        payload["class_count"] += len(module.classes)
        payload["function_count"] += module.function_count
        payload["line_count"] += module.line_count
        payload["languages"][module.language] += 1

    directories: list[dict] = []
    modules: list[dict] = []
    symbols: list[dict] = []
    tooltips: dict[str, str] = {}

    for path, payload in directories_raw.items():
        local_modules = [modules_by_id[module_id] for module_id in payload["modules"] if module_id in modules_by_id]
        hotspots = sorted(
            local_modules,
            key=lambda item: (len(item.reverse_dependencies), len(item.internal_dependencies), item.line_count),
            reverse=True,
        )[:6]
        entry = {
            "kind": "directory",
            "key": path,
            "slug": payload["slug"],
            "title": path,
            "summary": {
                "module_count": payload["module_count"],
                "class_count": payload["class_count"],
                "function_count": payload["function_count"],
                "line_count": payload["line_count"],
                "languages": dict(sorted(payload["languages"].items())),
            },
            "modules": sorted(payload["modules"])[:MAX_LIST_ITEMS],
            "hotspots": [item.module_id for item in hotspots],
            "notes": [
                "Directory scopes are useful for subsystem-level UML slices.",
                "Hotspots are ranked by reverse dependencies, dependency breadth, and size.",
            ],
        }
        entry["tooltip"] = tooltip_text(
            path,
            [
                f"modules {payload['module_count']}",
                f"classes {payload['class_count']}",
                f"lines {payload['line_count']}",
            ],
        )
        directories.append(entry)
        tooltips[f"directory::{path}"] = entry["tooltip"]

    for module in scan.modules:
        neighbor_ids = [item for item in _expand_neighbors(scan, [module.module_id], depth=neighbor_depth) if item != module.module_id][:max_neighbors]
        class_keys = [f"{module.module_id}::{class_info.name}" for class_info in module.classes]
        dep_count = len(module.internal_dependencies)
        inbound_count = len(module.reverse_dependencies)
        class_count = len(module.classes)
        entry = {
            "kind": "module",
            "key": module.module_id,
            "slug": stable_slug(f"module::{module.module_id}"),
            "title": module.module_id,
            "file_path": module.file_path,
            "relative_dir": module.relative_dir or ".",
            "language": module.language,
            "summary": {
                "class_count": class_count,
                "function_count": module.function_count,
                "line_count": module.line_count,
                "dependency_count": dep_count,
                "reverse_dependency_count": inbound_count,
            },
            "imports": module.imports[:MAX_LIST_ITEMS],
            "internal_dependencies": module.internal_dependencies[:MAX_LIST_ITEMS],
            "reverse_dependencies": module.reverse_dependencies[:MAX_LIST_ITEMS],
            "neighbor_modules": neighbor_ids,
            "classes": class_keys,
            "role_note": infer_module_role(dep_count, inbound_count, class_count),
        }
        entry["tooltip"] = tooltip_text(
            module.module_id,
            [module.language, f"deps {dep_count}", f"inbound {inbound_count}", f"classes {class_count}"],
        )
        modules.append(entry)
        tooltips[f"module::{module.module_id}"] = entry["tooltip"]

    for module in scan.modules:
        for class_info in module.classes:
            key = f"{module.module_id}::{class_info.name}"
            entry = {
                "kind": "symbol",
                "key": key,
                "slug": stable_slug(f"symbol::{key}"),
                "title": class_info.name,
                "module_id": module.module_id,
                "file_path": module.file_path,
                "language": class_info.language,
                "summary": {
                    "base_count": len(class_info.bases),
                    "method_count": len(class_info.methods),
                    "neighbor_module_count": len(module.internal_dependencies) + len(module.reverse_dependencies),
                    "derived_count": len(derived.get(key, [])),
                },
                "bases": class_info.bases[:MAX_LIST_ITEMS],
                "methods": class_info.methods[:MAX_METHODS_PER_CLASS],
                "neighbor_modules": sorted(set(module.internal_dependencies + module.reverse_dependencies))[:MAX_LIST_ITEMS],
                "derived_symbols": derived.get(key, [])[:MAX_LIST_ITEMS],
            }
            entry["tooltip"] = tooltip_text(
                key,
                [class_info.kind, f"methods {len(class_info.methods)}", f"bases {len(class_info.bases)}"],
            )
            symbols.append(entry)
            tooltips[f"symbol::{key}"] = entry["tooltip"]

    directories.sort(key=lambda item: (-item["summary"]["module_count"], item["title"]))
    modules.sort(key=lambda item: (-item["summary"]["reverse_dependency_count"], item["title"]))
    symbols.sort(key=lambda item: (item["module_id"], item["title"]))

    return {
        "summary": {
            "repo_root": scan.repo_root,
            "module_count": scan.module_count,
            "class_count": scan.class_count,
            "directory_count": len(directories),
            "languages": scan.languages,
            "neighbor_depth": neighbor_depth,
        },
        "directories": directories,
        "modules": modules,
        "symbols": symbols,
        "tooltips": tooltips,
        "notes": list(scan.generated_notes),
    }



def render_context_markdown(context_payload: dict) -> str:
    lines = [
        "# UML Review Context",
        "",
        "This bundle enriches UML review pages with scope-aware context cards and tooltip payloads.",
        "",
        "## Summary",
        "",
    ]
    for key, value in context_payload["summary"].items():
        lines.append(f"- **{key}**: {value}")
    lines.extend(["", "## Entity Sets", ""])
    lines.append(f"- directories: {len(context_payload['directories'])}")
    lines.append(f"- modules: {len(context_payload['modules'])}")
    lines.append(f"- symbols: {len(context_payload['symbols'])}")
    lines.append(f"- tooltips: {len(context_payload['tooltips'])}")
    if context_payload.get("notes"):
        lines.extend(["", "## Notes", ""])
        for note in context_payload["notes"]:
            lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)



def write_context_bundle(output_dir: Path, context_payload: dict) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    context_json = output_dir / "uml_review_context.json"
    tooltips_json = output_dir / "uml_review_tooltips.json"
    summary_md = output_dir / "README.md"
    write_json(context_json, context_payload)
    write_json(tooltips_json, context_payload["tooltips"])
    write_text(summary_md, render_context_markdown(context_payload))
    return {"context_json": str(context_json), "tooltips_json": str(tooltips_json), "summary_md": str(summary_md)}



def _split_label(text: str, max_width: int = 18, max_lines: int = 3) -> list[str]:
    if len(text) <= max_width:
        return [text]
    words = text.replace("/", " / ").replace("::", " :: ").split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
            if len(lines) >= max_lines - 1:
                break
    if current:
        lines.append(current)
    if lines and len(lines[-1]) > max_width:
        lines[-1] = lines[-1][: max_width - 1] + "â€¦"
    return lines[:max_lines]



def _render_relation_svg(center: str, nodes: list[str], edges: list[tuple[str, str]]) -> str:
    unique_nodes: list[str] = []
    for item in nodes:
        label = str(item).strip()
        if label and label not in unique_nodes:
            unique_nodes.append(label)
    if center in unique_nodes:
        unique_nodes.remove(center)
    unique_nodes.insert(0, center)

    width, height = 860, 430
    cx, cy = width / 2, height / 2
    radius = 145
    coords: dict[str, tuple[float, float]] = {center: (cx, cy)}
    orbit = unique_nodes[1:9]
    for index, label in enumerate(orbit):
        angle = (2 * math.pi * index / max(len(orbit), 1)) - math.pi / 2
        coords[label] = (cx + radius * math.cos(angle), cy + radius * math.sin(angle))

    def esc(value: str) -> str:
        return html.escape(value, quote=True)

    lines = [
        f'<svg class="relation-map" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Context map for {esc(center)}">',
        '<defs><filter id="softGlow"><feGaussianBlur stdDeviation="6" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>',
    ]
    for source, target in edges:
        if source not in coords or target not in coords:
            continue
        sx, sy = coords[source]
        tx, ty = coords[target]
        lines.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" class="relation-edge" />')
    for label, (x, y) in coords.items():
        radius_px = 50 if label == center else 36
        cls = "relation-node relation-center" if label == center else "relation-node"
        lines.append(f'<g class="{cls}" filter="url(#softGlow)">')
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius_px}" />')
        chunks = _split_label(label, max_width=18, max_lines=3 if label == center else 2)
        start_y = y - (len(chunks) - 1) * 8
        for idx, chunk in enumerate(chunks):
            lines.append(f'<text x="{x:.1f}" y="{start_y + idx * 16:.1f}" text-anchor="middle">{esc(chunk)}</text>')
        lines.append("</g>")
    lines.append("</svg>")
    return "".join(lines)



def _build_scope_preview(entity: dict) -> dict:
    if entity["kind"] == "directory":
        nodes = [entity["title"]] + entity.get("hotspots", [])[:6]
        edges = [(entity["title"], item) for item in entity.get("hotspots", [])[:6]]
        return {"center": entity["title"], "nodes": nodes, "edges": edges}
    if entity["kind"] == "module":
        nodes = [entity["title"]] + entity.get("internal_dependencies", [])[:5] + entity.get("reverse_dependencies", [])[:5]
        edges = [(entity["title"], item) for item in entity.get("internal_dependencies", [])[:5]]
        edges += [(item, entity["title"]) for item in entity.get("reverse_dependencies", [])[:5]]
        return {"center": entity["title"], "nodes": nodes, "edges": edges}
    bases = [item.split(".")[-1] for item in entity.get("bases", [])[:4]]
    derived = [item.split("::")[-1] for item in entity.get("derived_symbols", [])[:4]]
    nodes = [entity["key"], entity.get("module_id", "")] + bases + derived
    edges = [(item, entity["key"]) for item in bases] + [(entity["key"], item) for item in derived]
    if entity.get("module_id"):
        edges.append((entity["module_id"], entity["key"]))
    return {"center": entity["key"], "nodes": [item for item in nodes if item], "edges": edges}



def _guide_href(guide: dict, root_prefix: str = '..') -> tuple[str, str]:
    return f"{root_prefix}/guides/{guide['slug']}.html", f"guide::{guide['id']}"


def _page_shell(title: str, site_title: str, body: str, root_prefix: str, guide_payload: dict | None = None) -> str:
    guide_link = f'<a class="nav-link" href="{root_prefix}/guides/index.html">Guides</a>' if guide_payload and guide_payload.get('guides') else ''
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{html.escape(title)} Â· {html.escape(site_title)}</title>
  <link rel=\"stylesheet\" href=\"{root_prefix}/assets/app.css\">
</head>
<body>
  <div class=\"app-shell\">
    <aside class=\"sidebar\">
      <div class=\"brand-block\">
        <p class=\"eyebrow\">UML Review</p>
        <h1>{html.escape(site_title)}</h1>
        <p class=\"muted\">Explore repository structure, scope context, and local UML slices like a documentation website.</p>
      </div>
      <nav class=\"side-nav\">
        <a class=\"nav-link\" href=\"{root_prefix}/index.html\">Overview</a>
        {guide_link}
        <a class=\"nav-link\" href=\"{root_prefix}/directories/index.html\">Directories</a>
        <a class=\"nav-link\" href=\"{root_prefix}/modules/index.html\">Modules</a>
        <a class=\"nav-link\" href=\"{root_prefix}/symbols/index.html\">Symbols</a>
      </nav>
    </aside>
    <main class=\"main-pane\">{body}</main>
  </div>
  <div id=\"tooltip-root\" class=\"tooltip-root\" hidden></div>
  <script src=\"{root_prefix}/assets/app.js\"></script>
</body>
</html>
"""



def _metrics_grid(summary: dict) -> str:
    parts = ['<div class="metrics-grid">']
    for key, value in summary.items():
        display = json.dumps(value) if isinstance(value, dict) else str(value)
        parts.append(f'<div class="metric-card"><span class="metric-label">{html.escape(str(key))}</span><strong>{html.escape(display)}</strong></div>')
    parts.append("</div>")
    return "".join(parts)



def _module_href(context_payload: dict, module_id: str) -> tuple[str, str]:
    for module in context_payload["modules"]:
        if module["key"] == module_id:
            return f'../modules/{module["slug"]}.html', f'module::{module_id}'
    return "#", f"module::{module_id}"



def _symbol_href(context_payload: dict, symbol_key: str) -> tuple[str, str]:
    for symbol in context_payload["symbols"]:
        if symbol["key"] == symbol_key:
            return f'../symbols/{symbol["slug"]}.html', f'symbol::{symbol_key}'
    return "#", f"symbol::{symbol_key}"



def _symbol_name_href(context_payload: dict, current_module_id: str, symbol_name: str) -> tuple[str, str]:
    for symbol in context_payload["symbols"]:
        if symbol["module_id"] == current_module_id and symbol["title"] == symbol_name:
            return f'../symbols/{symbol["slug"]}.html', f'symbol::{symbol["key"]}'
    for symbol in context_payload["symbols"]:
        if symbol["title"] == symbol_name:
            return f'../symbols/{symbol["slug"]}.html', f'symbol::{symbol["key"]}'
    return "#", f"symbol::{current_module_id}::{symbol_name}"



def _list_block(title: str, items: list[str], href_builder) -> str:
    rows = [f'<section class="content-card"><h3>{html.escape(title)}</h3>']
    if not items:
        rows.append('<p class="muted">No entries in this slice.</p>')
    else:
        rows.append('<ul class="entity-list compact">')
        for item in items:
            href, tooltip_key = href_builder(item)
            rows.append(f'<li><a href="{html.escape(href)}" data-tooltip-key="{html.escape(tooltip_key)}">{html.escape(item)}</a></li>')
        rows.append("</ul>")
    rows.append("</section>")
    return "".join(rows)



def _overview_page(site_title: str, context_payload: dict, guide_payload: dict | None = None) -> str:
    body = [
        '<header class="page-header"><p class="eyebrow">Repository overview</p><h2>Review explorer</h2><p class="lead">Navigate the codebase through directories, modules, classes, and their local dependency context.</p></header>',
        _metrics_grid(context_payload["summary"]),
        '<section class="content-grid">',
        '<section class="content-card"><h3>Top directories</h3><ul class="entity-list">',
    ]
    for item in context_payload["directories"][:10]:
        body.append(f'<li><a href="directories/{item["slug"]}.html" data-tooltip-key="directory::{html.escape(item["key"])}">{html.escape(item["title"])}<span>{item["summary"]["module_count"]} modules</span></a></li>')
    body.append('</ul></section><section class="content-card"><h3>Hot modules</h3><ul class="entity-list">')
    for item in context_payload["modules"][:12]:
        body.append(f'<li><a href="modules/{item["slug"]}.html" data-tooltip-key="module::{html.escape(item["key"])}">{html.escape(item["title"])}<span>{item["summary"]["reverse_dependency_count"]} inbound</span></a></li>')
    body.append('</ul></section><section class="content-card"><h3>Class symbols</h3><ul class="entity-list">')
    for item in context_payload["symbols"][:12]:
        body.append(f'<li><a href="symbols/{item["slug"]}.html" data-tooltip-key="symbol::{html.escape(item["key"])}">{html.escape(item["title"])}<span>{html.escape(item["module_id"])}</span></a></li>')
    body.append('</ul></section></section>')
    if guide_payload and guide_payload.get('guides'):
        body.append('<section class="content-card"><h3>How it works</h3><div class="guide-grid">')
        for guide in guide_payload['guides'][:6]:
            body.append(f'<a class="guide-card" href="guides/{guide["slug"]}.html" data-tooltip-key="guide::{html.escape(guide["id"])}"><strong>{html.escape(guide["title"])}</strong><span>{html.escape(guide["summary"])}</span><em>{html.escape(guide["category"].title())}</em></a>')
        body.append('</div></section>')
    return _page_shell("Overview", site_title, "".join(body), ".", guide_payload=guide_payload)



def _entity_index_page(site_title: str, title: str, kind: str, items: list[dict], guide_payload: dict | None = None) -> str:
    tooltip_prefix = "directory" if kind == "Directories" else ("module" if kind == "Modules" else "symbol")
    rows = [
        f'<header class="page-header"><p class="eyebrow">{html.escape(kind)}</p><h2>{html.escape(title)}</h2><p class="lead">Search and open focused review pages for this entity type.</p></header>',
        '<section class="toolbar-card"><label class="search-label">Search <input id="entity-search" class="search-input" type="search" placeholder="Filter entities..."></label></section>',
        '<section class="content-card"><ul class="entity-list searchable-list">',
    ]
    for item in items:
        subtitle = item.get("file_path") or item.get("module_id") or json.dumps(item.get("summary", {}))
        rows.append(f'<li data-search-text="{html.escape((item["title"] + " " + str(subtitle)).lower())}"><a href="./{item["slug"]}.html" data-tooltip-key="{tooltip_prefix}::{html.escape(item["key"])}">{html.escape(item["title"])}<span>{html.escape(str(subtitle))}</span></a></li>')
    rows.append("</ul></section>")
    return _page_shell(title, site_title, "".join(rows), "..", guide_payload=guide_payload)




def _entity_page(site_title: str, entity: dict, context_payload: dict, guide_payload: dict | None = None) -> str:
    preview = _build_scope_preview(entity)
    preview_svg = _render_relation_svg(preview["center"], preview["nodes"], preview["edges"])
    body = [
        (
            f"<header class=\"page-header\"><p class=\"eyebrow\">{html.escape(entity['kind'].title())}</p>"
            f"<h2>{html.escape(entity['title'])}</h2>"
            f"<p class=\"lead\">Key: <code>{html.escape(entity['key'])}</code></p></header>"
        ),
        _metrics_grid(entity["summary"]),
        f'<section class="content-card"><h3>Context preview</h3>{preview_svg}</section>',
    ]
    if guide_payload and guide_payload.get('guides'):
        body.append('<section class="content-card"><h3>Guide shortcuts</h3><ul class="entity-list compact">')
        preferred = guide_payload['guides'][:3]
        for guide in preferred:
            body.append(f'<li><a href="../guides/{guide["slug"]}.html" data-tooltip-key="guide::{html.escape(guide["id"])}">{html.escape(guide["title"])}</a></li>')
        body.append('</ul></section>')
    if entity["kind"] == "directory":
        body.append(_list_block("Modules", entity.get("modules", []), lambda item: _module_href(context_payload, item)))
        body.append(_list_block("Hotspots", entity.get("hotspots", []), lambda item: _module_href(context_payload, item)))
    elif entity["kind"] == "module":
        body.append(f'<section class="content-card"><h3>Context note</h3><p>{html.escape(entity.get("role_note", ""))}</p></section>')
        body.append(_list_block("Internal dependencies", entity.get("internal_dependencies", []), lambda item: _module_href(context_payload, item)))
        body.append(_list_block("Reverse dependencies", entity.get("reverse_dependencies", []), lambda item: _module_href(context_payload, item)))
        body.append(_list_block("Classes", [item.split("::")[-1] for item in entity.get("classes", [])], lambda item: _symbol_name_href(context_payload, entity["key"], item)))
        body.append(_list_block("Neighbor modules", entity.get("neighbor_modules", []), lambda item: _module_href(context_payload, item)))
    else:
        body.append(_list_block("Base types", [item.split(".")[-1] for item in entity.get("bases", [])], lambda item: _symbol_name_href(context_payload, entity["module_id"], item)))
        body.append(_list_block("Methods", entity.get("methods", []), lambda item: ("#", f"symbol::{entity['key']}")))
        body.append(_list_block("Derived symbols", [item.split("::")[-1] for item in entity.get("derived_symbols", [])], lambda item: _symbol_name_href(context_payload, entity["module_id"], item)))
        body.append(_list_block("Neighbor modules", entity.get("neighbor_modules", []), lambda item: _module_href(context_payload, item)))
    return _page_shell(entity["title"], site_title, "".join(body), "..", guide_payload=guide_payload)





def _guide_index_page(site_title: str, guide_payload: dict) -> str:
    rows = [
        '<header class="page-header"><p class="eyebrow">Guides</p><h2>How it works</h2><p class="lead">Technical and functional guides generated from the repository structure and review data.</p></header>',
        '<section class="toolbar-card"><label class="search-label">Search <input id="entity-search" class="search-input" type="search" placeholder="Filter guides..."></label></section>',
        '<section class="content-card"><ul class="entity-list searchable-list">',
    ]
    for guide in guide_payload.get('guides', []):
        rows.append(
            f'<li data-search-text="{html.escape((guide["title"] + " " + guide["summary"] + " " + guide["category"]).lower())}"><a href="./{guide["slug"]}.html" data-tooltip-key="guide::{html.escape(guide["id"])}">{html.escape(guide["title"])}<span>{html.escape(guide["category"].title())}</span></a></li>'
        )
    rows.append('</ul></section>')
    return _page_shell('Guides', site_title, ''.join(rows), '..', guide_payload=guide_payload)



def _guide_related_block(title: str, items: list[str], href_builder) -> str:
    if not items:
        return ''
    rows = [f'<section class="content-card"><h3>{html.escape(title)}</h3><ul class="entity-list compact">']
    for item in items:
        href, tooltip_key = href_builder(item)
        rows.append(f'<li><a href="{html.escape(href)}" data-tooltip-key="{html.escape(tooltip_key)}">{html.escape(item)}</a></li>')
    rows.append('</ul></section>')
    return ''.join(rows)



def _guide_page(site_title: str, guide: dict, context_payload: dict, guide_payload: dict) -> str:
    body = [
        f'<header class="page-header"><p class="eyebrow">{html.escape(guide["category"].title())} guide</p><h2>{html.escape(guide["title"])}</h2><p class="lead">{html.escape(guide["summary"])}</p></header>',
        '<section class="content-grid">',
        f'<section class="metric-card"><span class="metric-label">Category</span><strong>{html.escape(guide["category"].title())}</strong></section>',
        f'<section class="metric-card"><span class="metric-label">Related directories</span><strong>{len(guide.get("related_directories", []))}</strong></section>',
        f'<section class="metric-card"><span class="metric-label">Related modules</span><strong>{len(guide.get("related_modules", []))}</strong></section>',
        '</section>',
    ]
    for section in guide.get('sections', []):
        body.append(f'<section class="content-card"><h3>{html.escape(section.get("title", "Section"))}</h3>')
        kind = section.get('kind', 'bullets')
        items = section.get('items', [])
        if kind == 'paragraphs':
            for item in items:
                body.append(f'<p>{html.escape(item)}</p>')
        elif kind == 'code':
            body.append('<pre class="code-block"><code>')
            body.append(html.escape('\n'.join(items)))
            body.append('</code></pre>')
        elif kind == 'steps':
            body.append('<ol class="plain-list step-list">')
            for item in items:
                body.append(f'<li>{html.escape(item)}</li>')
            body.append('</ol>')
        else:
            body.append('<ul class="plain-list">')
            for item in items:
                body.append(f'<li>{html.escape(item)}</li>')
            body.append('</ul>')
        body.append('</section>')
    body.append(_guide_related_block('Related directories', guide.get('related_directories', []), lambda item: (next((f'../directories/{entry["slug"]}.html' for entry in context_payload['directories'] if entry['key'] == item), '#'), f'directory::{item}')))
    body.append(_guide_related_block('Related modules', guide.get('related_modules', []), lambda item: _module_href(context_payload, item)))
    return _page_shell(guide['title'], site_title, ''.join(body), '..', guide_payload=guide_payload)

def _css() -> str:
    return """
:root {
  color-scheme: dark;
  --bg: #0f1117;
  --panel: #161a22;
  --panel-soft: #1d2330;
  --line: #2f3746;
  --text: #eef3fb;
  --muted: #aab4c7;
  --accent: #8d79ff;
  --accent-soft: rgba(141, 121, 255, 0.18);
}
* { box-sizing: border-box; }
body { margin: 0; font-family: Inter, Arial, sans-serif; background: var(--bg); color: var(--text); }
a { color: inherit; text-decoration: none; }
code { font-family: "JetBrains Mono", Consolas, monospace; }
.app-shell { min-height: 100vh; display: grid; grid-template-columns: 280px minmax(0, 1fr); }
.sidebar { border-right: 1px solid var(--line); background: linear-gradient(180deg, #11141b 0%, #0f1117 100%); padding: 24px 18px; position: sticky; top: 0; height: 100vh; }
.brand-block h1 { margin: 0 0 8px 0; font-size: 1.3rem; }
.eyebrow { margin: 0 0 6px 0; text-transform: uppercase; letter-spacing: 0.12em; color: var(--accent); font-size: 0.72rem; }
.muted { color: var(--muted); }
.side-nav { display: grid; gap: 8px; margin: 24px 0; }
.nav-link { padding: 10px 12px; border: 1px solid var(--line); border-radius: 12px; background: var(--panel); }
.nav-link:hover { border-color: var(--accent); background: var(--accent-soft); }
.main-pane { padding: 28px; }
.page-header { margin-bottom: 22px; }
.page-header h2 { margin: 0 0 10px 0; font-size: 2rem; }
.lead { color: var(--muted); max-width: 68rem; }
.metrics-grid { display: grid; gap: 14px; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); margin-bottom: 22px; }
.metric-card, .content-card, .toolbar-card { background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 18px; }
.metric-label { display: block; color: var(--muted); margin-bottom: 8px; font-size: 0.82rem; }
.content-grid { display: grid; gap: 18px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); margin-bottom: 18px; }
.entity-list, .plain-list { list-style: none; padding: 0; margin: 0; }
.entity-list li + li, .plain-list li + li { margin-top: 10px; }
.entity-list a { display: flex; justify-content: space-between; gap: 10px; align-items: center; padding: 11px 12px; border-radius: 12px; background: var(--panel-soft); border: 1px solid transparent; }
.entity-list a:hover { border-color: var(--accent); background: var(--accent-soft); }
.entity-list span { color: var(--muted); font-size: 0.86rem; text-align: right; }
.compact a { justify-content: flex-start; }
.search-label { display: block; font-weight: 600; }
.search-input { display: block; width: 100%; margin-top: 8px; padding: 12px 14px; border-radius: 12px; border: 1px solid var(--line); background: #0f131a; color: var(--text); }
.relation-map { width: 100%; height: auto; min-height: 320px; border-radius: 12px; background: radial-gradient(circle at center, rgba(141,121,255,0.08), rgba(0,0,0,0) 55%); }
.relation-edge { stroke: rgba(226, 231, 255, 0.35); stroke-width: 2; }
.relation-node circle { fill: #202736; stroke: rgba(255,255,255,0.16); stroke-width: 1.5; }
.relation-center circle { fill: rgba(141,121,255,0.28); stroke: rgba(141,121,255,0.86); }
.relation-node text { fill: var(--text); font-size: 12px; }
.guide-grid { display: grid; gap: 14px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
.guide-card { display: grid; gap: 8px; padding: 16px; border-radius: 16px; border: 1px solid var(--line); background: var(--panel-soft); }
.guide-card:hover { border-color: var(--accent); background: var(--accent-soft); }
.guide-card span, .guide-card em { color: var(--muted); font-style: normal; }
.code-block { overflow-x: auto; padding: 14px; border-radius: 14px; border: 1px solid var(--line); background: #0f131a; }
.step-list { padding-left: 20px; }
.tooltip-root { position: fixed; z-index: 9999; max-width: 340px; padding: 10px 12px; border-radius: 12px; border: 1px solid var(--line); background: #0f131a; color: var(--text); box-shadow: 0 12px 40px rgba(0,0,0,0.35); pointer-events: none; }
@media (max-width: 1024px) {
  .app-shell { grid-template-columns: 1fr; }
  .sidebar { position: static; height: auto; border-right: 0; border-bottom: 1px solid var(--line); }
}
"""



def _js() -> str:
    return """
(async function () {
  let tooltips = {};
  try {
    const response = await fetch(document.querySelector('script[src$="app.js"]').src.replace('/assets/app.js', '/data/tooltips.json'));
    tooltips = await response.json();
  } catch (error) {
    tooltips = {};
  }

  const tooltipRoot = document.getElementById('tooltip-root');
  const searchInput = document.getElementById('entity-search');
  if (searchInput) {
    const items = Array.from(document.querySelectorAll('.searchable-list > li'));
    searchInput.addEventListener('input', () => {
      const term = searchInput.value.trim().toLowerCase();
      for (const item of items) {
        const haystack = item.getAttribute('data-search-text') || '';
        item.hidden = term ? !haystack.includes(term) : false;
      }
    });
  }

  const showTooltip = (event) => {
    const key = event.currentTarget.getAttribute('data-tooltip-key');
    const text = tooltips[key];
    if (!text) {
      return;
    }
    tooltipRoot.textContent = text;
    tooltipRoot.hidden = false;
    const x = Math.min(window.innerWidth - 360, event.clientX + 16);
    const y = Math.min(window.innerHeight - 80, event.clientY + 16);
    tooltipRoot.style.left = `${Math.max(8, x)}px`;
    tooltipRoot.style.top = `${Math.max(8, y)}px`;
  };

  const hideTooltip = () => {
    tooltipRoot.hidden = true;
  };

  document.querySelectorAll('[data-tooltip-key]').forEach((el) => {
    el.addEventListener('mouseenter', showTooltip);
    el.addEventListener('mousemove', showTooltip);
    el.addEventListener('mouseleave', hideTooltip);
  });
})();
"""





def write_review_site(
    output_dir: Path,
    context_payload: dict,
    site_title: str = "UML Review Explorer",
    guide_payload: dict | None = None,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = output_dir / "assets"
    data_dir = output_dir / "data"
    directories_dir = output_dir / "directories"
    modules_dir = output_dir / "modules"
    symbols_dir = output_dir / "symbols"
    guides_dir = output_dir / "guides"
    assets_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    directories_dir.mkdir(parents=True, exist_ok=True)
    modules_dir.mkdir(parents=True, exist_ok=True)
    symbols_dir.mkdir(parents=True, exist_ok=True)
    guides_dir.mkdir(parents=True, exist_ok=True)

    combined_tooltips = dict(context_payload["tooltips"])
    if guide_payload:
        combined_tooltips.update(guide_payload.get("tooltips", {}))

    write_text(assets_dir / "app.css", _css())
    write_text(assets_dir / "app.js", _js())
    write_json(data_dir / "context.json", context_payload)
    if guide_payload:
        write_json(data_dir / "guides.json", guide_payload)
    write_json(data_dir / "tooltips.json", combined_tooltips)
    write_text(output_dir / "index.html", _overview_page(site_title, context_payload, guide_payload=guide_payload))
    write_text(directories_dir / "index.html", _entity_index_page(site_title, "Directory Explorer", "Directories", context_payload["directories"], guide_payload=guide_payload))
    write_text(modules_dir / "index.html", _entity_index_page(site_title, "Module Explorer", "Modules", context_payload["modules"], guide_payload=guide_payload))
    write_text(symbols_dir / "index.html", _entity_index_page(site_title, "Symbol Explorer", "Symbols", context_payload["symbols"], guide_payload=guide_payload))

    if guide_payload and guide_payload.get("guides"):
        write_text(guides_dir / "index.html", _guide_index_page(site_title, guide_payload))
        for guide in guide_payload["guides"]:
            write_text(guides_dir / f'{guide["slug"]}.html', _guide_page(site_title, guide, context_payload, guide_payload))
    else:
        write_text(guides_dir / "index.html", _page_shell("Guides", site_title, '<section class="content-card"><h3>No guide payload</h3><p class="muted">This site was generated without guide pages.</p></section>', '..'))

    for item in context_payload["directories"]:
        write_text(directories_dir / f'{item["slug"]}.html', _entity_page(site_title, item, context_payload, guide_payload=guide_payload))
    for item in context_payload["modules"]:
        write_text(modules_dir / f'{item["slug"]}.html', _entity_page(site_title, item, context_payload, guide_payload=guide_payload))
    for item in context_payload["symbols"]:
        write_text(symbols_dir / f'{item["slug"]}.html', _entity_page(site_title, item, context_payload, guide_payload=guide_payload))

    summary_md = output_dir / "README.md"
    write_text(
        summary_md,
        "\n".join(
            [
                "# UML Review Explorer",
                "",
                "Static website generated from UML-oriented repository context.",
                "",
                f"- site title: {site_title}",
                f"- guides: {len(guide_payload['guides']) if guide_payload else 0}",
                f"- directories: {len(context_payload['directories'])}",
                f"- modules: {len(context_payload['modules'])}",
                f"- symbols: {len(context_payload['symbols'])}",
                f"- root page: index.html",
                "",
            ]
        ),
    )
    return {
        "site_dir": str(output_dir),
        "index_html": str(output_dir / "index.html"),
        "summary_md": str(summary_md),
        "context_json": str(data_dir / "context.json"),
        "tooltips_json": str(data_dir / "tooltips.json"),
        "guides_json": str(data_dir / "guides.json") if guide_payload else None,
        "guide_pages": len(guide_payload["guides"]) if guide_payload else 0,
        "directory_pages": len(context_payload["directories"]),
        "module_pages": len(context_payload["modules"]),
        "symbol_pages": len(context_payload["symbols"]),
    }
