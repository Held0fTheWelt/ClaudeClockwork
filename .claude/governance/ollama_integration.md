# Ollama Workload Integration

## Kernprinzip

Ollama übernimmt so viel Arbeit wie möglich — Claude Agents prüfen, korrigieren, und wenden Projektkontext an. Ziel: maximale Kostenreduktion bei Claude API-Tokens.

```
Ollama (lokales Modell)
  → Rohanalyse oder vollständiger Implementation-Draft
  → kennt Python-APIs, kann Code generieren

Claude Agent (Sonnet)
  → Qualitätskontrolle: passt das zu DIESEM Projekt?
  → korrigiert Fehler (fehlende Type Hints, falsche Modul-Platzierung, falsches Pattern)
  → wendet projekt-spezifische Patterns an die Ollama nicht kennt
  → finaler commit-bereiter Code
```

**Effektive Aufgabenteilung:**
- `brief` + `architecture` → Ollama: ~80% der Analyse. Claude: Verifikation + Entscheid.
- `draft` → Ollama: ~60–70% des Codes. Claude: Review + Korrekturen + Projektkontext.
- `review` → Ollama: vollständige Erst-Prüfung. Claude: Abnahme oder Eskalation.

---

## Hardware-Routing

| Gerät | VRAM/RAM | Modelle die passen | Optimale Nutzung |
|---|---|---|---|
| **RTX 3080** | 10 GB VRAM | ≤13B Q8 oder ≤30B Q4 | GPU-Inferenz (~760 GB/s Bandbreite) |
| **CPU 7950X3D** | 64 GB DDR5 | bis ~50B Q8 oder 70B Q4 | Modelle die nicht in VRAM passen |

**Kritische Regel: Hybrid = langsam.**
Passt ein Modell nicht vollständig in den VRAM, muss Ollama Schichten zwischen RAM und VRAM aufteilen. Der PCIe-Transfer wird Engpass → kann langsamer sein als reines CPU.

```bash
# Explizit CPU erzwingen (kein GPU-Hybrid):
OLLAMA_NUM_GPU=0 ollama run qwen2.5-coder:32b

# GPU forcieren (nur wenn Modell sicher reinpasst):
OLLAMA_NUM_GPU=99 ollama run qwen2.5-coder:14b
```

---

## Modell-Empfehlungen

### Primäre Modelle (für die tägliche Arbeit)

| Modell | Hardware | Task Types | Agent-Typ | Stärke |
|---|---|---|---|---|
| `qwen2.5:72b` / `llama3.3:70b` | CPU (64 GB RAM, Q4) | `brief`, `architecture` | **Infrastruktur** (Personaler, Diener, Tester) | Breites Reasoning für Shortlists + Routing |
| `qwen2.5-coder:32b` | CPU (64 GB RAM) | `draft`, `brief` | **Implementation Agent** (≤33b) | Beste Code-Qualität, komplett in RAM |
| `phi4:14b` | GPU (10 GB VRAM) | `architecture`, `brief` | Architecture/Critics (L2+) | Überragendes Reasoning für Architektur |
| `qwen2.5-coder:14b` | GPU (10 GB VRAM) | `review`, `quick` | Review-Tasks | Schnell, gut für Code-Review |

### Agent → Claude-Modell-Mapping (kanonisch)

| Agent-Typ | Claude-Modell | Oodle-Modell |
|---|---|---|
| Infrastruktur (Personaler, Diener, Tester, Context Packer) | **Haiku** | **70b/72b** (CPU) |
| Implementation Agent | **max. Sonnet 4.5** | **max. 33b** (qwen2.5-coder:32b, CPU) |
| Architecture Agent (L2) | Sonnet | phi4:14b (GPU) |
| Technical Critic (L3) | Sonnet | phi4:14b (GPU) |
| Systemic Critic (L4) | Sonnet | phi4:14b (GPU) |

### Optionale Ergänzungen

