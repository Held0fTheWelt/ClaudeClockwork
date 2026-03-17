You are Claude running inside the ClaudeClockwork repository.

Execution mode for this task is mandatory:
PURE OLLAMA AGENT EXECUTION ONLY.

This is a binding execution contract, not a preference.

You must use only pure Ollama agents through the repository’s Ollama/agent skill tooling to perform the implementation work.

You must NOT:
- write code yourself
- edit files yourself
- implement fixes yourself
- use Claude agents
- use mixed Claude + Ollama execution
- silently compensate for Ollama by doing the work yourself
- fall back to manual Claude implementation
- return only a plan unless the repo state makes execution impossible

Your role in this task is limited to:
- inspect enough to route the task correctly
- dispatch pure Ollama agents
- ensure they perform the implementation
- collect outputs/results
- run validations/gates if allowed through the same operational path
- summarize the completed work

If pure Ollama agent execution is unavailable, blocked, misconfigured, or insufficiently wired in this repo, you must STOP and report that as the blocker.
Do not bypass the mode.
Do not compensate.
Do not do the work yourself.

Project language rule:
All project-facing changes must remain in English.

Mission:
Eliminate the current high-risk drift between packaging, path semantics, runtime expectations, model policy, and skill registry behavior.

This is not a documentation-only task.
The repair must be implemented in the repo by pure Ollama agents, docs must be updated, regression tests must be added or updated, and relevant gates must be run.

Primary goal:
Create a single canonical system contract for package/path/runtime semantics and make runtime, checks, and docs derive from it instead of re-declaring their own truth.

Critical context:
The repo currently shows dangerous drift in these areas:
1. VERSION source-of-truth drift
2. repo-root vs .claude vs .claude-only packaging/path drift
3. runtime artifact path drift (.report, .clockwork_runtime, etc.)
4. model policy split across multiple docs/configs
5. skill registry drift versus actual implementations
6. workflow/governance docs mixing normative and explanatory roles

The task is to fix the architecture, not just patch symptoms.

==================================================
MANDATORY EXECUTION RULES
==================================================

1. Pure Ollama only
All implementation work must be performed by pure Ollama agents using the repo’s agent/skill mechanism for Ollama execution.
If something is not working correctly on doing this, fix it. Don't write Scripts, use Skills only.
If a skill is missing, invent one with your claude agents, that completely integrates to your skill system.
If runtime fails, try smaller context more frequently

2. Claude is not an implementer here nor are Claude Agents (Haiki, Sonnet, Opus)
You may coordinate, inspect, route, validate, and summarize.
You may not personally perform code changes.


3. No silent fallback
If Ollama agent execution fails, is unavailable, or is blocked by repo/runtime limitations, report that explicitly and stop.
Do not continue with Claude implementation.

4. No mixed execution
Do not split work so that Ollama explores and Claude implements.
Do not patch leftovers yourself.
Do not “help” with manual edits.

5. Use the repo’s existing Ollama capability
The repository already contains skill/tooling intended to use Ollama agents.
Use that path rather than inventing a different execution path.

6. Evidence over intention
Do not claim completion unless the Ollama agents have actually changed files, updated docs, updated tests, and produced verifiable results.

==================================================
HARD REQUIREMENTS
==================================================

1. Canonical system contract
Create one machine-readable canonical contract file, for example:
- .claude/system_contract.yaml

It must define at minimum:
- canonical VERSION location
- supported package modes
- required vs optional paths per package mode
- runtime artifact directories
- whether missing runtime dirs may be auto-created
- canonical model runtime config location
- canonical skill registry output location

2. Central contract loader
Implement a reusable Python loader/helper for the contract.
Boot checks, QA gates, and any relevant runtime/tooling code must consume this loader instead of hardcoding their own assumptions.

3. Canonical VERSION truth
Unify VERSION handling.
Choose exactly one canonical VERSION source and migrate checks to it.
Recommended target:
- .claude/VERSION is canonical

If root VERSION must temporarily exist for compatibility, it must be clearly treated as derived/compat only, not equal source-of-truth.

4. Package mode support
Explicitly support and validate:
- repo mode
- .claude-only mode

Checks must not fail incorrectly just because a portable .claude-only package lacks runtime-generated directories.

5. Runtime directory semantics
Fix the treatment of runtime output paths such as:
- .report
- .clockwork_runtime
and any equivalent artifact/evidence directories

These must be classified correctly as:
- required distribution content
- optional runtime content
- auto-creatable runtime content

6. Model policy deduplication
Reduce model-routing truth to one canonical runtime config.
The executor/routing logic must read one canonical machine-readable config, not multiple competing sources.

Human docs may explain the behavior, but must not define separate operational truth.

