# Traceability

| Claim / diagram element | Code | Test |
|---|---|---|
| MCP server exposes 8 tools | `clockwork/server.py` | `tests/clockwork/test_server.py::test_server_exposes_all_tools` |
| Bundle builders write catalog/repo/focus/scope/review/guide outputs | `clockwork/tools/bundles.py` | `tests/clockwork/test_bundles.py` |
| Gate detects uncataloged ADRs, missing mermaid, broken links, missing TRACEABILITY, missing uml-package | `clockwork/tools/gates.py` | `tests/clockwork/test_gates.py` |
| Scan/render core (modules, classes, deps, PlantUML/Mermaid) | `clockwork/tools/uml_shared.py` | `tests/clockwork/test_uml_shared.py` |
| Review context + static site | `clockwork/tools/uml_review_shared.py` | `tests/clockwork/test_review_shared.py` |
| Repo-level gate green on this repository | `tests/gates/test_architecture_documentation_gate.py` | (self) |