| Modell | Stärke | Wann nutzen |
|---|---|---|
| `qwen2.5-coder:7b` | Sehr schnell | Triviale Checks, L0-Tasks |
| `deepseek-r1:14b` | Chain-of-Thought Reasoning | Komplexe Architektur-Entscheidungen |
| `qwen2.5:32b` | Allgemeines Reasoning | Wenn Coder-Bias stört |

---

## Tool-Aufruf

**Importierbares Modul:** `<PROJECT_ROOT>/src/ollama_client.py`
**Legacy Script:** `.claude/tools/ollama_brief.py`

```python
from src.ollama_client import OllamaClient, OllamaUnavailableError

client = OllamaClient()

# Architecture decision with phi4 on GPU:
result = client.architecture(
    "Should the Ollama client timeout logic live in ollama_client.py or orchestrator.py?"
)

# Implementation draft with 32b on CPU:
result = client.draft(
    "Implement a Python function that checks if a port is open on localhost"
)

# Code review:
code = open("src/orchestrator.py").read()
result = client.review(f"Review this Python code:\n\n{code}")
```

**Bash (for Claude Code integration):**
```bash
# Syntax:
echo "task description" | python3 <PROJECT_ROOT>/.claude/tools/ollama_brief.py [model] [type]

# Types: brief | draft | architecture | review | quick
```

---

## Agent-Entscheidungsprotokoll

### Nach Erhalt des Ollama-Outputs — Was prüft der Claude Agent?

**Bei `brief` / `architecture`:**
```
✓ Nennt das Briefing korrekte Python-Module? (z.B. ollama_client, nicht requests)
✓ Ist die vorgeschlagene Modul-Platzierung korrekt?
✓ Werden die Mandatory Patterns erwähnt? (OllamaFreeze, Type Hints, max 300 Zeilen)
→ Accept: Briefing als Kontext verwenden
→ Refine: Kontext ergänzen, nochmal senden (max. 2x)
→ Skip: Ollama unavailable oder 2 Refinements ohne Verbesserung
```

**Bei `draft`:**
```
✓ Sind Type Hints auf allen public functions vorhanden?
✓ PEP 8 eingehalten?
✓ Keine hardcodierten Pfade? (alles über config.XYZ)
✓ OllamaUnavailableError korrekt propagiert (nicht silent)?
✓ Datei unter 300 Zeilen?
→ Accept & Apply: Code direkt in Projekt-Dateien schreiben
→ Correct & Apply: Fehler inline korrigieren, dann schreiben
→ Reject: Struktur fundamental falsch (Layer-Verletzung) → manuell implementieren
```

**Bei `review`:**
```
✓ Sind alle Critical-Issues valide (nicht false positives)?
→ Accept: Review-Report als Grundlage für Validation Agent
→ Correct: False positives entfernen, eigene Findings ergänzen
```

### Refinement-Schleife (max. 2 Iterationen)

```python
from src.ollama_client import OllamaClient

client = OllamaClient()

# Iteration 1: Basic request
result = client.draft("Implement OllamaClient.call_timed() method")

# Agent checks: too generic? Wrong module placement?
# Iteration 2: With additional context
result = client.draft(
    "Implement OllamaClient.call_timed() method",
    extra_context=(
        "Target file: src/ollama_client.py\n"
        "Must return tuple[str, float] — content and tok/s\n"
        "Must raise OllamaUnavailableError, not return None\n"
        "Use urllib.request only, no requests library"
    )
)
```

---

## Wann welcher Task-Type

| Situation | Ollama-Type | Modell | Erwartetes Claude-Delta |
|---|---|---|---|
| Neue Python-Funktion implementieren (L1) | `draft` | `qwen2.5-coder:32b` | ~30–40% Korrekturen |
| Architektur-Entscheid (L2) | `architecture` | `phi4:14b` | Verifikation, selten Korrekturen |
| Code-Review vor Validation Agent | `review` | `qwen2.5-coder:14b` | False-Positive-Filter |
| Schnelle technische Frage (L0) | `quick` | `qwen2.5-coder:7b` | Direkte Nutzung |
| Komplexes System-Design (L3+) | `architecture` | `deepseek-r1:14b` | Tiefere Prüfung nötig |

