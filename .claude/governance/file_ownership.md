# File Ownership — Python Orchestrator Agent System

> Jede Datei gehört genau einem Agent. Kein Agent darf Dateien eines anderen bearbeiten.
> Cross-Domain-Änderungen gehen über Team Lead → Domain Handoff Protocol.

---

## Ownership-Tabelle

| Pfad / Muster | Owner Agent | Schreibrecht |
|---|---|---|
| `.claude/agents/*.md` | Team Lead | Governance-Definitionen |
| `.claude/agents/learning/team_lead.md` | Team Lead | Eigenes Learning Log |
| `.claude/agents/learning/implementation_agent.md` | Implementation Agent | Eigenes Learning Log |
| `.claude/agents/learning/documentation_agent.md` | Documentation Agent | Eigenes Learning Log |
| `.claude/agents/learning/librarian_agent.md` | Librarian Agent | Eigenes Learning Log |
| `.claude/agents/learning/collector_agent.md` | Collector Agent | Eigenes Learning Log |
| `.claude/agents/learning/validation_agent.md` | Validation Agent | Eigenes Learning Log |
| `.claude/agents/learning/pattern_recognition_agent.md` | Pattern Recognition Agent | Eigenes Learning Log |
| `.claude/agents/learning/skill_agent.md` | Skill Agent | Eigenes Learning Log |
| `.claude/agents/learning/critics/technical_critic.md` | Technical Critic | Eigenes Learning Log |
| `.claude/agents/learning/critics/systemic_critic.md` | Systemic Critic | Eigenes Learning Log |
| `.claude/agents/critics/*.md` | Team Lead / Architecture Agent | Critic-Definitionen |
| `.claude/governance/*.md` | Team Lead | Governance-Protokolle |
| `.claude/python/*.md` | Team Lead / Architecture Agent | Python-Standards |
| `.claude/knowledge/index.md` | Librarian Agent | Wissensbasis-Index |
| `.claude/knowledge/routing.md` | Skill Agent | Routing-Intelligence |
| `.claude/knowledge/*.md` (sonstige) | Librarian Agent | Knowledge-Einträge |
| `.claude/skills.md` | Skill Agent | Skills-Registry |
| `.claude/collaboration.md` | Skill Agent | Collaboration-Szenarien |
| `.claude/tools/*.py` | Implementation Agent | Tooling |
| `memory/*.md` | Team Lead | Cross-Session-Kontext |
| `Docs/Documentation/` | Documentation Agent | Technische Docs |
| `Docs/Tutorials/` | Documentation Agent | Guides |
| `Docs/References/` | Librarian Agent | Referenz-Dokumente |
| `Docs/Review/` | Validation Agent | Validation Reports |
| `Docs/Critics/` | Technical Critic / Systemic Critic | Critic-Outputs |
| `Docs/Plans/` | Team Lead | Pläne |
| `src/` | Implementation Agent | Python-Implementierung |
| `<PROJECT_ROOT>/src/agents/` | Implementation Agent | Agent-Implementierungen |

---

## Verletzungs-Protokoll

Wenn ein Agent eine Datei außerhalb seiner Ownership bearbeiten muss:

```
1. Agent meldet an Team Lead: "Ich brauche Änderung in [fremde Datei]"
2. Team Lead aktiviert den zuständigen Owner-Agent via Domain Handoff
3. Owner-Agent führt die Änderung durch
4. Owner-Agent meldet Abschluss an Team Lead
```

Keine stille Übernahme. Kein Editieren fremder Dateien — auch nicht "kurz mal schnell".

---

## Dokument-Platzierungskorrektur (BP-006)

Wenn ein Dokument am falschen Ort liegt (z. B. Referenz in `Docs/Plans/`, Plan in `Docs/Documentation/`):
1. Feststellung an Team Lead melden (aktueller Ort, vorgeschlagener Zielort)
2. Team Lead koordiniert Rücksprache mit Owner (User oder zuständiger Agent)
3. Verschiebung führt nur der Owner des Zielorts (oder Quellorts) durch
4. Keine stille Verschiebung ohne Freigabe

Vollständiges Protokoll: `governance/document_placement.md`.

---

## Spawn-Prompt Pflichtinhalt

Jeder Agent-Spawn über das Task-Tool muss enthalten:

```
## Projekt-Kontext
Python Orchestrator: Konsolenanwendung für autonome Ollama/Claude-Agenten-Orchestrierung.
Modul-Hierarchie: main → orchestrator → agents/* → ollama_client/claude_client → config
Dependency-Richtung: main → orchestrator → agents → clients (nie umgekehrt)
Patterns: OllamaFreeze, SelfContainedSpawn, StructuredOutput, AvailabilityGuard
PEP 8, Type Hints für alle public functions, max 300 Zeilen pro Datei.

## Deine Rolle & Schreibrechte
Rolle: [Agent-Name]
Du darfst NUR folgende Dateien schreiben: [explizite Liste]

## Governance
- Nur eigene Dateien bearbeiten (file_ownership.md)
- Lies Dateien zuerst vollständig vor dem Bearbeiten
- Ollama-First bei L1+ (wenn relevant)
- OllamaUnavailableError werfen, nie silent swallow

## Aufgabe
[Konkrete Aufgabe mit Akzeptanzkriterien]

## Zu lesende Kontext-Dateien
[Explizite Pfade]

## Ollama Briefing (wenn vorhanden)
[Output von ollama_client.py oder ollama_brief.py]
```

# File Ownership (mirror)

Primary Oodle ownership is defined in `.claude/governance/file_ownership.md`.  
Claude Code must respect those boundaries and request gates for risky changes.
