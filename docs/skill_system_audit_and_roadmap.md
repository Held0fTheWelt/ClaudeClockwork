# Skill System Audit and Roadmap

**Current phase list and inventory:** See `roadmaps/Roadmap_ClockworkV18.md` and `mvps/MVP_Phase*.md`. This document is legacy audit context; counts below may be outdated.

## Aktueller Ist-Zustand nach erneuter Prüfung

Die erneuerte ZIP enthält jetzt **drei parallele Schichten**, die sauber gegeneinander abgegrenzt werden müssen:

1. **Legacy-Python-Skills** unter `.claude/tools/skills/*.py`
2. **Manifest-basiertes Full Skill System** unter `.claude/skills/**/manifest.json`
3. **Referenz-/Prompt-Skills** unter `.claude/skills/**/SKILL.md`

Nach erneuter Prüfung und Bereinigung ergibt sich aktuell:

- **94 Python-Module** unter `.claude/tools/skills/` (davon **91** runnable Legacy-Skills, **2** interne Helper, **1** Skill-Runner-Bridge)
- **34 manifest-basierte Skills** unter `.claude/skills/**/manifest.json`
- davon **28 Legacy-Wrapper** und **6 native neue Skills**
- **17 Referenz-Skills** mit `SKILL.md`
- **2 Plugin-Skelette** unter `plugins/`
- **5 Tests**, aktuell **alle grün**

## Wichtigster technischer Befund

Der größte echte Integrationsfehler war kein fachlicher, sondern ein **Pfad-/Laufzeitproblem**:

- die Runtime suchte in `skills/`
- der tatsächliche Manifest-Bestand lag in `.claude/skills/`

Dadurch war das neue System vorhanden, aber **nicht wirklich verdrahtet**. Das ist jetzt bereinigt:

- `build_registry()` erkennt jetzt standardmäßig **`.claude/skills` und optional `skills`**
- die Runtime ergänzt die nötigen Importpfade (`project_root`, `project_root/.claude`)
- `skill_registry_search`, `skill_scaffold` und `capability_map_build` kennen jetzt beide Welten
- die Registry exportiert jetzt **Manifestpfad, Source-Root und Bridge-Status**

## Was neu hinzugefügt wurde

### Neue native Skills

1. `manifest_validate`
2. `legacy_skill_inventory`
3. `reference_skill_catalog`
4. `plugin_scaffold`
5. `plugin_registry_export`
6. `manifest_registry_export` (bereits vorhanden, jetzt erweitert)

### Neue Wrapper-Skills

1. `cleanup_apply`
2. `cleanup_plan_apply`
3. `code_clean`
4. `code_clean_scan`
5. `repo_clean`
6. `repo_clean_scan`
7. `determinism_harness`
8. `contract_drift_sentinel`
9. `schema_batch_validate`
10. `evidence_init`
11. `evidence_router`
12. `release_cut`

### Neue Plugin-Skelette

- `plugins/filesystem/plugin.json`
- `plugins/git/plugin.json`

## Was im Bestand besonders wertvoll bleibt

### 1. QA / Drift / Determinismus

Diese Gruppe ist weiterhin besonders wertvoll und sollte in der nächsten Welle weiter manifestisiert oder nativ gemacht werden:

- `repo_validate`
- `spec_validate`
- `qa_gate`
- `policy_gatekeeper`
- `determinism_proof`
- `hardening_scan_fix`
- `drift_semantic_check`
- `team_topology_verify`
- `reference_fix`

### 2. Evidence / Artifact / Release

Der Bestand enthält bereits eine sehr brauchbare Pipeline-Idee:

- `evidence_init`
- `evidence_router`
- `evidence_bundle_build`
- `security_redactor`
- `release_cut`
- `outcome_event_generate`
- `outcome_ledger_append`

### 3. Routing / Adaptation

Diese Skills haben weiterhin hohen Architekturwert, sind aber noch nicht gut genug vom Kern gelöst:

- `bandit_router_select`
- `model_routing_select`
- `model_routing_record_outcome`
- `route_autotune_suggest`
- `route_profile_patch_pack`
- `route_profile_update`
- `escalation_router`

### 4. Referenz-Skills mit Ideenwert

Die neuen `SKILL.md`-Bestände sollten nicht als direkte Runtime-Skills missverstanden werden. Sie sind aktuell eher **Skill-/Prompt-/MCP-Referenzen**. Für die weitere Architektur besonders nützlich sind:

- `mcp-builder`
- `skill-creator`
- `web-artifacts-builder`
- `webapp-testing`
- `pdf`
- `docx`
- `pptx`
- `xlsx`
- `theme-factory`
- `frontend-design`
- `canvas-design`

Diese Gruppe sollte in Zukunft eher als **Resource-/Prompt-/Plugin-Ebene** behandelt werden als als direkter Python-Skill.

## Roadmap zur Vollimplementierung

### Phase 0 — Stabilisierung des eingebauten Kerns

Status: **erledigt in dieser Runde**

- Registry auf `.claude/skills` umgestellt
- Dual-Root-Support (`.claude/skills`, `skills`) ergänzt
- Registry-Export und Plugin-Export aktualisiert
- Tests repariert und erweitert

### Phase 1 — Manifest-Härtung

Ziel: aus dem aktuellen Wrapper-System ein belastbares Runtime-System machen.

Arbeitspunkte:

