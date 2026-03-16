#!/usr/bin/env python3
"""pdf_export

Batch-export multiple Markdown documentation files to deterministic PDFs
(or HTML fallback if no PDF library available).

Interface: run(req: dict) -> SkillResultSpec

Inputs:
  project_root  str   — repository root
  doc_files     list  — relative paths to source files (Markdown or .mmd)
  output_dir    str   — relative output dir (default: docs/_exports/pdf)
  naming_scheme str   — "flat_underscore" (default) or "hierarchical"
  fallback_fmt  str   — "html" (default) or "markdown"
  mermaid       str   — "embed_as_text" (default) or "skip"
  dry_run       bool  — if true, plan only (default: true)

Outputs:
  exported      list  — {input_file, output_file, status, tool, bytes, warnings}
  skipped       list  — {input_file, reason}
  tool_used     str   — primary tool name
  output_dir    str
  dry_run       bool
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ok(req: dict, outputs: dict, warnings: list[str] | None = None, metrics: dict | None = None) -> dict:
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "pdf_export"),
        "status": "ok",
        "outputs": outputs,
        "errors": [],
        "warnings": warnings or [],
        "metrics": metrics or {},
    }


def _fail(req: dict, errors: list[str]) -> dict:
    return {
        "type": "skill_result_spec",
        "request_id": req.get("request_id", ""),
        "skill_id": req.get("skill_id", "pdf_export"),
        "status": "fail",
        "outputs": {},
        "errors": errors,
        "warnings": [],
        "metrics": {},
    }


def _detect_tool() -> str:
    """Return first available PDF tool: 'pandoc' | 'reportlab' | 'html'."""
    if shutil.which("pandoc"):
        return "pandoc"
    try:
        import reportlab  # noqa: F401
        return "reportlab"
    except ImportError:
        pass
    return "html"


def _output_name(rel: str, scheme: str) -> str:
    """Convert relative doc path to output filename."""
    # Strip docs/ prefix
    r = rel.replace("\\", "/")
    if r.startswith("docs/"):
        r = r[5:]
    # Extension swap
    if r.endswith(".mmd"):
        r = r[:-4] + "_diagram.pdf"
    else:
        r = r[:-3] + ".pdf" if r.endswith(".md") else r + ".pdf"
    # Naming scheme
    if scheme == "flat_underscore":
        r = r.replace("/", "_")
    return r


def _html_from_md(md: str, title: str = "") -> str:
    """Minimal Markdown -> HTML (no external deps)."""
    lines = md.splitlines()
    out = [
        "<!DOCTYPE html><html><head>",
        f"<meta charset='utf-8'><title>{title}</title>",
        "<style>body{font-family:sans-serif;max-width:820px;margin:2em auto;padding:1em;line-height:1.65}",
        "h1{border-bottom:2px solid #333;padding-bottom:.4em}",
        "h2{border-bottom:1px solid #aaa;padding-bottom:.2em;margin-top:1.4em}",
        "code{background:#f4f4f4;padding:.15em .4em;border-radius:3px;font-family:monospace}",
        "pre{background:#f4f4f4;padding:1em;border-left:3px solid #ccc;overflow-x:auto}",
        "table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:.45em}",
        "th{background:#f4f4f4;font-weight:bold}</style></head><body>",
    ]
    in_pre = False
    for line in lines:
        s = line.rstrip()
        if s.startswith("```"):
            if not in_pre:
                out.append("<pre><code>")
                in_pre = True
            else:
                out.append("</code></pre>")
                in_pre = False
            continue
        if in_pre:
            out.append(s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            continue
        if s.startswith("# "):
            out.append(f"<h1>{s[2:].strip()}</h1>")
        elif s.startswith("## "):
            out.append(f"<h2>{s[3:].strip()}</h2>")
        elif s.startswith("### "):
            out.append(f"<h3>{s[4:].strip()}</h3>")
        elif s.startswith("#### "):
            out.append(f"<h4>{s[5:].strip()}</h4>")
        elif s.startswith("- ") or s.startswith("* "):
            out.append(f"<p>&#x2022; {s[2:].strip()}</p>")
        elif s.strip():
            out.append(f"<p>{s.strip()}</p>")
    if in_pre:
        out.append("</code></pre>")
    out.append("</body></html>")
    return "\n".join(out)


def _export_pandoc(src: Path, dst: Path) -> tuple[bool, str]:
    """Convert src -> dst via pandoc. Returns (ok, error_msg)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = subprocess.run(
            ["pandoc", str(src), "-o", str(dst), "--pdf-engine=xelatex"],
            capture_output=True, text=True, timeout=60,
        )
        if r.returncode == 0 and dst.exists():
            return True, ""
        # Try without pdf-engine flag
        r2 = subprocess.run(
            ["pandoc", str(src), "-o", str(dst)],
            capture_output=True, text=True, timeout=60,
        )
        if r2.returncode == 0 and dst.exists():
            return True, ""
        return False, r2.stderr.strip() or "pandoc failed"
    except Exception as e:
        return False, str(e)


