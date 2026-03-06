STRICT MODE

Project language policy:
- ClaudeClockwork is an English-language project.
- Treat English as the canonical language for code, manifests, rulesets, prompts, docs, reports, roadmaps, test descriptions, migration notes, naming, and architectural terminology.
- Do not silently switch project-facing artifacts back to German or mix languages inside technical deliverables.
- If legacy content exists in another language, identify it, assess whether it is still needed, and either migrate it to English or explicitly mark it as legacy.
- Preserve English as a consistency rule across the repository.

Execution policy:
- Treat every unclear overlap in responsibility as a bug, design flaw, or migration gap.
- Treat every document that implies a higher implementation state than the code actually provides as a consistency failure.
- Treat every bridge, adapter, wrapper, registry rule, manifest contract, plugin stub, and MCP preparation as testable and verifiable.
- Explicitly distinguish between:
  - implemented
  - operational
  - partially integrated
  - scaffolded
  - planned only
- Do not soften findings. Name half-finished systems as half-finished.
- Do not preserve ambiguity for convenience.

Drift policy:
- Detect architectural drift across code, manifests, registries, runtime behavior, documentation, roadmaps, tests, and migration files.
- Treat path mismatches, import mismatches, stale registries, duplicate systems, shadow implementations, dead compatibility layers, and outdated assumptions as first-class drift findings.
- Treat inconsistent naming, mixed roots, conflicting conventions, and undocumented transitional structures as issues that must be resolved or explicitly documented.

Repair policy:
- Fix all safe and local inconsistencies directly.
- If multiple competing mechanisms exist for the same purpose, consolidate them where possible.
- If consolidation is not yet safe, clearly separate responsibilities and document the reason.
- Do not remove legacy mechanisms blindly; inspect them for still-useful behavior, migration value, or missing capabilities not yet covered by the new system.
- Repurpose legacy components when they add value and are still structurally sound.

Validation policy:
- Add or update tests for every critical drift point you touch.
- Validate runtime paths, manifest loading, registry behavior, bridge behavior, plugin boundaries, and status claims in documentation.
- Verify that actual execution paths match declared architecture.
- Verify that English-language policy is still upheld in the active ruleset and project-facing artifacts.

Reporting policy:
- Report findings with explicit severity:
  - critical
  - functional
  - structural
  - documentary
  - open technical debt
- At the end, provide:
  1. current architecture snapshot
  2. drift findings
  3. changes made
  4. tests and validation results
  5. remaining risks and ambiguities
  6. prioritized next steps

Behavioral constraint:
- Do not produce cosmetic cleanup disguised as architectural work.
- Do not claim completion where only scaffolding exists.
- Do not treat “prepared”, “planned”, or “documented” as equivalent to “working”.
- Keep the repository aligned to a single coherent architecture and keep the project language English.

The Zen of CodeClockwork:
- Beautiful is better than ugly.
- Explicit is better than implicit.
- Simple is better than complex.
- Complex is better than complicated.
- Flat is better than nested.
- Sparse is better than dense.
- Readability counts.
- Special cases aren't special enough to break the rules.
- Although practicality beats purity.
- Errors should never pass silently.
- Unless explicitly silenced.
- In the face of ambiguity, refuse the temptation to guess.
- There should be one-- and preferably only one --obvious way to do it.
- Now is better than never, unless you should really make a Task in the Roadmap.
- Although never is often better than *right* now.
- If the implementation is hard to explain, it's a bad idea.
- If the implementation is easy to explain, it may be a good idea.