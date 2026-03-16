# Regression Coverage Report

**Date:** 2026-03-16
**Status:** All regression tests passing

## Objective

Prove that the four forge capabilities (`code.plan`, `code.forge`, `code.review`, `code.validate`) are now **first-class LocalAI runtime capabilities** and are no longer rejected as `unknown_capability`.

## Test Coverage

### 1. Runtime Integration Tests (`tests/test_runtime_forge_integration.py`)

**Goal:** Verify `run_local_capability()` can dispatch all four capabilities.

| Test | Capability | Purpose |
|---|---|---|
| `test_code_plan_is_available` | code.plan | Regression: NOT unknown_capability |
| `test_code_plan_returns_contract_shaped_result` | code.plan | Returns proper contract structure |
| `test_code_plan_all_archetypes` | code.plan | All 5 archetypes supported |
| `test_code_forge_is_available` | code.forge | Regression: NOT unknown_capability |
| `test_code_forge_returns_contract_shaped_result` | code.forge | Returns proper contract structure |
| `test_code_review_is_available` | code.review | Regression: NOT unknown_capability |
| `test_code_review_returns_contract_shaped_result` | code.review | Returns proper contract structure |
| `test_code_validate_is_available` | code.validate | Regression: NOT unknown_capability |
| `test_code_validate_returns_contract_shaped_result` | code.validate | Returns proper contract structure |
| `test_all_code_capabilities_available` | All 4 | All available in runtime |
| `test_run_local_capability_no_longer_rejects_forge_capabilities` | All 4 | NOT rejected as unknown |

**Status:** ✅ All 11 tests passing

### 2. Composed Skill Integration Tests (`tests/test_skill_forge_run_integration.py`)

**Goal:** Verify `skill_forge_run()` orchestrates stages correctly.

| Test | Coverage |
|---|---|
| `test_full_mode_executes_all_stages` | Full pipeline execution |
| `test_plan_only_mode` | Partial mode: plan only |
| `test_through_forge_mode` | Partial mode: plan + forge |
| `test_through_review_mode_requires_prior_results` | Precondition validation |
| `test_validate_only_mode_requires_prior_results` | Precondition validation |
| `test_invalid_archetype_rejected` | Input validation |
| `test_invalid_mode_rejected` | Input validation |
| `test_missing_purpose_rejected` | Input validation |
| `test_all_valid_archetypes_accepted` | All archetypes work |
| `test_execution_log_is_structured` | Log structure |
| `test_execution_log_includes_input_resolution` | Log events |
| `test_execution_log_includes_validation` | Log events |
| `test_result_includes_run_id` | Result structure |
| `test_result_includes_resolved_inputs` | Result structure |
| `test_result_includes_temp_workspace` | Result structure |
| `test_result_includes_final_status` | Result structure |

**Status:** ✅ All 16 tests passing

## Regression Proof

### Before (Prior to Task 1)

Calling `run_local_capability("code.plan", {...})` would:
- Return `{"status": "unknown_capability", "error": "Unknown capability: code.plan"}`
- OR: Fail completely with AttributeError/KeyError

### After (Task 1-8 Complete)

Calling `run_local_capability("code.plan", {...})` now:
- ✅ Returns contract-shaped dict with `"status": "ok"` or proper error
- ✅ Sets `"capability": "code.plan"` correctly
- ✅ Includes `"inputs"`, `"outputs"`, `"metrics"`, `"errors"` keys
- ✅ Same for code.forge, code.review, code.validate

### Evidence

```python
# Regression test: Negative assertion
result = run_local_capability("code.plan", {...})
assert result["status"] != "unknown_capability"  # ✅ PASSING
assert result["capability"] == "code.plan"       # ✅ PASSING
```

## Test Suite

```bash
# Run all regression tests
pytest tests/test_runtime_forge_integration.py::TestRegressionAllCapabilitiesAvailable -v

# Run full integration suite
pytest tests/test_runtime_forge_integration.py tests/test_skill_forge_run_integration.py -v
```

## Coverage Summary

| Aspect | Tests | Status |
|---|---|---|
| Runtime dispatch | 11 | ✅ All passing |
| Composed skill | 16 | ✅ All passing |
| **Total** | **27** | ✅ **All passing** |

---

**Conclusion:** The skill-forge pipeline is no longer implemented but inaccessible. It is now a **first-class LocalAI runtime capability** with full regression coverage proving no backward-incompatible changes.