def _export_reportlab(src: Path, dst: Path) -> tuple[bool, str]:
    """Convert src -> dst via reportlab. Returns (ok, error_msg)."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted

        dst.parent.mkdir(parents=True, exist_ok=True)
        md = src.read_text(encoding="utf-8", errors="replace")
        doc = SimpleDocTemplate(
            str(dst), pagesize=A4,
            leftMargin=18 * mm, rightMargin=18 * mm,
            topMargin=18 * mm, bottomMargin=18 * mm,
            title=src.name,
        )
        styles = getSampleStyleSheet()
        story: list[Any] = []
        in_pre = False
        pre_lines: list[str] = []
        for line in md.splitlines():
            s = line.rstrip()
            if s.startswith("```"):
                if not in_pre:
                    in_pre = True
                    pre_lines = []
                else:
                    in_pre = False
                    story.append(Preformatted("\n".join(pre_lines), styles["Code"]))
                    pre_lines = []
                continue
            if in_pre:
                pre_lines.append(s)
                continue
            if s.startswith("# "):
                story.append(Paragraph(s[2:].strip(), styles["Heading1"]))
            elif s.startswith("## "):
                story.append(Paragraph(s[3:].strip(), styles["Heading2"]))
            elif s.startswith("### "):
                story.append(Paragraph(s[4:].strip(), styles["Heading3"]))
            elif s.strip():
                story.append(Paragraph(s.strip(), styles["BodyText"]))
            else:
                story.append(Spacer(1, 6))
        doc.build(story)
        return True, ""
    except Exception as e:
        return False, str(e)


def _export_html(src: Path, dst_pdf: Path) -> tuple[str, str]:
    """Write HTML fallback. Returns (actual_output_path, warning)."""
    dst = dst_pdf.with_suffix(".html")
    dst.parent.mkdir(parents=True, exist_ok=True)
    md = src.read_text(encoding="utf-8", errors="replace")
    html = _html_from_md(md, title=src.stem)
    dst.write_text(html, encoding="utf-8")
    return str(dst), "no PDF library available; wrote HTML fallback"


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

def run(req: dict) -> dict:
    inputs = req.get("inputs", {})

    project_root_s = inputs.get("project_root", ".")
    project_root = Path(project_root_s).resolve()
    if not project_root.exists():
        return _fail(req, [f"project_root not found: {project_root}"])

    doc_files: list[str] = inputs.get("doc_files", [])
    if not doc_files:
        return _fail(req, ["inputs.doc_files is required and must be non-empty"])

    output_dir_s = inputs.get("output_dir", "docs/_exports/pdf")
    output_dir = (project_root / output_dir_s).resolve()

    scheme = inputs.get("naming_scheme", "flat_underscore")
    fallback_fmt = inputs.get("fallback_fmt", "html")
    mermaid = inputs.get("mermaid", "embed_as_text")
    dry_run = bool(inputs.get("dry_run", True))

    tool = _detect_tool()

    if dry_run:
        planned = [
            {"input": f, "output": str(output_dir / _output_name(f, scheme))}
            for f in doc_files
        ]
        return _ok(req, {
            "dry_run": True,
            "tool_available": tool,
            "output_dir": str(output_dir),
            "planned_files": planned,
        }, metrics={"planned": len(planned)})

    exported: list[dict] = []
    skipped: list[dict] = []
    all_warnings: list[str] = []
    tools_used: set[str] = set()

    for rel in doc_files:
        src = project_root / rel
        if not src.exists():
            skipped.append({"input_file": rel, "reason": "file not found"})
            continue

        out_name = _output_name(rel, scheme)
        dst = output_dir / out_name

        # --- Mermaid handling ---
        if rel.endswith(".mmd"):
            if mermaid == "skip":
                skipped.append({"input_file": rel, "reason": "mermaid skip policy"})
                continue
            # Wrap as markdown then export via html
            wrapped = src.read_text(encoding="utf-8", errors="replace")
            tmp = tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8")
            tmp.write(f"# Diagram Source: {src.name}\n\n```\n{wrapped}\n```\n\n"
                      f"*Note: Render this file in Mermaid Live Editor for the visual diagram.*\n")
            tmp.flush()
            tmp_path = Path(tmp.name)
            actual_out, warn = _export_html(tmp_path, dst)
            tools_used.add("html_fallback")
            entry = {
                "input_file": rel,
                "output_file": actual_out.replace(str(project_root) + "/", ""),
                "status": "fallback",
                "tool": "html_fallback",
                "bytes": Path(actual_out).stat().st_size,
                "warnings": ["mermaid rendered as HTML text embed"],
            }
            exported.append(entry)
            all_warnings.extend(entry["warnings"])
            tmp_path.unlink(missing_ok=True)
            continue

        # --- Normal markdown ---
        if tool == "pandoc":
            ok, err = _export_pandoc(src, dst)
            if ok:
                tools_used.add("pandoc")
                exported.append({
                    "input_file": rel,
                    "output_file": str(dst.relative_to(project_root)),
                    "status": "ok",
                    "tool": "pandoc",
                    "bytes": dst.stat().st_size,
                    "warnings": [],
                })
                continue
            else:
                all_warnings.append(f"pandoc failed for {rel}: {err}; falling back to HTML")

        elif tool == "reportlab":
            ok, err = _export_reportlab(src, dst)
            if ok:
                tools_used.add("reportlab")
                exported.append({
                    "input_file": rel,
                    "output_file": str(dst.relative_to(project_root)),
                    "status": "ok",
                    "tool": "reportlab",
                    "bytes": dst.stat().st_size,
                    "warnings": [],
                })
                continue
            else:
                all_warnings.append(f"reportlab failed for {rel}: {err}; falling back to HTML")

        # HTML fallback
        actual_out, warn = _export_html(src, dst)
        tools_used.add("html_fallback")
        exported.append({
            "input_file": rel,
            "output_file": actual_out.replace(str(project_root) + "/", ""),
            "status": "fallback",
            "tool": "html_fallback",
            "bytes": Path(actual_out).stat().st_size,
            "warnings": [warn],
        })
        all_warnings.append(f"{rel}: {warn}")

    primary = "pandoc" if "pandoc" in tools_used else (
        "reportlab" if "reportlab" in tools_used else "html_fallback"
    )

    return _ok(req, {
        "exported": exported,
        "skipped": skipped,
        "tool_used": primary,
        "output_dir": str(output_dir),
        "dry_run": False,
    }, warnings=all_warnings, metrics={
        "total": len(doc_files),
        "exported": len(exported),
        "skipped": len(skipped),
        "fallbacks": sum(1 for e in exported if e.get("status") == "fallback"),
    })