---

## Wann Ollama obligatorisch vs. optional vs. skip

| Eskalationslevel | Ollama aufrufen? | Type |
|---|---|---|
| L0 — Minor, eine Datei | Nein — gar nicht aufrufen (Overhead > Nutzen) | — |
| L1 — Multi-Datei, klare Grenzen | Optional — empfohlen bei >50 Zeilen Code | `brief` oder `draft` |
| L2 — Architecture Review | Obligatorisch | `architecture` |
| L3+ — Critic Review | Obligatorisch | `architecture` + ggf. `review` |

> **Wichtig:** "Nein" bei L0 bedeutet: Ollama wird erst gar nicht aufgerufen.
> Wird Ollama aufgerufen (L1+) und ist nicht erreichbar → immer FREEZE, nie stilles Weitermachen.

---

## Ollama-Status prüfen

```bash
# Läuft Ollama? (empfohlen — funktioniert ohne PATH)
curl -s http://localhost:11434/api/tags \
  | python3 -c "import sys,json; [print(m['name']) for m in json.load(sys.stdin)['models']]"

# Oder: direkt über Binary
OLLAMA="/c/Users/YvesT/AppData/Local/Programs/Ollama/ollama.exe"
"$OLLAMA" list
```

---

## Freeze Protocol — Obligatorisch bei Ollama-Ausfall

**Ollama ist kein optionales Hilfsmittel — es ist die Workload-Basis.**
Ein Freeze ist kein Vollstopp — es ist ein **partieller Hold**: nur der Agent, der Ollama benötigt, wartet.

### Ablauf bei OllamaUnavailableError

```
1. Betroffener Agent (der Ollama aufgerufen hat) → stoppt sofort
   Kein Teilimplementieren ohne Briefing.

2. Parallel laufende Agents → arbeiten weiter, bewahren Ergebnisse auf

3. Team Lead gibt FREEZE-Report aus:

   ╔══════════════════════════════════════════════════════════╗
   ║  OLLAMA UNAVAILABLE — PARTIAL FREEZE                    ║
   ║                                                          ║
   ║  Frozen:    [Agent + Aufgabe]                            ║
   ║  Preserved: [Liste bereits erledigter Teilergebnisse]   ║
   ║  Waiting:   Ollama restoration at localhost:11434        ║
   ║                                                          ║
   ║  Next steps:                                             ║
   ║  1. Start Ollama (Windows tray or app)                   ║
   ║  2. Test: python3 <PROJECT_ROOT>/src/main.py          ║
   ║           --task "test ollama"                           ║
   ║  3. Resume — preservierte Ergebnisse werden übergeben   ║
   ╚══════════════════════════════════════════════════════════╝

4. Kein autonomer Retry — Agent wartet auf User-Signal "test ollama" / "resume"
```

### Resume nach Wiederherstellung

```
User: "test ollama" → PASS
  → Team Lead übergibt preservierte Ergebnisse an frozen Agent
  → Ollama-Briefing nachholen
  → Task fortsetzen als wäre nichts gewesen
```

**Kein "Skip → weiter".** Der Freeze-Zustand bleibt bis Ollama operational ist.

---

## test-ollama — Funktionstest

```bash
python3 <PROJECT_ROOT>/src/main.py --task "test ollama"
```

**Was der Test prüft:**
1. Ollama erreichbar unter `localhost:11434`
2. Mindestens ein Modell installiert
3. Inferenz liefert validen Python Output
4. Ausgabe von: Modellname, tok/s, Output-Länge, Pass/Warn

**Exit-Codes (via test_ollama.py):**
- `0` — PASS: Ollama operational, Agents dürfen starten
- `1` — FAIL: Ollama nicht erreichbar
- `2` — FAIL: Kein Modell installiert
- `3` — FAIL: Inferenz fehlgeschlagen
