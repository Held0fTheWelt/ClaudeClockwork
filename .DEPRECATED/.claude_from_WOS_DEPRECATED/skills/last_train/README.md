# last_train_merge (Last-Train Skill)

Scan multiple `.zip` archives, build a **combined** archive (union of all contents), and produce a **timeline report**
showing whether each step is an **evolution** (net improvement) or a **loss** (functionality removed by missing files).

## Why "Last Train"?
You often have multiple archives and want the *last train leaving the station* to carry **everything** that ever mattered.

## Skill ID
- `last_train_merge`

## What it does (deterministic)
1) Read each zip and build a manifest (path -> sha256, size).
2) Ignore junk artifacts (pycache, *.pyc, test caches) using `ignore_globs`.
3) Compare each zip to the previous zip:
   - added / removed / changed files
   - critical path presence
4) Emit a verdict:
   - **evolution**: mostly additions/changes and no critical regressions
   - **loss**: critical removals or significant drops
   - **mixed**: both improvements and regressions
   - **unknown**: insufficient signals
5) Create `combined_last_train.zip` by merging file contents:
   - prefer the **latest** occurrence of each path
   - always omit ignored artifacts

## Safety
- No deletion of the repo.
- Writes only to the configured output dir.

## Typical usage
```bash
python .claude/tools/skills/skill_runner.py --in .claude/contracts/examples/last_train_merge.skill_request.example.json --out out.json
```

## Limitations
- "Evolution vs loss" is heuristic; it cannot understand semantics of code changes.
- If functionality changes without file removals (behavioral regressions), this won't catch it.
- Zip order matters; provide `zip_paths` in chronological order.
