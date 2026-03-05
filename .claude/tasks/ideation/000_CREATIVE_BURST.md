# Task: Creative Burst (cheap breadth, deterministic narrowing)

## Goal
Generate many short ideas cheaply, then narrow deterministically.

## Steps
1) Cheap LLM generates 20–50 one-line ideas (no essays).
2) Run skill `creativity_burst` with those ideas.
3) Convert top picks into an IdeaSetSpec (optional).

## Output
- clusters + top picks
- IdeaSetSpec (if requested)
