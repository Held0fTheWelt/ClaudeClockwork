You are Claude running Claude angents inside ClaudeClockwork.

Mission:
Repair the Ollama-only execution kernel so that pure LocalAI work can actually run through the intended guarded path.

Scope:
Fix only the narrow kernel issues below.
Do not broaden the task.
Do not redesign unrelated systems.
Do not touch docs except where strictly necessary to reflect the repaired behavior.
Do not implement new features beyond what is required to make the existing mode/runtime path work correctly.

Repository:
D:\ClaudeClockwork

Critical constraints:
- Work only in D:\ClaudeClockwork
- Do not use or create project-local .claude folders in other repos
- Do not bypass the system by doing the task directly
- Do not create ad-hoc helper scripts as a substitute for fixing the runtime path
- Do not use Claude subagents for implementation
- Commit after each completed repair step with descriptive commit messages

Repair only these kernel defects:

1) Add missing mode metadata for manifest skills
Problem:
The guarded manifest path rejects key LocalAI skills because metadata.mode_requirements is missing.

Required fixes:
- Patch .claude/skills/localai/skill_forge_run/manifest.json
- Patch .claude/skills/localai/localai_run/manifest.json

Requirements:
- Add valid metadata.mode_requirements
- Ensure the declarations match intended LocalAI usage
- These skills must pass ModeMetadataValidator on the official manifest path
- Do not weaken validation logic globally just to make them pass

2) Point skill_forge_run at the real implementation
Problem:
The active manifest entrypoint for skill_forge_run points at the stub implementation in .claude/... instead of the more complete implementation in claudeclockwork/localai/skills/skill_forge_run.py

Required fixes:
- Inspect both implementations:
  - .claude/skills/localai/skill_forge_run/skill.py
  - claudeclockwork/localai/skills/skill_forge_run.py
- Make the manifest-backed execution path use the real implementation

Requirements:
- Prefer correcting the manifest entrypoint or consolidating to one canonical implementation
- Remove or neutralize the stub path so it cannot silently be used again
- Do not keep two divergent active implementations
- Final behavior must execute the real LocalAI pipeline or fail honestly

3) Make skill_forge_run non-stub in practice
Problem:
Current active behavior ends in partial_success placeholder behavior instead of real execution.

Required fixes:
- Ensure skill_forge_run actually runs the intended staged LocalAI flow
- Ensure it does not return fake success or placeholder partial success
- If a required stage is unavailable, fail explicitly with a real error
- Publish behavior must be honest and based on actual outputs

Requirements:
- No fake temp workspace success path
- No placeholder final_status
- No “looks implemented” surface with non-executing core

4) Make localai_run usable through the guarded manifest path
Problem:
localai_run currently fails mode metadata validation on the official path.

Required fixes:
- Ensure localai_run is manifest-valid
- Ensure it executes through the real bridge/runtime path under mode enforcement
- Ensure it does not bypass mode checks

5) Keep mode enforcement intact
Problem:
The goal is not to weaken the guard, but to make the intended LocalAI skills compliant.

Requirements:
- Do not disable ModeMetadataValidator
- Do not add broad fallback exceptions
- Do not make unknown or underspecified skills auto-pass
- Preserve the hard contract that mode declarations are required

6) Add narrow regression tests
Add focused tests only for the repaired kernel behavior.

Must prove:
- skill_forge_run manifest metadata is accepted by the validator
- localai_run manifest metadata is accepted by the validator
- skill_forge_run resolves to the intended non-stub implementation
- invoking skill_forge_run through the official skill runner / bridge path does not return placeholder partial_success
- invoking localai_run through the official guarded path works or fails honestly
- default mode still enforces the guarded LocalAI path rather than weakening checks

7) Verification
At the end, report only:
- changed files
- what was repaired
- exact tests run
- test results
- one concrete proof that skill_forge_run now uses the real implementation
- one concrete proof that localai_run now passes the guarded manifest path

Definition of done:
- skill_forge_run manifest has valid mode metadata
- localai_run manifest has valid mode metadata
- skill_forge_run no longer routes to the stub implementation
- skill_forge_run executes a real LocalAI path or fails honestly
- localai_run executes through the official guarded manifest path
- validation remains strict
- regression tests prove the repaired kernel behavior