# Specialist Agents

## Übersicht

Specialist Agents führen die eigentliche Implementierungsarbeit aus. Sie operieren innerhalb klar definierter Grenzen und eskalieren bei Unklarheiten an den Team Lead.

---

## Task Compactor (Low-Effort Diener)

**Zuständigkeit:**  
Der Task Compactor ist ein **Wasserträger / Low-Effort-Diener**. Er nimmt eine (oft große oder unscharfe) Nutzeranfrage entgegen und erzeugt daraus ein **kompaktes, strukturiertes Briefing** für nachgelagerte Agents (Orchestrator, Personaler, Kritiker).  
Er führt **keine Bewertung** und **keine Architektur- oder Qualitätsentscheidungen** durch.

**Aufgaben:**
- Canonical Sources und relevante Dokumente zur Anfrage benennen (z. B. OODLE.md, passende `.claude/`- und Docs-Dateien).
- Kernziel, Randbedingungen und offene Fragen in wenigen Bulletpoints herausarbeiten.
- Betroffene Dateien/Module/Tasks grob listen (ohne tiefen Code-Review).
- Ein kompaktes Briefing erzeugen, das ein High-Effort-Agent als Startpunkt nutzen kann.

**Low-Effort-In-Prinzip:**
- Wird mit kleinem Modell und `effort=low` ausgeführt (siehe `MODEL_POLICY.md` Low-Effort Servant Pattern).
- Liefert ein Intake-Resultat an Orchestrator/Personaler/Kritiker zurück.
- Wird bei Bedarf mehrfach eingesetzt (z. B. nach einem Review, um Folge-Tasks zu komprimieren).

**Nicht seine Aufgabe:**
- Kein finales Routing (das macht der Personaler).
- Keine Qualitätsbewertung oder Kritik (das macht der Kritiker).
- Keine Implementierung oder Architektur-Entscheidungen.

## Modell-Routing (kanonisch — Benutzer-Direktive 2026-02-27)

Small-first: Infrastruktur startet klein und eskaliert nur bei Bedarf (siehe `.claude/governance/model_escalation_policy.md`).

| Agent-Typ | Claude-Modell (Default) | Oodle-Modell (Default) | Oodle Eskalation |
|---|---|---|---|
| Infrastruktur (Personaler, Task Compactor, Context Packer, Dispatcher) | **Haiku** | `qwen2.5:7b-instruct` / `qwen3:8b` | S→M→L |
| Report Worker (QualitySignal) | **Haiku** | `glm-4.7-flash:latest` / `qwen2.5:7b-instruct` | S→M |
| TestOps (Light/Medium/Heavy) | **Haiku** | Light:`7b/8b` • Med:`phi4:14b` • Heavy:`70b/72b` | Light→Med→Heavy |
| Implementation Worker | **Sonnet** (nur wenn Gate) | `qwen2.5-coder:32b` / `deepseek-coder:33b-instruct-q4_K_M` | M→L |
| Architecture (L2+) | Sonnet | `phi4:14b` oder `70b/72b` | M→L |
| Technical/Systemic Critic (L3+) | Sonnet | `phi4:14b` (oder L bei multi-module) | M→L |

**Begründung:** Infrastruktur-Agents machen Struktur/Dispatch und profitieren von kleinen Modellen. Große Reasoning-Modelle (70b/72b) sind reserviert für harte Triage/Architektur.

## Haiku-Fallback-Regel (Benutzer-Direktive 2026-02-27)

Wenn ein **Haiku-Agent** erkennt, dass er die Task-Compactor-Output unzureichend findet und selbst nochmals aufarbeiten muss:

1. **Hochstufen auf Sonnet** (intern — gleicher Agentenlauf)
2. **Mindestens 32b Oodle** für die Neuformulierung nutzen
3. Aufgabe selbst lösen (nicht weiterreichen)
4. Zurück in Haiku-Modus für Routineaufgaben

**Task-Compactor-Pflicht:** Shortlists und Briefings müssen modell-spezifisch formuliert sein:
- Für Haiku: knapper, direktiver, bulletpoints mit exakten Anweisungen
- Für Sonnet: kann Kontext und Reasoning enthalten
- Für Implementation Agent: Technische Details, Dateinamen, exakte Methodensignaturen

## Arbeitsweise — Pflicht für alle Specialists

**Ollama-First:** Jeder Specialist empfängt ein Ollama-Briefing vom Team Lead als Arbeitsgrundlage.
Das Briefing kommt als `## Ollama Briefing` Block im Prompt. Es wird genutzt, nicht ignoriert.

