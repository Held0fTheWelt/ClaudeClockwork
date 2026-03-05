# Agent Routing Intelligence

> Wächst über Zeit durch Erfahrungen aller Agents. Wird von Team Lead für Agent- und Modell-Auswahl genutzt.
> Einträge werden nach abgeschlossenen Tasks ergänzt.

---

## Kompositions-Prinzip

Agent-Rollen sind Orientierung. Team Lead wählt pro Task das kleinste präziseste Team:
- L0: 1 Specialist (haiku) — kein QA nötig
- L1: 1 Specialist (sonnet) + Collector wenn Risiko vorhanden
- L2+: Specialist + Validation + ggf. Critic
- Kein Agent wird aus Vollständigkeit hinzugezogen — nur bei echtem Nutzen

---

## Task → Agent + Modell Mapping

| Task-Typ | Agent | Modell | Ollama-Type | Vorbedingungen |
|---|---|---|---|---|
| Neue Python-Funktion/-Klasse (vollständig) | Implementation Agent | sonnet | `draft` | Ollama draft als Basis |
| Single-file Bugfix (Python) | Implementation Agent | haiku | `quick` oder keins (L0) | — |
| Ollama-Client-Änderung | Implementation Agent | sonnet | `draft` | architecture.md injizieren |
| Neues Top-Level-Modul in `src/` | Architecture Agent | sonnet | `architecture` | Architecture Review L2 |
| Technische Dokumentation | Documentation Agent | haiku | `brief` | Quellcode vorher gelesen |
| Wissen indexieren / archivieren | Librarian Agent | haiku | — | Abgeschlossene Implementation als Input |
| Korrektheit gegen Akzeptanzkriterien | Collector Agent | haiku | — | Task Brief mit Kriterien vorhanden |
| Syntax / Import / Laufzeit Validation | Validation Agent | sonnet | `review` | Code fertig |
| Pattern-Extraktion | Pattern Recognition Agent | sonnet | — | Mind. 2 ähnliche Implementierungen |
| Architektur-Entscheid | Architecture Agent | sonnet | `architecture` | L2 Eskalation |
| L3 Performance / subprocess-Pooling | Technical Critic | sonnet | `architecture` | Validation Report vorhanden |
| Governance-Docs schreiben/updaten | Implementation Agent | sonnet | — | Klarer Content-Plan vorhanden |
| Status-Checks (test ollama) | — | haiku | — | Nur Script-Ausführung nötig |
| Effizienz-Analyse / Routing-Beratung | Skill Agent | sonnet | `architecture` (phi4:14b) oder `brief` (qwen2.5-coder:14b) | Letzte Tasks als Observationsbasis |

---

## Bekannte Routing-Anti-Patterns

- **Implementation Agent für Architektur-Entscheide** → falsch: Architecture Agent
- **haiku für neue Python-Klasse** → zu schwach für komplexe Implementation: sonnet + Ollama draft
- **Specialist ohne Ollama-Briefing bei L1+** → verboten per execution_protocol.md
- **Documentation Agent ohne Quellcode-Basis** → Docs werden ungenau

---

## Domain-Kontext Injection Tabelle

| Domain-Erkennungsmerkmal | Kontext-Datei | Agent |
|---|---|---|
| `OllamaClient`, `ollama_client`, Ollama HTTP | `<PROJECT_ROOT>/src/ollama_client.py` | Implementation Agent |
| `ClaudeClient`, `claude_client`, subprocess spawn | `<PROJECT_ROOT>/src/claude_client.py` | Implementation Agent |
| `Orchestrator`, `workflow`, Trigger-Erkennung | `<PROJECT_ROOT>/src/orchestrator.py` | Implementation Agent |
| `config.DOCS_PATH`, `config.CLAUDE_PATH` | `<PROJECT_ROOT>/src/config.py` | Implementation Agent |
| `BaseAgent`, `AgentResult`, `<PROJECT_ROOT>/src/agents/` | `<PROJECT_ROOT>/src/agents/base.py` | Implementation Agent |
| Modul-Boundary, Dependency-Richtung | `.claude/python/architecture.md` | Architecture Agent |
| Python-Patterns (Freeze, Spawn, Output) | `.claude/python/patterns.md` | Implementation Agent |

---

## Routing-Kalibrierung (wächst über Zeit)

| Datum | Task-Typ | Gewählter Agent+Modell | Ergebnis | Notiz |
|---|---|---|---|---|
| 2026-02-26 | Governance-Docs erstellen (Learning System) | Implementation Agent + sonnet | Gut | Content vollständig vorgeplant → Agent nur ausführend |
| 2026-02-26 | Status-Check (test ollama) | — haiku | Gut | Einfache Script-Ausführung, kein Reasoning nötig |
| 2026-02-27 | Python Orchestrator Migration (vollständig) | Claude Code direkt | Gut | Komplexe Multifile-Migration, kein Subagent-Overhead nötig |


## operations.observability
- Department Lead Ops Ledger (silent): `.claude/agents/operations/department_lead_ops_ledger.md`
