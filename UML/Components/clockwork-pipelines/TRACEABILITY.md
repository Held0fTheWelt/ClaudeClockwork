# Traceability

| Claim / diagram element | Code | Test |
|---|---|---|
| Config defaults + YAML overrides | `clockwork/pipelines/runtime.py` | `tests/clockwork/test_pipelines_runtime.py::test_yaml_overrides` |
| Forbidden-model hard fail | `clockwork/pipelines/runtime.py` | `tests/clockwork/test_pipelines_runtime.py::test_forbidden_model_hard_fails` |
| 404 fallback to phi4 | `clockwork/pipelines/runtime.py` | `tests/clockwork/test_pipelines_runtime.py::test_generate_falls_back_on_404` |
| Three-step graph order (draft->review->refine) | `clockwork/pipelines/draft_review_refine.py` | `tests/clockwork/test_pipelines_graph.py::test_pipeline_runs_three_steps_in_order` |
| Degradation instead of FREEZE | `briefs.py`, `draft_review_refine.py`, `server.py` | `test_pipeline_degrades_without_backend`, `test_local_tools_degrade_without_backend` |
| Live roundtrip (optional) | `clockwork/pipelines/runtime.py` | `tests/clockwork/test_integration_local.py` |