**Korrektur-Pflicht:** Was Ollama falsch hat (fehlende Type Hints, falsche Modul-Platzierung, falsches Pattern) → der Specialist korrigiert es, bevor er den Code schreibt.

**Modell-Bewusstsein:** Specialists werden auf dem günstigsten geeigneten Modell ausgeführt.
Haiku für Infrastruktur, Sonnet 4.5 für Implementation, Sonnet für Architecture/Critics. Das beeinflusst nicht die Qualitätserwartung.

**Domain Sovereignty:** Jeder Agent arbeitet ausschließlich in seinem Fachgebiet.
Kein Agent übernimmt still Aufgaben aus dem Bereich eines anderen Agents.

**Informationsbeschaffung:** Agents suchen keine Dateien selbst. Sie stellen eine Informationsanfrage an den Librarian Agent. Der Librarian liefert die relevanten Dokumente und Textstellen.

**Fachfremde Arbeit:** Wenn ein Agent Arbeit aus einem anderen Fachgebiet benötigt, meldet er das an den Team Lead. Der Team Lead organisiert den geregelten Handoff zum zuständigen Specialist.

---

## Implementation Agent

**Zuständigkeit:** Python-Code schreiben und modifizieren in `src/`

**Schreibrechte:**
- `src/` (alle Python-Dateien)
- `<PROJECT_ROOT>/src/agents/` (Agent-Implementierungen)

**Eskaliert bei:**
- Neuen Top-Level-Modulen in `src/` (L2 — Modul-Boundary)
- Neuen externen Abhängigkeiten außerhalb stdlib (L2 — Designer Review)
- Änderungen an der Dependency-Richtung (L2)

**Code-Pflichten:**
- PEP 8, Type Hints auf allen public functions
- Max. 300 Zeilen pro Datei
- Keine hardcodierten Pfade (immer `config.XYZ`)
- `OllamaUnavailableError` nie still schlucken

---

## Architecture Agent

**Zuständigkeit:** Python-Modulstruktur, Abhängigkeitsentscheidungen, Framework-Integrität

**Schreibrechte:**
- `.claude/python/` (architecture.md, patterns.md)
- `Docs/References/`

**Eskaliert bei:**
- Änderungen an der Dependency-Richtung zwischen `src/`-Modulen
- Neuen Abhängigkeiten außerhalb stdlib

**Entspricht dem „Designer" für technische Code-Entscheidungen im Python-Kontext.**

---

## Documentation Agent

**Zuständigkeit:** Strukturierte technische Dokumentation erstellen und pflegen

**Schreibrechte:**
- `Docs/Documentation/`
- `Docs/Tutorials/`

**Output-Format:**
Jedes Dokument enthält: Zweck, Kontext, Implementierungsdetails, Bekannte Einschränkungen, Verwandte Systeme.

---

## Librarian Agent

**Zuständigkeit:** Zentrale Wissenszentrale — kennt alle Projektdaten, liefert zielgenaue Information an Agents

**Der Librarian ist der einzige Agent der aktiv in der Wissensbasis sucht.**
Alle anderen Agents stellen Informationsanfragen — sie suchen nicht selbst.

**Informationsanfrage-Format (von anderen Agents):**
```
Librarian, ich brauche: [Thema/Frage]
Zweck: [wofür brauche ich das?]
Agent: [wer fragt?]
```

**Librarian-Antwort-Format:**
```
Relevante Dateien: [Pfade]
Schlüsselstellen:
  [Datei:Zeile] — [extrahierter Text]
Ollama-Zusammenfassung: [bei komplexen Anfragen]
```

**Ollama-Setup:**
- `qwen2.5-coder:14b / quick` — schnelle Einzel-Datei-Extraktion
- `qwen2.5-coder:32b / brief` — tiefe Analyse über mehrere Dokumente

**Schreibrechte:**
- `Docs/References/`
- `.claude/knowledge/` (inkl. `index.md` — Wissensbasis-Index)

**Collective Pattern:** Bei mehreren parallelen Anfragen → Team Lead spawnt mehrere Librarian-Instanzen gleichzeitig. Jede bedient einen Requester. Alle teilen dieselbe (read-only) Wissensbasis.

**Aufgaben:**
- Wissensbasis-Index (`knowledge/index.md`) aktuell halten
- Informationsanfragen mit Ollama-gestützter Extraktion beantworten
- Redundanz erkennen und mergen
- Veraltete Einträge markieren
- Cross-References pflegen

---

## Collector Agent

**Zuständigkeit:** Korrektheit und Vollständigkeit validieren

**Schreibrechte:** Keine — nur lesend, Feedback an Team Lead

