# Rule Discovery & Maintenance

## Core Principle

The rule base is never complete. With every work step — especially during task creation and reviews — implicit, not yet documented rules are actively identified and sorted into the structure.

## When Is a New Rule Recognized?

A rule is considered recognizable when at least one of the following applies:

- **Repetition** — A pattern occurs consistently in multiple modules or functions
- **Convention** — Code follows a uniform structure that is not coincidental (naming, order, dependencies)
- **Constraint** — A limitation of the language, framework, or architecture enforces a specific approach
- **Error Source** — An error occurs whose cause can be traced to an undocumented rule
- **Deviation** — Code deviates from documented rules and the deviation proves correct → adjust existing rule
- **Architecture Gap** — During work, it becomes visible that the architecture implies a rule that is not yet documented

## Process on Discovery

1. **Identify** — Recognize pattern/constraint/convention as not yet documented
2. **Classify** — Check which `.claude/` document the rule thematically belongs to:
   - Python patterns → `.claude/python/patterns.md`
   - Architecture rules → `.claude/python/architecture.md`
   - Governance/process → `.claude/governance/`
   - Cross-project insights → `MEMORY.md`
3. **Insert or Create** — Insert into existing document OR create new `.claude/` document
4. **Update `.claude/SYSTEM.md`** — For new document: extend quick links + subfolder reference
5. **Inform User** — Briefly communicate which rule was recognized and where it was entered
6. **Document in Plan/Review** — Note under "Newly Discovered Rules"

## Quality Criteria for New Rules

- **Concrete** — No vague statements; verifiable rules with examples or code snippets
- **Substantiated** — Reference to specific code, error, or architecture property that justifies the rule
- **Sorted** — Thematically in the correct document, not as a loose appendix
- **Contradiction-Free** — Cross-check against existing rules; on contradiction, update older rule or ask user

## What Is NOT Included

- One-time, project-specific workarounds without repetition potential
- Unverified assumptions about patterns based on only a single file
- Information already in `.claude/` or `MEMORY.md`

## When Rule Discovery Is Mandatory

- For every Task: Workflow (plan creation)
- For every Review: Workflow
- For every Document: Workflow
- For every Implement: Workflow
