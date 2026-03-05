# AddOn Boundaries (Core vs AddOn)

## Goal
Clockwork must remain easy to understand and maintain:
- **Core**: minimal, always-on essentials
- **AddOns**: optional packs, can be removed without breaking core navigation

## Rules
1) Every Skill ID must be classified as either **core** or an **addon pack member**.
2) AddOn packs must document:
   - included skills
   - outputs and folders touched
   - non-goals / limitations
3) Core must not depend on optional AddOn content to boot.

## Source of truth
- `addons/map.yaml`
- `addons/*/README.md`