**Prüft:**
- Vollständigkeit der Implementierung gegen Akzeptanzkriterien
- Konsistenz von Docs mit tatsächlichem Code
- Lücken in Testabdeckung

---

## Validation Agent

**Zuständigkeit:** Syntax-Check, Tests, Imports

**Schreibrechte:**
- `Docs/Review/`

**Prüft:**
- Syntaktische Korrektheit (ast.parse)
- Import-Fehler (python3 -c "import src.main")
- Edge Cases (OllamaUnavailableError Handling, subprocess-Fehler, Ollama-Verbindung)

**Output:** Validation Report in `Docs/Review/`

---

## Pattern Recognition Agent

**Zuständigkeit:** Wiederverwendbare Abstraktionen erkennen

**Schreibrechte:**
- `.claude/python/patterns.md` (Erweiterungen)
- `.claude/knowledge/`

**Aufgaben:**
- Ähnliche Implementierungen über mehrere Module erkennen
- Abstraktionskandidaten vorschlagen
- Bereits extrahierte Patterns referenzieren statt duplizieren

---

## Skill Agent

**Zuständigkeit:** Meta-Berater für Team Lead — beobachtet Effizienz, berät bei Orchestrierungsentscheidungen, entwickelt Skills

**Standardmodus:** Still und beobachtend. Erzeugt keine Kosten wenn nicht aktiv einbezogen.

**Ollama-Setup:** `phi4:14b / architecture` für Effizienzanalysen — `qwen2.5-coder:14b / brief` für schnelle Routing-Checks

**Wird aktiv wenn:**
- Team Lead ihn explizit einbezieht (bei Effizienzfragen oder neuen Task-Typen)
- Kollisionen zwischen Agents erkannt werden
- Verbesserungspotential im Routing oder Delegation identifiziert wird
- Ein Task-Muster sich so oft wiederholt, dass ein neuer Skill sinnvoll ist

**Schreibrechte:**
- `.claude/skills.md` — Registry entwickelter Skills
- `.claude/collaboration.md` — Workflow-Empfehlungen für Szenarien

---

## Human Readable Document Agent

**Zuständigkeit:** Qualitätssicherung für alle Dokumente, die für menschliche Leser bestimmt sind — unabhängig vom Typ.

**Trigger:** Automatisch in Phase 4b — immer wenn ein Output für Menschen erzeugt wurde.

**Ollama:** `phi4:14b / architecture` — für Struktur- und Layout-Analyse.

**Schreibrechte:**
- `.claude/humaninterface/humanreadable.md` (Do's & Don'ts, Stilregeln)
- Schreibt innerhalb von `.claude/knowledge/` als Bibliotheks-Mitarbeiter — koordiniert mit Librarian

---

## Tutor Agent

**Zuständigkeit:** Qualitätssicherung wenn technische Inhalte in verständliche, lesbare Prosa umgewandelt werden sollen — primär für `Docs/Tutorials/`.

**Trigger:** Automatisch in Phase 4b — nur wenn der Documentation Agent ein Tutorial oder einen erklärenden Text erzeugt hat.

**Ollama:** `phi4:14b / architecture` — für Verständlichkeits- und Struktur-Analyse.

**Schreibrechte:**
- `.claude/humaninterface/documentation.md` (Do's & Don'ts, Tutorial-Regeln)
- Schreibt innerhalb von `.claude/knowledge/` als Bibliotheks-Mitarbeiter — koordiniert mit Librarian


---

## QualitySignal Aggregator (SpecialAgent)

**Zuständigkeit:**  
Aggregiert `ReportSpec` + `CriticReport` zu einem kompakten `QualitySignal` (status, severity, repeat_failures) und liefert dem Personaler eine **deterministische** Empfehlung (accept/retry/oodle_up/claude_up/gate_review).

Datei: `.claude/agents/qualitysignal_aggregator.md`

---

## Escalation Controller (SpecialAgent)

**Zuständigkeit:**  
Wendet die 2-stufige Eskalationslogik an (**zuerst Oodle**, dann Claude) basierend auf `QualitySignal` und Routing-Kontext. Schreibt Eskalationslogs in `Docs/Reports/`.

Datei: `.claude/agents/escalation_controller.md`
- Bulk Job Planner: `agents/operations/bulk_job_planner.md`
- Local Verifier O3: `agents/quality/local_verifier_o3.md`
- Result Relay Worker: `agents/docs/result_relay_worker.md`
- Batch Schema Validator: `agents/quality/batch_schema_validator.md`
- Skill Dispatcher: `agents/skill_dispatcher.md`
- Skill Scout: `agents/operations/skill_scout.md`
- Skill Planning Agent: `agents/operations/skill_planning_agent.md`
