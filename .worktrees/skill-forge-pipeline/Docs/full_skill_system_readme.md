# ClaudeClockwork Full Skill System

Dieses Repository enthält neben dem bestehenden Legacy-Skill-Runner jetzt ein **manifest-basiertes Full Skill System**, das aktuell primär unter **`.claude/skills/`** lebt.

## Einstieg

Direktes Ausführen eines manifest-basierten Skills:

```bash
python -m claudeclockwork.cli --project-root . --skill-id capability_map_build --inputs "{}"
```

Planer-basierte Auswahl:

```bash
python -m claudeclockwork.cli --project-root . --user-input "search the skill registry for migration"
```

## Design-Prinzip

- Kanonischer Manifest-Pfad ist aktuell **`.claude/skills/<category>/<skill_name>/`**
- Optional werden zusätzlich zukünftige `skills/`-Roots erkannt
- Jeder Skill besitzt ein `manifest.json`
- Legacy-Skills aus `.claude/tools/skills/` werden über Wrapper angebunden
- `.claude/tools/skills/skill_runner.py` bleibt als Bridge erhalten

## Aktueller Umfang

- **34 manifest-basierte Skills**
- **28 Legacy-Wrapper**
- **6 native Full-Skill-System-Skills**
- **2 Plugin-Skelette**
- **17 Referenz-Skills mit `SKILL.md`**

## Neue native Skills in dieser Runde

- `manifest_validate`
- `legacy_skill_inventory`
- `reference_skill_catalog`
- `plugin_scaffold`
- `plugin_registry_export`

## Nützliche Kommandos

Registry exportieren:

```bash
python -m claudeclockwork.cli --project-root . --skill-id manifest_registry_export --inputs "{}"
```

Plugin-Index exportieren:

```bash
python -m claudeclockwork.cli --project-root . --skill-id plugin_registry_export --inputs "{}"
```

Manifeste validieren:

```bash
python -m claudeclockwork.cli --project-root . --skill-id manifest_validate --inputs "{}"
```

Legacy-Abdeckung prüfen:

```bash
python -m claudeclockwork.cli --project-root . --skill-id legacy_skill_inventory --inputs "{}"
```

Weitere Details: `Docs/skill_system_audit_and_roadmap.md`.
