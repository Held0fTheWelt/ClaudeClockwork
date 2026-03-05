# Clockwork

Meta-Governance- und Tooling-Schicht für Multi-Agent-Claude/Ollama-Orchestrierung. Der Systemkern liegt in `.claude/`: Agent-Rollen, Governance-Protokolle, Skill Runner und JSON-Contracts. Anwendungscode lebt unter `src/` (projektbezogen).

---

## Quick Start

Umgebung prüfen (Boot-Check):

```bash
python .claude/tools/boot_check.py
```

Erwartung: je Zeile `[PASS]` oder `[FAIL]`, am Ende `Result: ALL CHECKS PASSED`.

Optional — Ollama-Verfügbarkeit testen:

```bash
python .claude/tools/test_ollama.py
# oder, falls vorhanden:
python src/main.py --task "test ollama"
```

Skill ausführen:

```bash
python .claude/tools/skills/skill_runner.py <skill_name> [args]
```

---

## Version & Status

- **Version:** siehe [.claude/VERSION](.claude/VERSION) (aktuell 17.7.0).
- **Roadmap:** [ROADMAP.md](ROADMAP.md) — Phasen, CBL-Rung, nächste Meilensteine.

---

## Wichtige Verzeichnisse

| Verzeichnis | Zweck |
|-------------|--------|
| `.claude/` | Systemkern: Agents, Governance, Skills, Contracts |
| `Docs/` | Living Documentation (Plans, Review, Critics, References, Tutorials) |
| `memory/` | Cross-Session-Kontext (Team Lead) |
| `.report/` | Berichte (kanonisch) |
| `.llama_runtime/` | Runtime-Zustand (Ledgers, Eval, Writes) |
| `.claude-performance/` | Telemetrie und Performance-Artefakte |

Details: [ARCHITECTURE.md](ARCHITECTURE.md), [CLAUDE.md](CLAUDE.md).

---

## Weitere Dokumentation

**Für Menschen:**

- [ARCHITECTURE.md](ARCHITECTURE.md) — Projektarchitektur, Runtime-Layout
- [ROADMAP.md](ROADMAP.md) — Phasen und Meilensteine
- [MODEL_POLICY.md](MODEL_POLICY.md) — Modell-Tiers und -Trigger
- [MEMORY.md](MEMORY.md) — Cross-Session-Kontext
- [QUALITY_TRACKING.md](QUALITY_TRACKING.md) — Qualitäts-Tracking

**Für Claude/Agents:**

- [CLAUDE.md](CLAUDE.md) — Session-Start, Protokoll, Workflow-Trigger
- [.claude/SYSTEM.md](.claude/SYSTEM.md) — System-Architektur, Agent-Hierarchie
- [.claude/INDEX.md](.claude/INDEX.md) — Einstieg im .claude-Kontext (Entry-Docs, Boot-Check)

**Skills:**

- [.claude/skills/registry.md](.claude/skills/registry.md) — Skill-Katalog
- [.claude/skills.md](.claude/skills.md) — Pointer auf Registry und Playbooks

---

## Voraussetzungen

- **Python 3** für Boot-Check, Skill Runner und Tools.
- **Ollama** ist optional; für L2+-Tasks (z. B. Architektur, neue Module) wird Ollama empfohlen. Wenn ein Task Ollama nutzt und Ollama nicht erreichbar ist, gilt das Freeze-Protokoll (keine Teilimplementierung). Siehe [CLAUDE.md](CLAUDE.md) und `.claude/governance/ollama_integration.md`.
