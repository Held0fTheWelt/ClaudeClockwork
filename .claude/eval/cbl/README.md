# CBL — Capability Benchmark Ladder (MVP24-D)

Benchmark tasks that define unlock criteria for each CBL rung. See Report 08 and `.claude-development/designs/eval_shadow_ab_cbl_spec.md`.

## Current position

**Rung 1 (Single-Agent)** — per Report 08.

## Structure

- `unlock_rules.yaml` — progression requirements, ceremony steps, demotion rules.
- `rung_<n>_<name>/` — one directory per rung; each contains `bench_*.yaml` benchmark task definitions.
- Example: `rung_1_single_agent/bench_route_simple.yaml`. Remaining benchmarks (rung_0 through rung_8) to be added in MVP30 (CBL Rung Unlock Ceremonies).

## Running CBL benchmarks

Implementation (MVP25/MVP30) will provide a runner that loads benchmarks from this tree, executes them, and records results to `.llama_runtime/cbl/` for progression tracking.
