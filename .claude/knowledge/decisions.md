# Decisions Log — Python Orchestrator

> Append-only. Kurze, datierte Einträge. Langzeit-Referenz für Architektur- und Policy-Entscheidungen.
> Owner: Team Lead (via file_ownership.md)

---

## Template

```
- Datum:       YYYY-MM-DD
- Entscheidung: [Was wurde entschieden]
- Kontext:     [Warum war die Entscheidung nötig]
- Optionen:    [Mindestens 2 Alternativen]
- Begründung:  [Warum diese Option]
- Follow-ups:  [Konsequenzen, nächste Schritte]
```

---

## 2026-02-27 — Migration von WarCollection UE5 auf Python Orchestrator

- Datum: 2026-02-27
- Entscheidung: Vollständige Migration des `.claude/`-Systems von einem UE5-Game-Projekt auf den Python Orchestrator.
- Kontext: Das vorherige System war auf Unreal Engine ausgerichtet (`.claude/unreal/`). Das neue Projekt ist eine Python-Konsolenanwendung für autonome Ollama/Claude-Agenten-Orchestrierung.
- Optionen: (A) Bestehendes System anpassen, (B) Vollständige Neuerstellung der `.claude/`-Governance.
- Begründung: Option B — zu viel UE5-spezifische Logik, die nicht übertragbar ist.
- Follow-ups: `src/`-Verzeichnis aufgebaut (main, orchestrator, workflow, ollama_client, claude_client, config, agents/).

---

## 2026-02-27 — stdlib-only als Constraint

- Datum: 2026-02-27
- Entscheidung: Keine externen Python-Abhängigkeiten. Nur Python stdlib.
- Kontext: Einfache Installierbarkeit, kein virtualenv-Overhead, maximale Portabilität.
- Optionen: (A) requests + pydantic, (B) stdlib only (urllib, subprocess, json, pathlib).
- Begründung: Option B — der Overhead von externen Paketen überwiegt den Nutzen für diesen Use Case.
- Follow-ups: requirements.txt dokumentiert stdlib-only. Bei L2-Eskalation Architecture Agent einbeziehen wenn externe Pakete benötigt werden.

---

## 2026-02-27 — Oodle-Konzepte in Python Orchestrator adoptiert

- Datum: 2026-02-27
- Entscheidung: Selektive Adoption von Llama Code (formerly Oodle Code) CMD Konzepten in die .claude/ Governance.
- Kontext: OODLE.md / `.claude/`-System enthält ausgereifte Konzepte für Routing, Context-Budget, Quality-Tracking.
- Adoptiert: decisions.md-Pattern, Execution-Phasen (intake|plan|build|validate|review|docs|archive), L5-Gate-Trigger-Liste, Minimal-Kontext-Prinzip.
- Nicht adoptiert: YAML-Runtime-Storage (.llama_runtime/writes/), externes Provider-Management, volles Enterprise-Agent-Tree.
- Begründung: Python Orchestrator ist Ollama-first/local-first. Oodle-Runtime-Infra zu aufwändig für aktuellen Scope.
- Follow-ups: YAML-getriebenes Routing in orchestrator._classify() als L2-Task einplanen.
