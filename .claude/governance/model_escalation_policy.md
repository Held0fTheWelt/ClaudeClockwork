# Model & Agent Escalation Policy

**Ziel:** Token-/Kostenreduktion bei gleichbleibender Qualität durch *small-first* Routing, kontrollierte Eskalation und eine feste 3-Ebenen-Agenthierarchie.

Diese Policy ist die kanonische Referenz für:

- **Stellschraube #1:** höheres/anderes **lokales Oodle-Modell**
- **Stellschraube #2:** höheres **Claude-Modell**

---

## 1) Agent Hierarchie (3 Ebenen)

### Orchestrator (Control Plane)
- Intake → Routing → Budget → Dispatch → Merge → Gates → Archive
- macht **keine** tiefe Implementierung

### SpecialAgents (Departments)
- liefern Capabilities, bauen Packs, normalisieren Ergebnisse
- arbeiten mit **kleinem Kontext**

### Worker (Execution Plane)
- schreiben Code/Reports, triagieren Tests, fixen Bugs
- bekommen **Pack + TasklistSpec** (nicht die gesamte Ursprungskonversation)

---

## 2) Trust Modes (Context-Kosten kontrollieren)

Jeder Handoff trägt einen Trust Mode:

- `inherit`: Worker vertraut **TasklistSpec + Pack** (kein Full-Read)
- `verify`: Worker bekommt zusätzlich **Goal/Constraints Extract** (10–20 Zeilen)
- `rebuild`: Worker ignoriert TasklistSpec und baut Plan neu (teuer)

**Default:** `inherit`.
`rebuild` nur bei `risk=high` oder `confidence < 0.5`.

---

## 3) Contracts (Sinnhaftigkeit)

Contracts wirken nur dann „komisch“, wenn man sie als Overhead sieht. In Agent-Teams sind sie der **Context-Sparer**:

- **Deterministisch**: Merger/Gates können maschinell entscheiden
- **Routing-fähig**: Personaler kann auf Feldern (risk/confidence/errors) routen
- **Lernfähig**: Quality Tracking pro Modell/Agent/Task wird stabil

Freitext ist erlaubt in `notes`/`rationale`, aber nicht als Ersatz für Kernfelder.

---

## 4) Eskalationsleiter (Oodle → Claude)

### 4.1 Oodle Modell-Tiers (lokal)

- **Tier S (small):** 7b–14b (Routing, Packing, Admin, schnelle Reviews)
- **Tier M (medium):** 32b–33b (Implementation, konkrete Fixes)
- **Tier L (large):** 70b–72b (hard reasoning, multi-module triage)

### 4.2 Claude Tiers (cloud)

- **Claude S:** Haiku (administrativ, dispatch, leichte Reviews)
- **Claude M:** Sonnet (Plan/Review/Debug mittel)
- **Claude L:** höchstes verfügbares Reasoning (nur Gate-getrieben)

### 4.3 Regel: Erst Oodle, dann Claude

Wenn ein Ergebnis unzureichend ist, eskaliere in dieser Reihenfolge:

1) **Oodle**: S → M → L (oder Modellfamilie wechseln, z. B. qwen → llama)
2) **Claude**: Haiku → Sonnet → Higher

---

## 5) Kritiker-Feedback Loop für den Personaler

Der Personaler soll **zwischen** Durchläufen Signal bekommen, ob sein Routing gut war.
Das passiert über den **Report Worker**, der eine Fehler-/Qualitätsdichte auswertet.

### 5.1 Report Worker liefert `QualitySignal`

- `error_count` (harte Fehler)
- `warning_count`
- `recurrence` (selbe Fehler wiederholt?)
- `confidence_drop` (z. B. Reviewer unsicher)
- `recommend_escalation` (none|oodle|claude)

### 5.2 Schwellen (Default)

- **Escalate Oodle** wenn:
  - `error_count >= 3` **oder**
  - `recurrence >= 2` **oder**
  - `confidence_drop` stark

- **Escalate Claude** wenn:
  - Oodle Tier L bereits genutzt und weiterhin `error_count >= 2`
  - oder `risk=high` Gate triggert

### 5.3 Kritiker als Korrektiv

Wenn Report Worker `recommend_escalation != none` liefert, muss der Personaler:

1) Kritiker-Report (technical/systemic) anfordern **oder** vorhandenen einlesen
2) Routing-Entscheidung anpassen
3) die Änderung im Routing-Dict begründen (`rationale`)

---

## 6) TestOps Sonderregel (kostenlos → mehr Durchläufe ok)

Tests werden deterministisch ausgeführt. LLMs triagieren nur Logs und erstellen Fix-Pläne.

- Light → Medium → Heavy eskalieren (lokal)
- erst bei wiederholtem Scheitern Claude eskalieren

---

## 7) Claude Tier Policy (Full Bandwidth, Cost-Aware)

**Grundsatz:** *Small-first*, dann über unabhängige Verifikation absichern. Eskalation erfolgt **zuerst über Oodle**, erst danach über Claude.

### Claude Tiers (Cloud)

- **C0 — Low-Level / Cheap:** Claude **4** / **4.1**
  - Admin/Dispatch, Checklisten, “stumpfe” Tasklist-Abarbeitung, einfache Format-/Refactor-Routinen (wenn über Packs geführt).
- **C1 — Fast:** Claude **4.5 Haiku**
  - Task Compaction, schnelle Reviews, kurze Rückfragen, “was ist kaputt?”-Triaging.
- **C2 — Precise:** Claude **4.5 Sonnet**
  - Präzise Implementierung/Reviews, diff-basierte Korrekturen, schwierige Bugfixes.
- **C3 — Critical Gate (sparsam):** Claude **4.6 Sonnet**
  - Nur für *entscheidende* Stellen: High-Risk Fix, finale Architektur-Entscheidung, “last resort” Debug.
- **C4 — Disabled by default:** **Opus 4.6**
  - Zu teuer → nur manuell, außerhalb normaler Automationen.

### Eskalationsregel (Claude)

1. **C0 → C1** wenn Output unklar/inkonsistent, aber Risiko niedrig ist.
2. **C1 → C2** wenn präzise Engineering-Arbeit nötig ist (Code-/Designqualität).
3. **C2 → C3** nur wenn: wiederholtes Scheitern, High-Risk, Security/Determinismus/Governance Gate.
4. **C4** nur manuell.

---

## 8) Pattern: Cheap Doer + Independent Verifier

Wenn ein günstiger Agent (C0/C1 oder O0/O1) nur “ausführt”, **muss** ein unabhängiger Verifier prüfen:

- **Doer:** führt TasklistSpec aus, erstellt Diff/Artefakte
- **Verifier:** prüft Diff/Tests/Logs (O2/O3 oder C2)
- **Governor:** entscheidet Accept/Retry/Escalate (Critic / Governance Gate)

Dieses Pattern spart Kontext, weil der Doer nicht “denkt”, sondern arbeitet — und Qualität trotzdem gesichert wird.
