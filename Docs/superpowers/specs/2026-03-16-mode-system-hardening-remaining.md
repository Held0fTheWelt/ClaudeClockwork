# Mode System Hardening - Remaining Tasks

## Overview

The mode system foundation has been implemented with fail-closed validation, hard gates at execution, and audit tooling. This spec covers four remaining hardening tasks to complete the integration.

## Current State

- ✅ Mode manager with persistent state (3 modes: default, adaptive, claude-min)
- ✅ Mode guard with hard-gates (ModeViolationError exceptions)
- ✅ Mode validator with fail-closed metadata checks
- ✅ Mode audit tool with 4 validation checks
- ✅ Executor with 6 hard-gates before skill execution
- ✅ CLI commands for mode management
- ✅ 44 tests passing (units + hardening + bypass prevention)

**Status:** Hardened mode system foundation complete. Remaining work: planner integration, manifest backfill, router hardening, documentation.

## Problem Statement

1. **Planner doesn't filter skills by mode** - Routing logic may suggest skills incompatible with active mode
2. **Skills lack mode_requirements metadata** - Existing manifests don't declare agent_type, mode constraints
3. **Router may bypass mode checks** - If router exists, it needs mode awareness
4. **Documentation incomplete** - No examples of mode_requirements in manifest schema

## Scope & Success Criteria

| Task | Success Criterion |
|------|------------------|
| **Task 1: Mode-Aware Planner** | Planner filters skills by mode before routing; tests verify incompatible skills excluded |
| **Task 2: Manifest Backfill** | All existing skill manifests have mode_requirements with agent_type and requires_mode |
| **Task 3: Router Hardening** | If router exists, it validates mode constraints; tests verify mode violations caught |
| **Task 4: Documentation** | Schema docs show mode_requirements examples; CLAUDE.md updated with mode requirements |

## Architecture

- **Planner filter** (new): Adds mode-awareness to skill filtering logic
- **Manifest validator** (existing): `ModeMetadataValidator` already fails closed; task is backfilling manifests
- **Router integration** (conditional): Only if router exists; add mode checks mirroring executor gates
- **Docs** (new): Examples and guidance in manifest schema documentation

## Implementation Order

1. **Task 1** - Mode-aware planner (independent, unblocks testing)
2. **Task 2** - Manifest backfill (independent; can be done in parallel or after planner)
3. **Task 3** - Router hardening (conditional on router existence; independent)
4. **Task 4** - Documentation (can be done in parallel; depends on tasks 1-3 for examples)

## Acceptance Criteria

- All tasks have TDD-based tests (write failing test → implement → pass)
- No changes to mode_manager, mode_guard, mode_validator, mode_audit, executor (already hardened)
- All tests pass: `pytest tests/test_mode_system.py -v`
- Code follows existing patterns in codebase
- Commits are atomic and focused per task
