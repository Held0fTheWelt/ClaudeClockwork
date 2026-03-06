# Rubric: PDF Quality (DocForge)

This rubric is used by **Critic** and **DecideGap**.

## Scoring (0–100)

### 1) Coverage (0–25)
- Does the document fully cover the defined scope?
- Are assumptions and non-goals explicit?

### 2) Structure & Navigation (0–20)
- Clear structure, meaningful headings, table of contents (if >3 pages).
- Consistent terminology.

### 3) Clarity & Readability (0–20)
- Short paragraphs, clear sentences, active phrasing.
- Appropriate audience level (beginner vs. expert).

### 4) Correctness & Consistency (0–15)
- No internal contradictions.
- Paths/terms align with SSoT/Governance.

### 5) Visuals (0–15)
- At least 1 meaningful diagram per core topic.
- Diagrams are readable (font size, contrast, legends).

### 6) Actionability (0–5)
- Concrete next steps, examples, checklists, API usage.

## Quality Levels
- **90–100:** Release-ready (cosmetic changes only).
- **75–89:** Good, but 1–3 larger gaps.
- **55–74:** Usable, but several structural/content gaps.
- **<55:** Requires rebuild / scope clarification.

## Critic Output (Required Format)

- Score (0–100)
- Top 10 Fixes (prioritized)
- 1 "Most Leverage Improvement" (the single step with the highest impact)
- Diagram feedback (if relevant)


## Expectation Traps, Non-goals, Future Work (Required)

A truly good document makes **explicit** what many would immediately expect — but which is not (yet) present.

**Required sections (depending on document type):**
- **Limitations & Constraints (as of today)**
- **What it explicitly is NOT (Non-goals)**
- **What many would expect but is not (yet) implemented (Expectation Traps)**
- **What is conceivable (Future Work / Possibilities) but currently not part of the system**

**Scoring (0–5):**
- 0: missing entirely
- 3: present, but generic / without concrete examples
- 5: concrete, testable, with clear statements + impacts (e.g. security/performance/scope)



## Limitation Harvest Coverage (0–5)

Assesses whether the document covers the deterministically harvested points (expected-but-missing, non-goals, future work).

- 0: harvest ignored
- 3: partially incorporated, without impacts/examples
- 5: complete and concrete, including impacts + clear boundaries
