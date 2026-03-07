# Clockwork MVP Chain — Legacy Index (v17 and earlier)

This file is an index of the historical Clockwork MVP chain covering CCW-MVP01 through CCW-MVP33, as tracked during Clockwork development up to and including v17.x.

Full chain (canonical, read-only): `.claude-development/Clockwork_MVP_Chain.md`

---

## Summary Table

| # | MVP ID | Name | Status | Date / Milestone | Phase Reference |
|---|--------|------|--------|-------------------|-----------------|
| 1 | CCW-MVP01 | Repo & Runtime Scaffolding (Clockwork Core) | done | 2026-03-02 | Phase 0 |
| 2 | CCW-MVP02 | Deterministic Skill Framework v1 | done | 2026-03-02 | Phase 0 |
| 3 | CCW-MVP03 | Agent Layer v1 (Prompts + Roles + Routing Policy Stub) | done | 2026-03-02 | Phase 0 |
| 4 | CCW-MVP04 | Documentation Ops v1 (Write/Review/Index) | done | 2026-03-02 | Phase 0 |
| 5 | CCW-MVP05 | Governance & Policy Enforcement v1 | done | 2026-03-02 | Phase 0 |
| 6 | CCW-MVP06 | Reports & Telemetry Layout v1 | done | 2026-03-02 | Phase 0 |
| 7 | CCW-MVP07 | Milestone System v1 (.claude-development/ scaffolding) | done | 2026-03-02 | Phase 0 |
| 8 | CCW-MVP08 | Parity Scan Skill + MVP Pre-Planning (Clockwork-only) | done | 2026-03-02 | Phase 0 |
| 9 | CCW-MVP09 | Parity Follow-up M1: Routing & Model Selection (Design MVP) | done | 2026-03-02 | Phase 1 |
| 10 | CCW-MVP10 | QA Gates & CI v1 | done | 2026-03-02 | Phase 6 |
| 11 | CCW-MVP11 | Eval Harness / Golden Tests v1 | done | 2026-03-02 | Phase 6 |
| 12 | CCW-MVP12 | Telemetry & Feedback Loop v1 | done | 2026-03-02 | Phase 3 |
| 13 | CCW-MVP13 | Cleaning Suite Completion | done | 2026-03-02 | Phase 8 |
| 14 | CCW-MVP14 | Archive & Prompt Evolution Completion | done | 2026-03-02 | Phase 8 |
| 15 | CCW-MVP15 | PDF Quality Skill (DocForge PDF Pipeline) | done | 2026-03-02 | Phase 3 |
| 16 | CCW-MVP16 | Parity Scan Planner Implementation + Registry Integrity | done | 2026-03-02 | Phase 1 |
| 17 | CCW-MVP17 | Clockwork Invariants + CI Gate + Integration Tests | done | 2026-03-02 | Phase 6 / Phase 9 |
| 18 | CCW-MVP18 | Adaptive Routing & Telemetry Feedback Loop | done | 2026-03-02 | Phase 3 |
| 19 | CCW-MVP19 | Meta-Tooling: QA Gate Extension + Addon CI + skill_runner Hygiene | done | 2026-03-02 | Phase 1 / Phase 6 |
| 20 | CCW-MVP20 | "Create MVP" Skill (Autonomous MVP Generation) | done | 2026-03-02 | Phase 3 |
| 21 | CCW-MVP21 | Clockwork Versioning (Version Bumps + Changelog + Release Tags) | done | 2026-03-02 | Phase 2 |
| 22 | CCW-MVP22 | Clockwork Invariant Cleanup | done | M2 Week 1 (2026-03-02) | Phase 8 |
| 23 | CCW-MVP22-D | Runtime Critics Architecture (Design) | done | M2 Week 2 design sprint | Phase 3 |
| 24 | CCW-MVP23-D | Capability Policy Design (Design) | done | M2 Week 2 design sprint | Phase 4 |
| 25 | CCW-MVP24-D | Eval Harness Completion Design (Design) | done | M2 Week 2 design sprint | Phase 6 |
| 26 | CCW-MVP23 | Runtime Critics v1 (Drift + Regression) | planned | M2 Week 3 | — |
| 27 | CCW-MVP24 | Capability Policy Enforcement | planned | M2 Week 3 | — |
| 28 | CCW-MVP25 | Eval Harness Completion | planned | M2 Week 3 | — |
| 29 | CCW-MVP26 | Security Hardening v1 | planned | M2 Week 4 | — |
| 30 | CCW-MVP30 | CBL Rung Unlock Ceremonies | planned | M2 Week 4 | — |
| 31 | CCW-MVP25-D | MAPE-K Learning Loop Design | planned | M2 Week 5–6 | — |
| 32 | CCW-MVP26-D | Plugin Runtime Design | planned | M2 Week 5–6 | Phase 4 |
| 33 | CCW-MVP27 | MAPE-K Learning Loop v1 | planned | M2 Week 5–6 | — |
| 34 | CCW-MVP28 | Full Critics Suite (10 new critics) | planned | M2 Week 5–6 | — |
| 35 | CCW-MVP29 | Plugin Runtime v1 | planned | M2 Week 7–8 | Phase 4 |
| 36 | CCW-MVP33 | Shadow-Operator Mode v1 | planned | M2 Week 7–8 | — |
| 37 | CCW-MVP27-D | Knowledge Graph Design | planned | M2 Week 9–12 | — |
| 38 | CCW-MVP28-D | Agent Genome & Evolution Design | planned | M2 Week 9–12 | — |
| 39 | CCW-MVP31 | Knowledge Graph v1 (SQLite) | planned | M2 Week 9–12 | — |
| 40 | CCW-MVP32 | Agent Genome & Evolution v1 | planned | M2 Week 9–12 | — |

