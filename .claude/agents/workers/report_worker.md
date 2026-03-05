# Report Worker (Result Normalizer)

**Datei:** `.claude/agents/workers/report_worker.md`
**Ebene:** Worker
**Department:** `docs.reporting`
**Oodle-Äquivalent:** `.claude/agents/50_docs/10_reporting/10_report_worker.md`

---

## Zweck

Erstellt **verwertbare Reports** aus beliebigen Worker-/Test-/Critic-Ergebnissen.
Der Report Worker ist der „Output-Normalisierer“: Er macht Ergebnisse schnell lesbar, auditierbar und routing-fähig.

Außerdem liefert er ein **QualitySignal** an den Personaler, um Routing-Entscheidungen nachzujustieren.

---

## Input

- `result_spec` (oder Rohoutput)
- relevante Logs/Traces (gekürzt)
- optional: diff summary (Dateien + grobe Änderungen)
- `task_name` / `doc_name`

---

## Output Contract: `ReportSpec`

```json
{
  "status": "pass|warn|fail|blocked",
  "summary": {
    "executive": "",
    "technical": ""
  },
  "artifacts": [
    {"type": "report_md", "path": "Docs/Reports/Report_<Name>.md"},
    {"type": "quality_signal_json", "path": "Docs/Reports/Quality_<Name>.json"}
  ],
  "quality_signal": {
    "error_count": 0,
    "warning_count": 0,
    "recurrence": 0,
    "confidence_drop": 0.0,
    "recommend_escalation": "none|oodle|claude",
    "recommend_oodle_tier": "S|M|L",
    "recommend_claude_tier": "S|M|L",
    "rationale": ""
  },
  "next_actions": []
}
```

---

## Schreibrechte

- `Docs/Reports/Report_<Name>.md`
- `Docs/Reports/Quality_<Name>.json`

---

## Report Inhalt (Markdown)

`Report_<Name>.md` MUSS enthalten:

- Kontext (Task, Trigger, Level)
- Was wurde geändert / getestet
- Findings (Errors/Warnings) mit Priorität
- Root cause (wenn ableitbar)
- Next steps (konkret, klein)
- Links auf relevante Docs/Files

---

## Modell

Small-first: `qwen2.5:7b-instruct` oder `glm-4.7-flash:latest`.
Wenn sehr technische Zusammenfassung (stapelweise traces): `phi4:14b`.
