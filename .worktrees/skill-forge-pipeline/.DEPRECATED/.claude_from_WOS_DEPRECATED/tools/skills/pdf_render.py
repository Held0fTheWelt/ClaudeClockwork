#!/usr/bin/env python3
"""pdf_render

Deterministic PDF renderer for Claude Clockwork.

This skill converts an **already prepared** Markdown manuscript into a readable PDF,
optionally embedding simple diagrams ("schemata") from a JSON spec.

It does NOT call any LLMs. It is designed to be the final step after a doc pipeline
(e.g., Explore -> Write -> Critic -> DecideGap) has produced:
- manuscript.md
- diagrams.json (optional)

Inputs (SkillRequestSpec):
{
  "skill_id": "pdf_render",
  "inputs": {
    "manuscript_path": "Docs/Documentation/FirstSteps.md",
    "manuscript_markdown": "...",          # alternative to manuscript_path
    "diagrams_path": "Docs/References/diagrams/first_steps/diagrams.json",
    "diagrams": { "diagrams": [...] },     # alternative to diagrams_path
    "pdf_path": "Docs/References/FirstSteps.pdf",
    "title": "First Steps",
    "subtitle": "Clockwork DocForge",
    "version": "v1.0",
    "include_toc": true
  }
}

Diagram markers inside Markdown:
- [[diagram:ID]]  (case-insensitive)

Supported diagram types (diagrams.json):
- block: boxes + arrows (system architecture)
- sequence: simple sequence diagram (participants + messages)

The diagram spec is intentionally small and deterministic.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import re

# reportlab is available in the runtime this repo targets
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Preformatted, PageBreak,
        ListFlowable, ListItem, Table, TableStyle, Flowable
    )
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    _REPORTLAB_AVAILABLE = True
except ImportError:
    _REPORTLAB_AVAILABLE = False
    # Stub classes so module-level class definitions don't fail at import
    class Flowable:  # type: ignore[no-redef]
        pass


def _ok(req: dict, outputs: dict, warnings: list[str] | None = None, metrics: dict | None = None) -> dict:
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "pdf_render"),
        "status": "ok",
        "outputs": outputs,
        "metrics": metrics or {},
        "errors": [],
        "warnings": warnings or [],
    }


def _fail(req: dict, msg: str, warnings: list[str] | None = None) -> dict:
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "pdf_render"),
        "status": "fail",
        "outputs": {},
        "metrics": {},
        "errors": [msg],
        "warnings": warnings or [],
    }


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _norm_marker(line: str) -> Optional[str]:
    # [[diagram:ID]] or [[DIAGRAM:ID]]
    s = line.strip()
    if not (s.startswith("[[") and s.endswith("]]")):
        return None
    inner = s[2:-2].strip()
    if ":" not in inner:
        return None
    k, v = inner.split(":", 1)
    if k.strip().lower() != "diagram":
        return None
    v = v.strip()
    return v or None


def _split_markdown_blocks(md: str) -> List[List[str]]:
    """Split markdown into blocks separated by blank lines, preserving diagram markers as single-line blocks."""
    lines = md.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    blocks: List[List[str]] = []
    cur: List[str] = []
    i = 0
    in_code = False
    fence = ""
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            if not in_code:
                in_code = True
                fence = line.strip()
                cur.append(line)
            else:
                cur.append(line)
                in_code = False
                fence = ""
            i += 1
            continue

        if in_code:
            cur.append(line)
            i += 1
            continue

        # diagram markers become their own block
        if _norm_marker(line):
            if cur:
                blocks.append(cur)
                cur = []
            blocks.append([line])
            i += 1
            continue

        if line.strip() == "":
            if cur:
                blocks.append(cur)
                cur = []
        else:
            cur.append(line)
        i += 1

    if cur:
        blocks.append(cur)
    return blocks


def _is_table_block(block: List[str]) -> bool:
    # very small heuristic: a pipe table with header + separator line
    if len(block) < 2:
        return False
    if "|" not in block[0]:
        return False
    sep = block[1].replace(" ", "")
    return set(sep) <= set("|:-") and "-" in sep


def _parse_table(block: List[str]) -> List[List[str]]:
    rows = []
    for line in block:
        if line.strip() == "":
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        rows.append(parts)
    # drop separator row if present
    if len(rows) >= 2:
        sep = "".join(rows[1]).replace(" ", "")
        if set(sep) <= set(":-") and "-" in sep:
            rows.pop(1)
    return rows


def _is_list_block(block: List[str]) -> bool:
    return all(re.match(r"^\s*[-*]\s+.+$", ln) for ln in block)


def _parse_list(block: List[str]) -> List[str]:
    out = []
    for ln in block:
        m = re.match(r"^\s*[-*]\s+(.+)$", ln)
        out.append(m.group(1).strip() if m else ln.strip())
    return out


def _is_code_block(block: List[str]) -> bool:
    return len(block) >= 2 and block[0].strip().startswith("```")


def _strip_code_fence(block: List[str]) -> Tuple[str, str]:
    first = block[0].strip()
    lang = first[3:].strip()
    # last fence might be missing; be tolerant
    body = "\n".join(block[1:-1] if block[-1].strip().startswith("```") else block[1:])
    return lang, body


def _heading_level(line: str) -> int:
    m = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
    if not m:
        return 0
    return len(m.group(1))


def _escape_para(text: str) -> str:
    # reportlab Paragraph uses a tiny HTML subset
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )


@dataclass
class DiagramSpec:
    id: str
    type: str
    title: str
    payload: dict


class BlockDiagramFlowable(Flowable):
    def __init__(self, spec: DiagramSpec, width: float, height: float):
        super().__init__()
        self.spec = spec
        self.width = width
        self.height = height

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        c = self.canv
        payload = self.spec.payload
        nodes = payload.get("nodes", [])
        edges = payload.get("edges", [])

        # simple grid layout
        cols = max(1, int(math.ceil(math.sqrt(max(1, len(nodes))))))
        rows = int(math.ceil(len(nodes) / cols))

        pad = 6 * mm
        box_w = (self.width - pad * 2) / max(1, cols)
        box_h = (self.height - pad * 2) / max(1, rows)

        node_pos = {}
        for idx, n in enumerate(nodes):
            r = idx // cols
            col = idx % cols
            x = pad + col * box_w
            y = self.height - pad - (r + 1) * box_h
            node_pos[n.get("id", f"n{idx}")] = (x, y, box_w, box_h)

        # draw edges first
        c.setStrokeColor(colors.grey)
        c.setLineWidth(1)
        for e in edges:
            a = e.get("from")
            b = e.get("to")
            if a not in node_pos or b not in node_pos:
                continue
            ax, ay, aw, ah = node_pos[a]
            bx, by, bw, bh = node_pos[b]
            x1, y1 = ax + aw/2, ay + ah/2
            x2, y2 = bx + bw/2, by + bh/2
            c.line(x1, y1, x2, y2)
            # simple arrow head
            ang = math.atan2(y2 - y1, x2 - x1)
            al = 4*mm
            a1 = ang + math.pi * 0.85
            a2 = ang - math.pi * 0.85
            c.line(x2, y2, x2 + al*math.cos(a1), y2 + al*math.sin(a1))
            c.line(x2, y2, x2 + al*math.cos(a2), y2 + al*math.sin(a2))

        # draw nodes
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.whitesmoke)
        for idx, n in enumerate(nodes):
            nid = n.get("id", f"n{idx}")
            x, y, w, h = node_pos[nid]
            c.rect(x, y, w-2*mm, h-2*mm, fill=1, stroke=1)
            label = str(n.get("label", nid))
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 9)
            c.drawString(x + 3*mm, y + h/2, label[:60])
            c.setFillColor(colors.whitesmoke)


class SequenceDiagramFlowable(Flowable):
    def __init__(self, spec: DiagramSpec, width: float, height: float):
        super().__init__()
        self.spec = spec
        self.width = width
        self.height = height

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        c = self.canv
        p = self.spec.payload
        participants = p.get("participants", [])
        messages = p.get("messages", [])

        if not participants:
            return

        padx = 8*mm
        pady = 6*mm

        n = len(participants)
        step_x = (self.width - 2*padx) / max(1, n-1)

        # lifelines
        c.setStrokeColor(colors.black)
        c.setFont("Helvetica", 9)
        x_positions = {}
        for i, name in enumerate(participants):
            x = padx + i * step_x
            x_positions[name] = x
            c.drawCentredString(x, self.height - pady, str(name)[:24])
            c.setDash(2, 2)
            c.line(x, self.height - pady - 4*mm, x, pady)
            c.setDash()

        # messages
        y = self.height - pady - 10*mm
        dy = 8*mm
        for msg in messages[:200]:
            frm = msg.get("from")
            to = msg.get("to")
            label = str(msg.get("label", ""))
            if frm not in x_positions or to not in x_positions:
                y -= dy
                continue
            x1, x2 = x_positions[frm], x_positions[to]
            c.setStrokeColor(colors.grey)
            c.line(x1, y, x2, y)

            # arrow head
            ang = math.atan2(0, x2 - x1)
            al = 3*mm
            a1 = ang + math.pi * 0.85
            a2 = ang - math.pi * 0.85
            c.line(x2, y, x2 + al*math.cos(a1), y + al*math.sin(a1))
            c.line(x2, y, x2 + al*math.cos(a2), y + al*math.sin(a2))

            c.setFillColor(colors.black)
            c.setFont("Helvetica", 8)
            c.drawString(min(x1, x2)+2*mm, y+2, label[:90])
            y -= dy
            if y < pady + 10*mm:
                break


def _diagram_flowable(spec: DiagramSpec, width: float) -> Flowable:
    # fixed height, proportional to width
    h = max(60*mm, min(120*mm, width * 0.55))
    t = spec.type.lower()
    if t == "sequence":
        return SequenceDiagramFlowable(spec, width, h)
    return BlockDiagramFlowable(spec, width, h)


def _build_styles():
    styles = getSampleStyleSheet()
    # tighten defaults slightly, keep very readable
    styles.add(ParagraphStyle(name="H1", parent=styles["Heading1"], fontSize=18, leading=22, spaceAfter=10))
    styles.add(ParagraphStyle(name="H2", parent=styles["Heading2"], fontSize=14, leading=18, spaceAfter=8))
    styles.add(ParagraphStyle(name="H3", parent=styles["Heading3"], fontSize=12, leading=16, spaceAfter=6))
    styles.add(ParagraphStyle(name="Body", parent=styles["BodyText"], fontSize=10.5, leading=14, spaceAfter=6))
    styles.add(ParagraphStyle(name="Code", parent=styles["BodyText"], fontName="Courier", fontSize=9, leading=11, spaceAfter=6))
    return styles


def _markdown_to_flowables(md: str, diagrams: Dict[str, DiagramSpec]) -> Tuple[List[Any], List[str]]:
    styles = _build_styles()
    story: List[Any] = []
    warnings: List[str] = []
    blocks = _split_markdown_blocks(md)

    for block in blocks:
        if len(block) == 1 and (did := _norm_marker(block[0])):
            key = did
            spec = diagrams.get(key)
            if not spec:
                warnings.append(f"diagram marker not found: {did}")
                story.append(Paragraph(_escape_para(f"[Missing diagram: {did}]"), styles["Body"]))
                story.append(Spacer(1, 6))
                continue
            story.append(Paragraph(_escape_para(spec.title or spec.id), styles["H3"]))
            story.append(_diagram_flowable(spec, width=170*mm))
            story.append(Spacer(1, 8))
            continue

        # code fences
        if _is_code_block(block):
            lang, body = _strip_code_fence(block)
            label = f"Code ({lang})" if lang else "Code"
            story.append(Paragraph(_escape_para(label), styles["H3"]))
            story.append(Preformatted(body, styles["Code"]))
            story.append(Spacer(1, 6))
            continue

        # pipe table
        if _is_table_block(block):
            rows = _parse_table(block)
            # cap columns
            max_cols = max(len(r) for r in rows) if rows else 0
            rows = [r + [""]*(max_cols-len(r)) for r in rows]
            tbl = Table(rows, hAlign="LEFT")
            tbl.setStyle(TableStyle([
                ("FONT", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONT", (0,1), (-1,-1), "Helvetica"),
                ("FONTSIZE", (0,0), (-1,-1), 9),
                ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
                ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
                ("VALIGN", (0,0), (-1,-1), "TOP"),
                ("LEFTPADDING", (0,0), (-1,-1), 4),
                ("RIGHTPADDING", (0,0), (-1,-1), 4),
                ("TOPPADDING", (0,0), (-1,-1), 3),
                ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 8))
            continue

        # bullet list
        if _is_list_block(block):
            items = _parse_list(block)
            lf = ListFlowable(
                [ListItem(Paragraph(_escape_para(it), styles["Body"])) for it in items],
                bulletType="bullet",
                leftIndent=14,
                bulletFontName="Helvetica",
                bulletFontSize=10,
            )
            story.append(lf)
            story.append(Spacer(1, 6))
            continue

        # headings / paragraphs
        # If the first line is a heading, treat it as heading and rest as body
        first = block[0]
        hl = _heading_level(first)
        if hl:
            text = re.sub(r"^#{1,6}\s+", "", first.strip())
            st = styles["H1"] if hl == 1 else styles["H2"] if hl == 2 else styles["H3"]
            story.append(Paragraph(_escape_para(text), st))
            rest = [ln for ln in block[1:] if ln.strip()]
            if rest:
                story.append(Paragraph(_escape_para(" ".join(rest)), styles["Body"]))
            story.append(Spacer(1, 4))
            continue

        # normal paragraph
        para = " ".join([ln.strip() for ln in block if ln.strip()])
        if para.strip():
            story.append(Paragraph(_escape_para(para), styles["Body"]))
        story.append(Spacer(1, 2))

    return story, warnings


def _make_cover(title: str, subtitle: str, version: str) -> List[Any]:
    styles = _build_styles()
    story: List[Any] = []
    story.append(Spacer(1, 40*mm))
    story.append(Paragraph(_escape_para(title), styles["H1"]))
    if subtitle:
        story.append(Paragraph(_escape_para(subtitle), styles["H2"]))
    if version:
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph(_escape_para(f"Version: {version}"), styles["Body"]))
    story.append(PageBreak())
    return story


def run(req: dict) -> dict:
    if not _REPORTLAB_AVAILABLE:
        return _fail(req, "reportlab is not installed; pdf_render requires: pip install reportlab")

    inputs = req.get("inputs") or {}
    manuscript_markdown = inputs.get("manuscript_markdown")
    manuscript_path = inputs.get("manuscript_path")
    diagrams_obj = inputs.get("diagrams")
    diagrams_path = inputs.get("diagrams_path")
    pdf_path = inputs.get("pdf_path")

    if not pdf_path:
        return _fail(req, "inputs.pdf_path is required")

    # load manuscript
    md = ""
    if manuscript_markdown:
        md = str(manuscript_markdown)
    elif manuscript_path:
        p = Path(manuscript_path)
        if not p.exists():
            return _fail(req, f"manuscript_path not found: {manuscript_path}")
        md = _read_text(p)
    else:
        return _fail(req, "Provide inputs.manuscript_markdown or inputs.manuscript_path")

    # load diagrams
    diagrams: Dict[str, DiagramSpec] = {}
    warnings: List[str] = []
    try:
        if diagrams_obj:
            dobj = diagrams_obj
        elif diagrams_path:
            dp = Path(diagrams_path)
            if dp.exists():
                dobj = _load_json(dp)
            else:
                dobj = None
                warnings.append(f"diagrams_path not found: {diagrams_path}")
        else:
            dobj = None

        if dobj and isinstance(dobj, dict):
            for d in dobj.get("diagrams", []):
                did = str(d.get("id", "")).strip()
                if not did:
                    continue
                diagrams[did] = DiagramSpec(
                    id=did,
                    type=str(d.get("type", "block")),
                    title=str(d.get("title", did)),
                    payload=dict(d),
                )
    except Exception as e:
        warnings.append(f"failed to load diagrams: {e}")

    title = str(inputs.get("title", "Document")).strip() or "Document"
    subtitle = str(inputs.get("subtitle", "")).strip()
    version = str(inputs.get("version", "")).strip()
    include_toc = bool(inputs.get("include_toc", False))

    out = Path(pdf_path)
    _ensure_parent(out)

    try:
        doc = SimpleDocTemplate(
            str(out),
            pagesize=A4,
            leftMargin=18*mm,
            rightMargin=18*mm,
            topMargin=18*mm,
            bottomMargin=18*mm,
            title=title,
            author=str(inputs.get("author", "Claude Clockwork")),
        )

        story: List[Any] = []
        story.extend(_make_cover(title, subtitle, version))

        # (Optional) naive TOC: collect H1/H2 headings and render as list with page numbers not supported deterministically here
        # Instead render a heading list.
        if include_toc:
            story.append(Paragraph("Table of Contents", _build_styles()["H2"]))
            # Extract headings from markdown
            toc_items = []
            for ln in md.splitlines():
                lvl = _heading_level(ln)
                if lvl in (1,2):
                    toc_items.append(re.sub(r"^#{1,6}\s+", "", ln.strip()))
            if toc_items:
                lf = ListFlowable(
                    [ListItem(Paragraph(_escape_para(t), _build_styles()["Body"])) for t in toc_items],
                    bulletType="bullet",
                    leftIndent=14,
                )
                story.append(lf)
            else:
                story.append(Paragraph("No headings found.", _build_styles()["Body"]))
            story.append(PageBreak())

        body, w = _markdown_to_flowables(md, diagrams)
        warnings.extend(w)
        story.extend(body)

        doc.build(story)

        return _ok(req, outputs={"pdf_path": str(out)}, warnings=warnings, metrics={"diagrams_used": len(diagrams)})
    except Exception as e:
        return _fail(req, f"pdf render failed: {e}", warnings=warnings)
