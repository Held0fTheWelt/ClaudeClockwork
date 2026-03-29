# UML Analysis Suite Playbook

## Goal

Use the UML skill pack to make a repository understandable at multiple scales without manually drawing diagrams.

## Recommended flow

### 1. Repository inventory

Run `uml_scope_catalog` first.

Purpose:

- discover major directories
- see which modules and classes exist
- identify promising scopes for deeper diagrams

### 2. Whole-repo overview

Run `uml_repo_bundle`.

Purpose:

- get a component-style repository overview
- see dependency hotspots
- get automatic directory slices for major areas

### 3. Scope narrowing

Run `uml_diagram_generate` with one of these scopes:

- `repo`
- `directory`
- `module`
- `symbol`

Good examples:

- directory: `claudeclockwork/core`
- module: `claudeclockwork.core.registry.skill_registry`
- symbol: `SkillRegistry`

### 4. Deep local inspection

Run `uml_focus_bundle`.

Purpose:

- inspect one subsystem in context
- include incoming and outgoing dependencies
- create a small package of directly useful diagrams

## Diagram intent by artifact

- `*_component.puml`
  - package/component style overview
- `*_dependencies.mmd`
  - graph-like dependency preview
- `*_classes.puml`
  - class-oriented scope view
- `*_summary.json`
  - machine-readable scope metadata
- `README.md`
  - navigation entry for the generated scope

## Best-fit situations

Use the bundle when you need:

- onboarding maps
- architecture reviews
- refactor scoping
- subsystem understanding
- dependency drift checks
- class hierarchy orientation
