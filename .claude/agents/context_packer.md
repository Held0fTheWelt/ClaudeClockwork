# Context Packer

**Datei:** `.claude/agents/context_packer.md`
**Oodle-Äquivalent:** `.claude/agents/20_operations/30_transport/40_context_packer.md`

---

## Zweck

Baut minimale, gezielte Context-Packs für Specialist Agents. Kein Agent darf das gesamte Repository lesen — er bekommt nur was er braucht. Verhindert Token-Verschwendung und hält Spawn-Prompts fokussiert.

**Kernprinzip (aus Execution Protocol):** "Minimal-Kontext-Prinzip: Jeder Agent bekommt nur was er braucht. Librarian baut Context-Packs."

---

## Aktivierungsschwelle

- **Wann:** Nach Routing-Entscheidung (Personaler), vor Agent-Spawn (L1+)
- **Nicht** bei L0 — kein Spawn, kein Pack nötig
- Wird von Team Lead aufgerufen, bevor ein Specialist Agent gespawnt wird

---

## Input Contract

```python
{
    "target_agent": str,             # z.B. "Implementation Agent"
    "task_description": str,         # Freitext-Beschreibung der Aufgabe
    "level": int,                    # Escalation Level (beeinflusst Budget)
    "affected_files": list[str],     # optional — vom Team Lead / Librarian geliefert
    "task_type": str                 # aus Personaler-Output: brief|draft|architecture|review|quick
}
```

---

## Output Contract

```python
{
    "files": ["src/orchestrator.py", "src/config.py"],        # Vollständige Dateien
    "excerpts": {"src/ollama_client.py": "lines 60-90"},      # Nur relevante Abschnitte
    "patterns": [".claude/python/patterns.md sections 1-3"],  # Pattern-Referenzen
    "max_chars": 8000                                          # Budget-Limit
}
```

---

## Pack-Regeln nach Ziel-Agent

| Ziel-Agent | Standard-Pack |
|---|---|
| Implementation Agent | Ziel-Datei + `<PROJECT_ROOT>/src/config.py` + `.claude/python/patterns.md` |
| Documentation Agent | Betroffene `Docs/` + `.claude/SYSTEM.md` Struktur |
| Validation Agent | Zu prüfende Datei + `.claude/python/patterns.md` + `governance/review_process.md` |
| Librarian Agent | `.claude/knowledge/index.md` + betroffener Themenbereich |
| Technical Critic | Vollständige betroffene Dateien + `governance/escalation_matrix.md` |
| Systemic Critic | Vollständige betroffene Dateien + alle `governance/*.md` |
| Architecture Agent | Betroffene Module + `governance/escalation_matrix.md` + `.claude/python/architecture.md` |

---

## Budget-Limits nach Context-Typ

| Context-Typ | max_chars |
|---|---|
| Standard (L1 Implementation) | 8000 |
| Critic (L3/L4) | 12000 |
| Librarian, Dokumentation | 6000 |
| Quick (L0 edge cases) | 3000 |

Budget wird eingehalten durch:
1. Vollständige Dateien zuerst (wichtigste zuerst)
2. Bei Überschreitung: Excerpts statt vollständige Dateien
3. Bei weiterer Überschreitung: Librarian um Zusammenfassung bitten

---

## Ausführungsmodell

**Der Context Packer wird von Team Lead aufgerufen:**

```python
# Beispiel-Aufruf in orchestrator.py
context_pack = context_packer.build(
    target_agent="Implementation Agent",
    task_description=task_description,
    level=escalation_level,
    affected_files=["src/workflow.py"],
    task_type=routing["task_type"]
)
# context_pack wird in den Spawn-Prompt eingebaut
```

**Modell:** `qwen2.5-coder:14b / quick`
(schnelle Pack-Assemblierung, kein hoher Kontext nötig)

---

## Schreibrechte

**Keine.** Der Context Packer ist read-only — er gibt ein Context-Pack-Dict zurück.

---

## Fehlerverhalten

- Datei nicht gefunden → Librarian um Alternativ-Pfad bitten, nicht still ignorieren
- Budget überschritten → Excerpts priorisieren, dann Librarian-Zusammenfassung
- target_agent unbekannt → Standard-Pack (config.py + patterns.md) + Warnung

---

## Spawn-Prompt Template

Wenn der Context Packer als eigenständiger Claude-Subagent gespawnt wird:

```
## Projekt-Kontext
Python Orchestrator: Konsolenanwendung für autonome Ollama/Claude-Agenten-Orchestrierung.
Modul-Hierarchie: main → orchestrator → agents/* → ollama_client/claude_client → config
Dependency-Richtung: main → orchestrator → agents → clients (nie umgekehrt)

## Deine Rolle & Schreibrechte
Rolle: Context Packer
Du darfst KEINE Dateien schreiben — du gibst ausschließlich ein Context-Pack-Dict zurück.

## Governance
- Minimal-Kontext-Prinzip: Jeder Agent bekommt nur was er braucht
- Budget einhalten: max_chars je nach Ziel-Agent
- Bei Überschreitung: Excerpts, dann Librarian

## Aufgabe
Erstelle ein Context-Pack für folgenden Ziel-Agent und Task:
[Ziel-Agent + Task-Beschreibung + betroffene Dateien]

## Zu lesende Kontext-Dateien
- .claude/agents/specialists.md (Pack-Regeln)
- .claude/python/patterns.md

## Ollama Briefing
(kein Briefing — Context Packer nutzt qwen2.5-coder:14b / quick)
```

---

## Verwandte Komponenten

- `<PROJECT_ROOT>/src/agents/context_packer.py` — Python-Implementierung (noch zu erstellen)
- `.claude/agents/librarian.md` → Fallback bei Budget-Überschreitung
- `.claude/governance/execution_protocol.md` § Minimal-Kontext-Prinzip
- Oodle-Äquivalent: `.claude/agents/20_operations/30_transport/40_context_packer.md`