- Manifest-Schema formalisieren
- Pflichtfelder und Typen per Validator absichern
- Import-/Entrypoint-Prüfung in CI verankern
- `manifest_validate` auf JSON-Schema- und Import-Checks ausbauen
- Kategorien, Tags, Aliase und Permissions konsequent normalisieren

### Phase 2 — Wrapper-Welle 3

Ziel: die wichtigsten unwrapped Legacy-Skills kontrolliert ins neue System ziehen.

Nächste Kandidaten mit hoher Priorität:

- `determinism_proof`
- `hardening_scan_fix`
- `drift_semantic_check`
- `team_topology_verify`
- `reference_fix`
- `outcome_event_generate`
- `outcome_ledger_append`
- `clockwork_version_bump`
- `telemetry_summarize`
- `performance_toggle`
- `performance_finalize`

### Phase 3 — Native Kern-Services statt Wrapper

Ziel: wichtige Meta- und QA-Skills nicht dauerhaft nur über Legacy-Adapter laufen lassen.

Zuerst nativ neu bauen:

- `skill_registry_search`
- `skill_scaffold`
- `capability_map_build`
- `repo_validate`
- `spec_validate`
- `qa_gate`

Danach:

- `evidence_bundle_build`
- `security_redactor`
- `parity_scan_and_mvp_planner`
- `eval_run`
- `pdf_quality`

### Phase 4 — Plugin Runtime

Ziel: Skills sauber zu Plugins bündeln.

Arbeitspunkte:

- `plugin.json`-Vertrag finalisieren
- Plugin-Discovery aus `plugins/*/plugin.json`
- Enable/Disable-Zustand speichern
- Dependency-Resolver einführen
- Plugin → Skill-Index materialisieren
- Lifecycle-Hooks vorbereiten (`on_install`, `on_enable`, `on_disable`, `healthcheck`)

### Phase 5 — MCP-Schicht

Ziel: ClaudeClockwork soll MCP **sprechen**, aber nicht davon abhängen.

Reihenfolge:

1. MCP-Client-Adapter
2. lokale STDIO-MCPs (`filesystem`, `git`, `build/test`)
3. Export ausgewählter nativer Skills als MCP-Tools
4. Resources für Referenz-Skills und Runbooks
5. Prompts/Tasks für größere Workflows

### Phase 6 — CI / Eval / Qualitätsgates

Ziel: das Skill-System dauerhaft kontrollierbar machen.

Pflichtgates:

- Manifest-Lint
- Import-Lint
- Permission-Lint
- Smoke-Run je Wrapped Skill
- Registry-Export-Diff
- Plugin-Index-Diff
- Capability-Map-Diff

## Empfohlene Prüf-Reihenfolge für die nächsten Sessions

1. `manifest_validate`, `legacy_skill_inventory`, `reference_skill_catalog`
2. `repo_validate`, `spec_validate`, `qa_gate`
3. `cleanup_*`, `repo_clean*`, `code_clean*`
4. `evidence_*`, `security_redactor`, `release_cut`
5. `determinism_*`, `contract_drift_*`, `schema_*`, `hardening_*`
6. `route_*`, `bandit_router_select`, `model_routing_*`
7. Plugin Runtime
8. MCP Runtime

## Nützliche Quellen für die Vollimplementierung

Offizielle Quellen, die für die nächsten Schritte besonders sinnvoll sind:

### Python Import / Plugin Discovery

- `importlib.import_module()` ist laut Python-Import-Referenz die empfohlene, einfachere API gegenüber `__import__()`: https://docs.python.org/3/reference/import.html
- `importlib.metadata` ist der eingebaute Zugriff auf installierte Paket-Metadaten und Entry Points: https://docs.python.org/3/library/importlib.metadata.html
- Der Python Packaging Guide beschreibt drei Standardwege für Plugin-Discovery: Naming Convention, Namespace Packages und Package Metadata: https://packaging.python.org/guides/creating-and-discovering-plugins/
- Für paketierte Plugins ist `pyproject.toml` der aktuelle Standardpfad: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/

### Manifest- und Schema-Validierung

- JSON Schema führt Draft **2020-12** als aktuelle Version: https://json-schema.org/specification
- Pydantic erzeugt JSON Schemas kompatibel zu **JSON Schema Draft 2020-12** und OpenAPI 3.1: https://docs.pydantic.dev/latest/concepts/json_schema/

### Hook-/Plugin-Orchestrierung

- `pluggy` bietet einen `PluginManager` mit Hook-Spezifikationen und registrierten Hook-Implementierungen: https://pluggy.readthedocs.io/en/latest/api_reference.html

### MCP

- Die MCP-Spezifikation trennt **Tools**, **Resources** und **Prompts** sauber: https://modelcontextprotocol.io/specification/2025-11-25
- Tool-Definitionen: https://modelcontextprotocol.io/specification/2025-06-18/server/tools
- Resource-Definitionen: https://modelcontextprotocol.io/specification/2025-06-18/server/resources
- Prompt-Definitionen: https://modelcontextprotocol.io/specification/2025-06-18/server/prompts

## Klare Empfehlung

Für ClaudeClockwork ist weiterhin **kein Big-Bang-Rewrite** sinnvoll.

Die beste Reihenfolge bleibt:

1. Manifest-System härten
2. Wrapper-Wellen kontrolliert ausbauen
3. wichtigste Meta-/QA-Skills nativ machen
4. Plugin-Runtime einziehen
5. MCP darüber setzen
6. harte CI-/Eval-Gates etablieren

Damit bleibt ClaudeClockwork lokal, kontrollierbar und evolvierbar.
