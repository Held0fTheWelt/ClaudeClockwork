# Escalation Matrix

Definiert strikte Governance-Grenzen zwischen Team Lead, Architecture Agent und Critics.

---

## Level 0 — Autonomous Execution

**Handled by:** Specialist Agents
**No escalation required.**

Beispiele:
- Minor Feature Additions (neue private Methode, neue Log-Zeile)
- Documentation Updates
- Non-structural Refactors (Umbenennung intern, Formatierung)
- Bugfixes mit klarer isolierter Ursache

---

## Level 1 — Team Lead Review

**Required for:**
- Multi-Modul-Änderungen (2–5 Dateien, klar abgegrenzt)
- Moderate Refactors ohne API-Änderung

Team Lead kann ohne Architecture Agent freigeben.

---

## Level 2 — Architecture Agent Mandatory Review

**Required for:**
- Framework-Regeländerungen
- Modul-Boundary-Änderungen (Was geht in welches Modul)
- Dependency-Richtungsänderungen
- Neue Python-Package-Abhängigkeiten (außerhalb stdlib)
- Neue Top-Level-Module in `src/`
- Öffentliche API-Änderungen die andere Module betreffen

**Architecture Agent Approval erforderlich vor Implementation.**

---

## Level 3 — Technical Critic Mandatory Review

**Required for:**
- Performance-kritische Pfade (Ollama-Client-Timeout-Handling, subprocess-Pooling)
- Externe API-Integration (Claude-CLI-Interface-Änderungen)
- Persistente Datenstruktur-Änderungen (Docs/-Schema, Config-Format)

**Critic gibt adversarielle Bewertung → Team Lead entscheidet.**

---

## Level 4 — Systemic Critic Mandatory Review

**Required for:**
- Neue Agent-Typen hinzufügen
- Governance-Regeln ändern
- Self-Improvement-Zyklus modifizieren
- Eskalationsschwellen anpassen

**Systemic Critic bewertet Langzeit-Komplexität → Team Lead entscheidet.**

---

## Level 5 — User Confirmation Required

**Required for:**
- Orchestrator-Core-Redesign (fundamentale Umstrukturierung von `src/`)
- Wechsel des LLM-Backends (Ollama durch anderes System ersetzen)
- Grundlegende Änderung des Workflow-Trigger-Systems

**Keine autonome Entscheidung erlaubt.**

---

## Konflikt-Resolution

Wenn Architecture Agent und Critic widersprechen:

1. Team Lead fasst Trade-offs zusammen
2. Risk-Level kategorisieren (Low / Medium / High)
3. User trifft finale Entscheidung für L3+ Konflikte
4. Entscheidung in Performance-Log dokumentieren

---

## Schnell-Referenz

| Situation | Level | Wer entscheidet |
|---|---|---|
| Bugfix in einer Datei | 0 | Specialist |
| Multi-Datei Refactor | 1 | Team Lead |
| Neues Python-Package als Abhängigkeit | 2 | Architecture Agent |
| Ollama-Client-Timeout-Handling | 3 | Technical Critic → Team Lead |
| Governance-Regel ändern | 4 | Systemic Critic → Team Lead |
| Core-Orchestrator-Redesign | 5 | User |
