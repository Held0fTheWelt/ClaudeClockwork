# Self-Improvement Cycle

## Zweck

Nach jeder Major Task analysiert das System seine eigene Performance, identifiziert Ineffizienzen und implementiert Verbesserungen in Governance und Patterns.

---

## Post-Task Zyklus

### Schritt 1: Performance-Analyse (Team Lead)

```
- Performance-Log ausfüllen (performance/log_template.md)
- Metriken mit vorherigen Tasks vergleichen
- Auffälligkeiten identifizieren (Rework-Spitzen, Eskalations-Fehler)
```

### Schritt 2: Adversarielle Überprüfung (optional, aber empfohlen)

```
- War die Eskalationslevel-Klassifikation korrekt?
- Hat ein Agent seine Zuständigkeitsgrenzen überschritten?
- Wurden Patterns dupliziert statt wiederverwendet?
```

### Schritt 3: Ineffizienzen identifizieren

```
Häufige Quellen:
- Unklare Akzeptanzkriterien → Task Brief verbessern
- Fehlende Patterns in .claude/python/patterns.md → Pattern extrahieren
- Falsche Eskalationslevel-Klassifikation → Decision Policy anpassen
- Redundante Docs → Librarian Agent beauftragt mit Merge
```

### Schritt 4: Verbesserungen implementieren

```
Autonom (L0):
- patterns.md erweitern
- Performance-Log schreiben
- Kleine Klarstellungen in Governance-Docs

Requires Review (L1-L2):
- Neue Agent-Verantwortlichkeiten
- Geänderte Review-Schritte

Requires Critic (L4):
- Governance-Regeländerungen
- Eskalationsschwellen anpassen
```

### Schritt 5: Dokumentation aktualisieren

```
- .claude/python/patterns.md: neue Patterns
- MEMORY.md: stabile Erkenntnisse
- Docs/Documentation/: wenn Implementierungsdocs affected
- .claude/governance/: wenn Prozess-Verbesserung
```

### Schritt 6: Agent-Regeln anpassen (wenn notwendig)

```
Nur bei nachgewiesenen strukturellen Problemen:
- Verantwortlichkeits-Überlappungen bereinigen
- Schwellenwerte justieren
- Neue Agent-Rollen vorschlagen (→ L4 Eskalation!)
```

---

## Periodisches Review (alle 10 Major Tasks)

```
1. Agent-Effektivität bewerten (Welche Agents leisten am meisten?)
2. Verantwortlichkeiten anpassen (Überlappungen eliminieren)
3. Eskalationsschwellen verfeinern (zu oft? zu selten?)
4. Knowledge-Archiv bereinigen (veraltete Einträge)
5. Systemic Critic Gesamtbewertung anfordern
```

---

## Anti-Patterns (was zu vermeiden ist)

- **Governance-Creep**: Neue Regeln ohne Entfernen alter Regeln
- **Agent-Proliferation**: Neue Agents für jede Spezialaufgabe
- **Review-Theater**: Reviews die immer APPROVED liefern (kein adversarieller Wert)
- **Knowledge-Silos**: Erkenntnisse nur in Agent-Memory, nicht in `.claude/`