---

## Cross-Reference: Legacy Chain Items → v18 Phases

The v18 roadmap phases (`roadmaps/Roadmap_ClockworkV18.md`) implement work originally planned in the legacy chain. The mapping below is approximate — v18 phases address the same problem areas, often consolidating multiple chain items.

| v18 Phase | MVP File | Legacy Chain Items Addressed |
|-----------|----------|------------------------------|
| Phase 0 — Foundation & Cleanup | `mvps/MVP_Phase0_FoundationCleanup.md` | CCW-MVP01 through CCW-MVP08 (scaffolding, agents, governance, skills framework) |
| Phase 1 — Manifest Hardening | `mvps/MVP_Phase1_ManifestHardening.md` | CCW-MVP09, CCW-MVP16, CCW-MVP19 (routing design, registry integrity, QA gate) |
| Phase 2 — Wrapper Wave 3 | `mvps/MVP_Phase2_WrapperWave3.md` | CCW-MVP21 (versioning, skill extension) |
| Phase 3 — Native Core Services | `mvps/MVP_Phase3_NativeCoreServices.md` | CCW-MVP12, CCW-MVP15, CCW-MVP18, CCW-MVP20, CCW-MVP22-D (telemetry, PDF, routing, create MVP, critics design) |
| Phase 4 — Plugin Runtime | `mvps/MVP_Phase4_PluginRuntime.md` | CCW-MVP23-D, CCW-MVP26-D, CCW-MVP29 (capability policy design, plugin runtime design and v1) |
| Phase 5 — MCP Layer | `mvps/MVP_Phase5_MCPLayer.md` | (new work, no direct legacy chain equivalent) |
| Phase 6 — CI / Eval / Quality Gates | `mvps/MVP_Phase6_CIEvalGates.md` | CCW-MVP10, CCW-MVP11, CCW-MVP17, CCW-MVP19, CCW-MVP24-D (QA gates, eval harness, invariants, CI) |
| Phase 7 — Wrapper Wave 4 | `mvps/MVP_Phase7_WrapperWave4.md` | (extended from Phase 2 wave) |
| Phase 8 — Code & Governance Hygiene | `mvps/MVP_Phase8_CodeHygiene.md` | CCW-MVP13, CCW-MVP14, CCW-MVP22 (cleaning suite, archive, invariant cleanup) |
| Phase 9 — Test Hardening | `mvps/MVP_Phase9_TestHardening.md` | CCW-MVP17 (integration tests) |
| Phase 10 — Compaction & Pluggability | `mvps/MVP_Phase10_Compaction.md` | (structural compaction, new work) |

---

## Notes

- "planned" status items in the legacy chain were superseded by the v18 phase structure. They were not abandoned — the underlying goals were re-scoped into v18 phases.
- Items with no "Phase Reference" are either subsumed into v18 phases not yet started (Phases 12–15) or are candidates for future planning.
- The legacy chain does not use B-NNN notation for top-level MVPs; B-NNN references appear as internal backlog items within individual MVP sections in the full chain file.

---

> Full chain: `.claude-development/Clockwork_MVP_Chain.md` (read-only historical reference)
