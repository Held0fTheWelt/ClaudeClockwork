# Broken Links Report — docs/README.md

_Last updated: 2026-03-02 (CCW-MVP04)_
_Checked by: CCW-MVP04 implementation audit_

## Status: CLEAN — no broken links found

All top-level links in `docs/README.md` were verified against the filesystem.

### Links checked

| Link text                              | Target path                                              | Status |
|----------------------------------------|----------------------------------------------------------|--------|
| Quickstart Tutorial                    | `docs/user/tutorials/01_quickstart.md`                   | OK     |
| User Guide                             | `docs/user/user_guide.md`                                | OK     |
| FAQ                                    | `docs/user/faq.md`                                       | OK     |
| Workflows Tutorial                     | `docs/user/tutorials/02_workflows.md`                    | OK     |
| Troubleshooting Tutorial               | `docs/user/tutorials/03_troubleshooting.md`              | OK     |
| Glossary                               | `docs/glossary.md`                                       | OK     |
| Architecture                           | `docs/tech/architecture.md`                              | OK     |
| CLI Reference                          | `docs/tech/api_or_cli.md`                                | OK     |
| Operations Guide                       | `docs/tech/operations.md`                                | OK     |
| System Map                             | `docs/diagrams/system_map.md`                            | OK     |
| C4 Context Diagram                     | `docs/diagrams/c4_context.mmd`                           | OK     |
| Security Guidelines                    | `docs/security/security_guidelines.md`                   | OK     |
| Threat Model                           | `docs/security/threat_model_light.md`                    | OK     |
| Release Notes                          | `docs/release/release_notes.md`                          | OK     |
| Changelog                              | `docs/release/changelog.md`                              | OK     |
| Documentation Suite Concept Pack       | `docs/concepts/project_documentation_suite/00_README.md` | OK     |
| Maintenance Schedule                   | `docs/concepts/project_documentation_suite/07_maintenance_schedule.md` | OK |
| reference_health.md                    | `docs/reference_health.md`                               | OK     |

### PDF export links

All HTML export files under `docs/_exports/pdf/` exist for the linked documents.
Note: `diagrams_c4_context_diagram.html` is present (export of `c4_context.mmd`).

### Notes

- `docs/README.md` line 92 references a skill runner invocation with a `/tmp/` path
  (`/tmp/pdf_export_req.json`) — this is a runtime example, not a link to check.
- No `docs/agents/README.md` exists — there are no broken links to that path from
  `docs/README.md` (that path is only referenced from clockwork docs, not project docs).

## Re-check command

```bash
python3 .claude/tools/skills/skill_runner.py --in /tmp/repo_validate_req.json --out /tmp/repo_validate_res.json
```

(Set `"skill": "repo_validate"` and `"check_markdown_links": true` in the request.)
