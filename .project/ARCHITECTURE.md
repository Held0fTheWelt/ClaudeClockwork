# ARCHITECTURE.md — Clockwork Rules System

> System design document for the Clockwork governance and tooling layer.
> Canonical reference for Architecture Agent decisions.
> Detailed design lives in `.claude/knowledge/architecture.md`.

---

## Overview

Clockwork is a meta-governance system for multi-agent Claude/Ollama orchestration.

- **System files:** `.claude/` — agents, governance, contracts, skills, tools, knowledge
- **Project files:** `.project/` — memory, docs, roadmap, quality tracking (this project)
- **Deployment:** when used on another project, `.project/` contents move to that project's root

## Key Design Principles

- Oodle-first (local LLM) — escalate to Claude only when needed
- Small-first model selection — escalate tier before switching providers
- Strict file ownership — no agent edits outside its domain
- Contracts over freitext — all inter-agent data uses typed JSON specs

## Current Architecture Notes

(empty — populate as decisions are made)
