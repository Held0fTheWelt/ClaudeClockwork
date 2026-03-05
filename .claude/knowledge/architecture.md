# Knowledge Architecture

## Wissens-Taxonomie

Alles Wissen im System ist in drei Typen eingeteilt:

| Typ | Ort | Lebensdauer |
|---|---|---|
| **Task Knowledge** | `Docs/Tasks/`, `Docs/Plans/` | Task-Duration |
| **Reference Knowledge** | `Docs/References/` | Projekt-Duration |
| **System Knowledge** | `.claude/` | Permanent |

---

## Indexierungs-Regeln

```
- Jeder Eintrag: getaggt nach Subsystem (Orchestration, Ollama, Claude-API, Workflow, Config, ...)
- Verknüpfung durch Abhängigkeiten (z.B. Orchestrator → OllamaClient → Config)
- Priorisiert nach Nutzungsfrequenz (häufig referenzierte Patterns → .claude/python/patterns.md)
```

---

## Librarian-Verantwortlichkeiten

| Aufgabe | Frequenz | Trigger |
|---|---|---|
| Redundanz erkennen + mergen | Post-Task | Wenn 2+ ähnliche Einträge existieren |
| Veraltete Einträge markieren | Periodisch | Nach API-Änderung oder Modul-Umbau |
| Cross-References pflegen | Post-Task | Wenn neues System dokumentiert |
| Retrieval-Pfade optimieren | Quarterly | Bei Knowledge-Bloat-Warnung |

---

## Wissens-Fluss

```
Implementierung
    ↓ (Pattern Recognition Agent)
Patterns identifiziert
    ↓ (Librarian Agent)
.claude/python/patterns.md ODER Docs/References/
    ↓ (Documentation Agent)
Docs/Documentation/ (detaillierte technische Dokumentation)
    ↓ (MEMORY.md Update)
Stabile Erkenntnisse in MEMORY.md
```

---

## Retrieval-Strategie

Wenn ein Agent Wissen sucht, folgt er dieser Reihenfolge:

1. **MEMORY.md** — stabile, häufig benötigte Erkenntnisse
2. **`.claude/python/patterns.md`** — projektspezifische Python-Muster
3. **`Docs/References/`** — detaillierte System-Referenzen
4. **`Docs/Documentation/`** — technische Implementierungsdetails
5. **Source Code direkt** — wenn keine Dokumentation vorhanden

---

## Wissens-Subsystem-Tags

| Tag | Beschreibung |
|---|---|
| `Orchestration` | `<PROJECT_ROOT>/src/orchestrator.py` — Task-Routing, Klassifikation |
| `Ollama` | `<PROJECT_ROOT>/src/ollama_client.py` — LLM-Inferenz, Freeze-Protokoll |
| `Claude-API` | `<PROJECT_ROOT>/src/claude_client.py` — Subagenten-Spawning |
| `Workflow` | `<PROJECT_ROOT>/src/workflow.py` — Trigger-Erkennung, Dok-Naming |
| `Config` | `<PROJECT_ROOT>/src/config.py` — Pfade, Modelle, Konstanten |
| `Agents` | `<PROJECT_ROOT>/src/agents/` — Specialist-Implementierungen |
| `Governance` | `.claude/governance/` — Prozessregeln |
| `Architecture` | `.claude/python/architecture.md` — Modul-Hierarchie |
| `Patterns` | `.claude/python/patterns.md` — Wiederverwendbare Patterns |

---

## Qualitäts-Schwellenwerte

Ein Knowledge-Eintrag wird als **veraltet** markiert wenn:
- 3+ Monate seit letzter Nutzung
- Modul das er beschreibt wurde umstrukturiert
- API die er beschreibt wurde geändert

Ein Knowledge-Eintrag wird **gelöscht** wenn:
- Als veraltet markiert + kein Update in 30 Tagen
- Vollständig durch einen anderen Eintrag abgedeckt
- Beschreibt ein System das nicht mehr existiert