7. Skill registry integrity
Eliminate registry drift.
Either:
- generate the registry from actual skill metadata, or
- add a hard validation step that proves the registry matches actual implementations

Preferred:
- generated registry + test that diff is clean

8. Governance doc role separation
Separate normative vs explanatory docs.
Normative governance docs must be clearly identified.
Explanatory docs must declare that they derive from the normative source and are not independent authorities.

9. Drift regression tests
Add tests that permanently guard against this class of drift.

10. Remove or replace weaker conflicting logic
Do not leave behind old code paths that still enforce contradictory assumptions.

==================================================
IMPLEMENTATION EXPECTATIONS
==================================================

You must inspect the repo and adapt names/paths to the actual codebase, but the resulting architecture must include these concepts.

Recommended implementation shape:

A. Contract
Add:
- .claude/system_contract.yaml

B. Shared loader
Add something like:
- .claude/tools/lib/system_contract.py
or equivalent shared location already used by the repo

C. Refactor checks
Update at minimum:
- boot check tooling
- QA gate tooling
- any package validation code
- any runtime path creation/check logic

D. Model config consolidation
Converge the operational truth into one canonical runtime config file.
Update the executor/router/model selection code to read only that source.

E. Registry generation/validation
Introduce:
- structured skill metadata source
- registry generation tool or validator
- generated registry artifact if appropriate

F. Documentation cleanup
Update the relevant docs so they clearly state:
- what is canonical
- what is derived
- how repo mode differs from .claude-only mode
- where VERSION lives
- where runtime artifacts belong
- which model config is authoritative
- whether the skill registry is generated or validated

==================================================
TESTS / GATES TO ADD
==================================================

Add or update tests for at least the following:

1. Contract consistency
- no critical check script hardcodes conflicting VERSION/path assumptions
- core tools load canonical contract successfully

2. Package mode validation
- repo mode passes with valid structure
- .claude-only mode passes with valid portable structure
- intentionally broken package fails correctly

3. VERSION truth
- only canonical VERSION source is required
- compat shim behavior is tested if present

4. Runtime directories
- runtime dirs are optional for package validation if contract says so
- runtime dirs are created when runtime policy allows it

5. Model config authority
- executor/router uses only canonical model runtime config
- conflicting legacy config does not silently override canonical behavior

6. Skill registry integrity
- generated registry or registry validation stays in sync with actual skill set

7. Doc role hygiene
- if you add metadata/frontmatter for doc role classification, test or lint it

==================================================
DELIVERABLES
==================================================

You must:
1. implement the repair through pure Ollama agents
2. update docs
3. add/update tests
4. run the relevant tests/gates
5. report the changed files
6. report any follow-up debt that could not be resolved in this pass

==================================================
WORKFLOW RULES
==================================================

- Do not ask for permission to proceed.
- Do not stop after analysis unless pure Ollama execution is impossible.
- Do not produce only a recommended plan.
- Make best-effort repo-appropriate decisions where naming differs.
- Prefer minimal, strong architecture over scattered patches.
- Preserve existing behavior where not in conflict with the new canonical contract.
- Keep project-facing language in English.
- Avoid introducing duplicate sources of truth while fixing duplicate sources of truth.
- Do not let Claude perform implementation work under any justification.

==================================================
PREFERRED EXECUTION ORDER
==================================================

Execute in this order, using pure Ollama agents:

Wave 1:
- introduce canonical system contract
- add shared loader
- unify VERSION truth
- refactor boot/package/QA checks to use contract

Wave 2:
- fix runtime artifact directory semantics
- support repo mode and .claude-only mode correctly
- remove contradictory path assumptions

Wave 3:
- consolidate model runtime policy into one operational config
- refactor executor/router/model selection to use it

Wave 4:
- fix skill registry drift via generation or hard validation

Wave 5:
- mark governance/docs as normative vs explanatory
- clean conflicting docs

Wave 6:
- add regression tests
- run gates
- summarize residual debt

==================================================
FINAL RESPONSE FORMAT
==================================================

Your final response must include:

1. Execution mode confirmation
- confirm that pure Ollama agents performed the implementation
- state whether any blocker prevented full pure Ollama execution

2. Summary
- what was repaired

3. Canonical decisions made
- canonical VERSION location
- canonical package modes
- canonical runtime dirs semantics
- canonical model runtime config
- registry strategy

4. Changed files
- grouped by area

5. Tests and gates run
- explicit results

6. Remaining debt
- only real unresolved items

Do not claim completion unless the implementation, docs, and tests were actually updated by pure Ollama agents.
If pure Ollama execution was not possible, do not pretend partial Claude work satisfies this task.