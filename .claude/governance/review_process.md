# Review Process

## Zweck

Der Review-Prozess stellt sicher, dass jede Implementierung korrekt, lesbar, dokumentiert und integrationskompatibel ist bevor sie als abgeschlossen gilt.

---

## Standard Review-Schritte

### 0. Hard QA Gate (PR-blocking)

Run the deterministic gate before human review:
- `qa_gate` (see `governance/qa_gate_policy.md`)

If the gate fails: **stop** and fix drift first.

### 1. Korrektheit prüfen (Collector Agent)

```
- Implementierung gegen alle Akzeptanzkriterien im Task Brief abgleichen
- Vollständigkeit: Sind alle geforderten Funktionen vorhanden?
- Korrektheit: Sind die Lösungen logisch korrekt?
- Keine Regressions (bestehende Funktionalität unberührt)?
```

### 2. Lesbarkeit prüfen (Collector Agent)

```
- Naming: PEP 8 eingehalten? (snake_case, PascalCase, UPPER_SNAKE_CASE)
- Struktur: Datei unter 300 Zeilen? (wenn nicht: Split prüfen)
- Type Hints: Alle public functions annotiert?
- Comments: Nur wo Logik nicht selbsterklärend ist?
- Keine Copy-Paste-Überbleibsel in Logs/Kommentaren
```

### 3. Dokumentation prüfen (Validation Agent)

```
- Technische Docs in Docs/Documentation/ aktuell?
- Relevante Referenzen in Docs/References/ vorhanden?
- MEMORY.md Update benötigt?
- .claude/python/patterns.md Update benötigt?
```

### 4. Integration Impact prüfen (Validation Agent)

```
- Syntax: ast.parse() erfolgreich?
- Import-Fehler: python3 -c "import src.main" ohne Fehler?
- OllamaUnavailableError korrekt propagiert (nicht silent)?
- Subprocess-Fehler abgefangen an Modul-Grenzen?
- Ollama-Verbindung: is_available() Guard vorhanden bei L1+?
```

### 5. Freigabe oder Rückgabe

```
APPROVED           → Phase 4 beginnt (Docs + Librarian)
APPROVED WITH CONDITIONS → Implementation hat Conditions-Liste zu erfüllen
REQUIRES REWORK    → Zurück zu Phase 1, neuer Review nach Rework
BLOCKED            → Eskalation an Team Lead
```

---

## Review-Output Format

```markdown
## Review: [Task-Name / PR-Name]
**Datum:** YYYY-MM-DD
**Reviewer:** [Agent-Rolle]
**Status:** APPROVED / APPROVED WITH CONDITIONS / REQUIRES REWORK / BLOCKED

### Korrektheit
[Befunde]

### Lesbarkeit
[Befunde — PEP 8, Type Hints, Zeilenzahl]

### Dokumentation
[Befunde]

### Integration Impact
[Befunde — Syntax-Status, Import-Status, OllamaUnavailableError-Handling]

### Conditions (wenn APPROVED WITH CONDITIONS)
- [ ] Condition 1
- [ ] Condition 2

### Rework-Scope (wenn REQUIRES REWORK)
[Was muss geändert werden?]
```

---

## Rework-Limit

Nach **2 Rework-Zyklen** auf demselben Task:
- Team Lead wird obligatorisch eingeschaltet
- Task wird neu bewertet (Komplexität unterschätzt?)
- Ggf. Eskalation an Architecture Agent oder User
