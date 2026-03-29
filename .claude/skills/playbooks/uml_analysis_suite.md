# UML Analysis Suite Playbook

Use this playbook when a repository needs both scope-level UML outputs and a navigable review experience.

## Recommended flow

1. Run `uml_scope_catalog` to inventory directories, modules, and symbols.
2. Run `uml_repo_bundle` for the broad structural overview.
3. Run `uml_diagram_generate` or `uml_focus_bundle` for specific slices that need diagram artifacts.
4. Run `uml_review_context_build` to assemble context cards and tooltip payloads.
5. Run `repo_how_it_works_build` to generate technical and functional guide pages.
6. Run `uml_review_site_build` to generate the static UML review website with integrated guides.
7. Use `uml_review_bundle` or `uml_review_knowledge_bundle` when you want steps 4 to 6 in one pass.

## When to prefer the review website

Use the review explorer when you want to:

- browse modules like documentation pages
- move from directories to modules to symbols
- inspect local context without opening source files immediately
- surface tooltip-level context while navigating links
- share a static, local artifact for architecture review

## Scope strategy

- repo scope: portfolio or architecture overview
- directory scope: subsystem or bounded context review
- module scope: implementation responsibility review
- symbol scope: class-level or inheritance-level inspection

## Good review sequence

- start at the overview page
- open a hot directory
- inspect the highest fan-in modules
- open symbols from those modules
- use focused UML bundles where the website suggests a hotspot

## Guide strategy

- use the guide builder when diagrams alone are not enough
- keep technical startup and hosting instructions close to the explorer
- keep functional flow pages close to the entity pages so architecture and operation stay connected
