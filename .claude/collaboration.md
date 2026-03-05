# Collaboration Guide — Python Orchestrator Agent System

> Szenario-spezifische Empfehlungen für Team-Komposition und Workload-Balancing.
> Verwaltet vom Skill Agent. Referenz für Team Lead bei Orchestrierungsentscheidungen.

---

## Wann welches Team zusammenstellen?

### Szenario A: Neue Python-Funktion/-Klasse implementieren

```
Ollama: qwen2.5-coder:32b / draft
Implementation Agent: sonnet
Collector: haiku (nur wenn >100 Zeilen oder externe Modul-Abhängigkeit)
Validation: nur wenn Subprocess-Handling oder Ollama-Client-Änderung
```

Kein Architecture Agent, keine Critics nötig — es sei denn Modul-Boundary-Entscheid ist unklar.

---

### Szenario B: Python-Architektur-Entscheid (neues Modul vs. Erweiterung?)

```
Ollama: phi4:14b / architecture
Architecture Agent (Designer): sonnet
Team Lead: Entscheid nach Architecture-Feedback
```

Kein Specialist nötig bis Entscheid gefallen.

---

### Szenario C: Bugfix (Single-File, klar isoliert)

```
Kein Ollama (L0)
Passender Specialist: haiku
Kein QA
```

Schnellstmögliche Ausführung — kein Overhead.

---

### Szenario D: Effizienz-Analyse des Teams

```
Ollama: phi4:14b / architecture (Systemanalyse als Basis)
Skill Agent: sonnet
Input: Ollama-Briefing + letzte 3-5 Tasks + routing.md + learning logs
Output: Empfehlung für Team Lead (collaboration.md Update)
```

Team Lead befragt Skill Agent wenn: gleicher Task-Typ mehrfach schlecht lief, Kosten unerwartet hoch, neue Task-Klasse aufgetaucht.

---

### Szenario E: Kritische Review (L3+)

```
Ollama: phi4:14b / architecture (Vorab-Analyse)
Technical Critic: sonnet
Systemic Critic: sonnet (nur bei L4)
Team Lead: Entscheid nach Critic-Inputs
```

Critics laufen parallel. Team Lead wartet auf beide bevor er entscheidet.

---

### Szenario F: Dokumentation nach Implementation (Phase 4a)

```
Kein Ollama
Documentation Agent: haiku
Librarian Agent: haiku (Index-Update)
```

Parallel ausführbar. Kein QA nötig. Löst automatisch Szenario J (Phase 4b) aus.

---

### Szenario G: Informationsanfrage (Agent braucht Kontext)

```
Specialist → Team Lead: "Ich brauche Wissen über [Thema]"
Librarian: haiku (Einzel-Datei) oder sonnet (Multi-Datei)
Ollama: qwen2.5-coder:14b/quick oder qwen2.5-coder:32b/brief
Output: Dateipfade + extrahierte Schlüsselstellen
→ Team Lead übergibt Informationspaket an Specialist
```

Kein Specialist sucht Dateien selbst — immer via Librarian.

---

### Szenario H: Parallele Librarian-Anfragen (Collective)

```
2+ Specialists brauchen gleichzeitig Informationen:
Team Lead → 2x Librarian (haiku, parallel via Task tool)
Jeder Librarian bedient einen Requester
Ergebnisse werden parallel zurückgeliefert
```

Spart Zeit — kein sequentielles Warten auf den Librarian.

---

### Szenario I: Domain Handoff (Orchestrator braucht Ollama-Client-Änderung)

```
Implementation Agent erkennt: "Hier brauche ich eine Änderung in ollama_client.py"
Implementation Agent → Team Lead: Meldung
Team Lead → Architecture Agent: Modul-Boundary-Entscheid
Architecture Agent → Team Lead: Entscheid + Spezifikation
Team Lead → Implementation Agent: Spezifikation als Kontext
Implementation Agent: implementiert mit diesem Kontext
```

Kein stilles Übernehmen — formaler Handoff über Team Lead.

---

### Szenario J: Human-Facing Docs QA (Phase 4b)

```
Ollama: phi4:14b / architecture (für beide Agents vor Beginn)
Human Readable Document Agent: sonnet
Tutor Agent: sonnet (nur wenn technische Inhalte → lesbare Prosa, d.h. Docs/Tutorials/)
```

**Trigger:** Automatisch nach Phase 4a (Szenario F) wenn Output für menschliche Leser bestimmt ist.

---

### Szenario K: Neuen Agent integrieren (Governance-Trinity-Update)

```
Ollama: Keins (projektspezifisch)
Implementation Agent: sonnet (alle drei Trinity-Dateien)
Systemic Critic: sonnet (wenn L4 — neue Governance-Regel)
```

**Kritisch:** Niemals Teilupdates. `specialists.md` + `execution_protocol.md` + `MEMORY.md` sind eine untrennbare Einheit.

---

## Warnsignale — Wann Skill Agent einbeziehen?

| Signal | Ursache | Empfehlung |
|---|---|---|
| Gleicher Task-Typ läuft 2x schlecht | Falsches Routing | Skill Agent analysieren lassen |
| Haiku produziert unbrauchbare Outputs | Task war L1, nicht L0 | Modell-Schwelle anpassen |
| Validation findet immer dieselben Fehler | Specialist-Learning-Log veraltet | Skill Agent + Pattern Recognition |
| Team Lead unsicher welches Team | Neuer Task-Typ | Skill Agent für Ersteinschätzung |
| Governance-Datei wurde isoliert geändert | Trinity-Regel verletzt | Sofort Trinity-Update nachziehen |

---

## Ressourcen-Faustregeln

| Situation | Kosten-Niveau | Team |
|---|---|---|
| L0 Bugfix | Minimal | 1x haiku |
| L1 Implementation | Niedrig | 1x sonnet + Ollama |
| L2 Architektur | Mittel | Ollama + Architecture Agent + ggf. Specialist |
| L3 Review | Hoch | Ollama + Specialist + Critics |
| Governance-Trinity-Update | Niedrig-Mittel | 1x sonnet (Implementation Agent) |
| Human-Facing Docs QA (Phase 4b) | Niedrig | 1-2x sonnet (parallel) |
| Effizienz-Analyse | Einmalig | Skill Agent (sonnet) |

## Operational defaults (v17.x)

- **German narrative input**: build a **Message Triad** first (`MessageTriadSpec`), then work from `work_brief`.
- **Fallback order**: work_brief → translation → source (original).
- **Hard STOP**: if Drift Sentinel FAILs, stop and fix drift before proceeding.
- **Policy**: use `policy_gatekeeper` to decide if deep_oodle / creative_feedback / rebuild / experiments are allowed.
- **Deep reasoning**: only use Deep Oodle with a Deliberation Pack built by `deliberation_pack_build`.

