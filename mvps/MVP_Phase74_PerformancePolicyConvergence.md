# MVP Phase 74 — Performance Policy Convergence (Stop “Write Back to .report”)

**Goal:** Make `.claude-performance/`, `.report/`, and `.clockwork_runtime/` tell one consistent story. Prevent documents or tools from instructing runtime outputs to be written into `.report/*`.

**Observed (repo scan 2026-03-08):**
- `.claude-performance/README.md` implies human summaries go to `.report/performance/`, but `.report/` is curated-only and should not receive runtime-derived files automatically.

---

## Definition of Done

- [ ] `.claude-performance/README.md` aligns with `Docs/report_vs_runtime_policy.md`
- [ ] No docs recommend writing runtime/perf outputs into `.report/*`
- [ ] If curated perf summaries exist, they are:
  - explicitly generated, redacted, and stable (manual/explicit step)
- [ ] A doc-consistency gate blocks conflicting instructions
- [ ] All existing tests pass

---

## P74.1 — Rewrite Performance README + Policy Alignment

**Files:**
- `.claude-performance/README.md`
- `Docs/report_vs_runtime_policy.md`
- `Docs/drift_register.md`

**Change:**
- Declare:
  - raw perf logs → runtime root
  - curated summaries → `.report/` ONLY via explicit exporter, and only redacted

**Acceptance:**
- Docs no longer contain conflicting “write into .report/performance” instruction.

---

## P74.2 — Add Gate: Doc Policy Consistency

**Files:**
- `claudeclockwork/core/gates/doc_policy_consistency_gate.py` (new)
- `tests/test_doc_policy_consistency_gate.py`

**Change:**
- Scan a curated set of policy docs for contradictory rules:
  - e.g., `.report` curated-only vs “write runtime outputs there”
- Fail with file+line.

**Acceptance:**
- A conflicting phrase triggers deterministic failure.

---

## Drift Prevention Instruction
This phase must update the drift register entry for “report/runtime confusion” with:
- the canonical rule,
- the enforcing gate,
- and the remediation steps.

---
