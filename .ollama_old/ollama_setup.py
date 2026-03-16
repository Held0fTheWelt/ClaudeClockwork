#!/usr/bin/env python3
"""
ClaudeClockwork local Ollama setup.

Purpose
-------
Create profile-tuned local model aliases for ClaudeClockwork, write a
machine-readable Clockwork mode config, and optionally pull missing models.

This script is deliberately conservative:
- it does not delete models unless --prune is passed
- it does not pull missing models unless --pull-missing is passed
- it uses Linux-safe temp paths under /tmp instead of Windows TEMP fallbacks
- it writes a separate Clockwork config instead of silently overwriting repo files

Project language for Clockwork-facing artifacts is English.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

HARDWARE = {
    "host": "WSL2 / Linux",
    "ram_gb": 64,
    "wsl_ram_gb": 56,
    "swap_gb": 8,
    "gpu": "RTX 3080 10GB",
    "cpu_threads": 16,
}

DEFAULT_OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
CONFIG_DIR = Path.home() / ".claudeclockwork" / "ollama"
CONFIG_PATH = CONFIG_DIR / "clockwork_mode.json"
TMP_MODELDIR = Path(os.environ.get("TMPDIR", "/tmp")) / "claudeclockwork_ollama_modelfiles"

PROFILE_ICONS = {
    "execution": "⚙",
    "coding": "💻",
    "review": "🔍",
    "planning": "🗺",
    "reasoning": "🧠",
    "docs": "📄",
    "summarize": "📝",
    "integration": "🔗",
    "judge": "⚖",
    "creative": "🎨",
    "vision": "👁",
    "packing": "📦",
    "research": "🔬",
    "embedding": "🧬",
    "unreal": "🕹",
    "autopsy": "🩺",
}

PROFILES: Dict[str, Dict[str, object]] = {
    "execution": {
        "description": "Deterministic executor for exact task application.",
        "params": {
            "temperature": 0.05,
            "top_p": 0.85,
            "top_k": 10,
            "repeat_penalty": 1.0,
            "min_p": 0.10,
            "num_ctx": 8192,
            "num_thread": 16,
        },
        "system": (
            "You are a deterministic execution worker. Apply the requested action "
            "exactly. Never add optional improvements. If instructions are ambiguous, "
            "output a short blocker list instead of guessing."
        ),
    },
    "coding": {
        "description": "Primary implementation profile for production code.",
        "params": {
            "temperature": 0.10,
            "top_p": 0.90,
            "top_k": 20,
            "repeat_penalty": 1.0,
            "min_p": 0.05,
            "num_ctx": 16384,
            "num_thread": 16,
        },
        "system": (
            "You are an expert software engineer. Produce correct, minimal, "
            "production-ready code. Follow existing conventions. Do not refactor or "
            "expand scope unless explicitly instructed."
        ),
    },
    "unreal": {
        "description": "Unreal Engine specialist for C++, build, modules and editor tooling.",
        "params": {
            "temperature": 0.08,
            "top_p": 0.90,
            "top_k": 20,
            "repeat_penalty": 1.0,
            "min_p": 0.05,
            "num_ctx": 16384,
            "num_thread": 16,
        },
        "system": (
            "You are a senior Unreal Engine specialist. Prioritize compile safety, "
            "module boundaries, reflection constraints, editor/runtime separation, "
            "build correctness, and project conventions."
        ),
    },
    "review": {
        "description": "Strict review profile for defect-focused code review.",
        "params": {
            "temperature": 0.10,
            "top_p": 0.90,
            "top_k": 20,
            "repeat_penalty": 1.05,
            "min_p": 0.05,
            "num_ctx": 16384,
            "num_thread": 16,
        },
        "system": (
            "You are a critical reviewer. Focus on correctness, regressions, missing "
            "tests, unsafe assumptions, architecture drift, and policy violations. "
            "Prefer precise issue lists over broad prose."
        ),
    },
    "planning": {
        "description": "Strategic planning for multi-step Clockwork work packets.",
        "params": {
            "temperature": 0.25,
            "top_p": 0.92,
            "top_k": 40,
            "repeat_penalty": 1.05,
            "min_p": 0.03,
            "num_ctx": 16384,
            "num_thread": 16,
        },
        "system": (
            "You are a systems planner. Break large work into reliable execution "
            "packs, preserve constraints, and optimize for reviewability, rollback "
            "safety, and deterministic delivery."
        ),
    },
    "reasoning": {
        "description": "High-depth reasoning for escalations and difficult design choices.",
        "params": {
            "temperature": 0.20,
            "top_p": 0.92,
            "top_k": 40,
            "repeat_penalty": 1.05,
            "min_p": 0.03,
            "num_ctx": 16384,
            "num_thread": 16,
        },
        "system": (
            "You are a senior reasoning model for hard trade-offs, root causes, and "
            "conflicting evidence. Prefer explicit assumptions, decision criteria, and "
            "clear final recommendations."
        ),
    },
    "docs": {
        "description": "Technical documentation and operational writeups.",
        "params": {
            "temperature": 0.15,
            "top_p": 0.90,
            "top_k": 30,
            "repeat_penalty": 1.03,
            "min_p": 0.04,
            "num_ctx": 16384,
            "num_thread": 16,
        },
        "system": (
            "You write clear technical documentation. Keep structure tight, preserve "
            "facts, separate procedure from rationale, and avoid marketing language."
        ),
    },
    "summarize": {
        "description": "Compression profile for packs, reports, and context handoff.",
        "params": {
            "temperature": 0.10,
            "top_p": 0.90,
            "top_k": 20,
            "repeat_penalty": 1.02,
            "min_p": 0.05,
            "num_ctx": 16384,
            "num_thread": 16,
        },
        "system": (
            "You compress large technical context into compact, loss-aware handoff "
            "packs. Preserve decisions, blockers, evidence, and next actions."
        ),
    },
    "packing": {
        "description": "Context curator for pack building and work brief compaction.",
        "params": {
            "temperature": 0.08,
            "top_p": 0.88,
            "top_k": 20,
            "repeat_penalty": 1.02,
            "min_p": 0.05,
            "num_ctx": 16384,
            "num_thread": 16,
        },
        "system": (
            "You are a context packer. Reduce noisy inputs into compact execution-ready "
            "briefs with explicit scope, constraints, evidence, and open questions."
        ),
    },
    "integration": {
        "description": "Integration profile for multi-file changes and repo fit checks.",
        "params": {
            "temperature": 0.10,
            "top_p": 0.90,
            "top_k": 20,
            "repeat_penalty": 1.02,
            "min_p": 0.05,
            "num_ctx": 16384,
            "num_thread": 16,
        },
        "system": (
            "You integrate changes into an existing codebase. Optimize for consistency, "
            "compile safety, migration safety, and repo-wide fit."
        ),
    },
    "judge": {
        "description": "Independent arbiter for reviewer disagreements.",
        "params": {
            "temperature": 0.08,
            "top_p": 0.88,
            "top_k": 20,
            "repeat_penalty": 1.05,
            "min_p": 0.05,
            "num_ctx": 16384,
            "num_thread": 16,
        },
        "system": (
            "You are an adjudicator. Compare competing analyses, identify the deciding "
            "evidence, and return a clear verdict with uncertainty noted."
        ),
    },
    "autopsy": {
        "description": "Failure autopsy and regression root-cause analysis.",
        "params": {
            "temperature": 0.08,
            "top_p": 0.90,
            "top_k": 20,
            "repeat_penalty": 1.05,
            "min_p": 0.05,
            "num_ctx": 16384,
            "num_thread": 16,
        },
        "system": (
            "You perform a failure autopsy. Identify the first likely break, the causal "
            "chain, the strongest evidence, and the smallest proving or disproving test."
        ),
    },
    "creative": {
        "description": "Creative exploration for design, naming, worldbuilding and ideation.",
        "params": {
            "temperature": 0.70,
            "top_p": 0.95,
            "top_k": 60,
            "repeat_penalty": 1.03,
            "min_p": 0.02,
            "num_ctx": 16384,
            "num_thread": 16,
        },
        "system": (
            "You are a creative but grounded collaborator. Generate varied options, keep "
            "tone consistent, and remain faithful to project constraints and established lore."
        ),
    },
    "vision": {
        "description": "Screenshot, UI, and visual artifact review.",
        "params": {
            "temperature": 0.10,
            "top_p": 0.90,
            "top_k": 20,
            "repeat_penalty": 1.02,
            "min_p": 0.05,
            "num_ctx": 8192,
            "num_thread": 16,
        },
        "system": (
            "You analyze screenshots and visual artifacts. Focus on layout problems, "
            "readability, interaction risks, inconsistencies, and high-value UI fixes."
        ),
    },
    "research": {
        "description": "Neutral option analysis and trade-off synthesis.",
        "params": {
            "temperature": 0.18,
            "top_p": 0.90,
            "top_k": 30,
            "repeat_penalty": 1.03,
            "min_p": 0.04,
            "num_ctx": 16384,
            "num_thread": 16,
        },
        "system": (
            "You are a research analyst. Compare options fairly, identify trade-offs, "
            "separate facts from inferences, and end with a practical recommendation."
        ),
    },
}

# Stable recipes assume models the user already has or is likely to keep.
MODEL_RECIPES: List[Dict[str, object]] = [
    {
        "source": "qwen2.5-coder:32b",
        "target": "qwen2.5-coder-32b:coding",
        "profile": "coding",
        "gpu_layers": 8,
        "stage": "stable",
        "role": "implementation_worker",
        "note": "Primary implementation model for code changes.",
    },
    {
        "source": "qwen2.5-coder:32b",
        "target": "qwen2.5-coder-32b:review",
        "profile": "review",
        "gpu_layers": 8,
        "stage": "stable",
        "role": "reviewer_crosscheck",
        "note": "Independent cross-check reviewer.",
    },
    {
        "source": "qwen2.5-coder:32b",
        "target": "qwen2.5-coder-32b:integration",
        "profile": "integration",
        "gpu_layers": 8,
        "stage": "stable",
        "role": "integrator",
        "note": "Multi-file integration and repo fit.",
    },
    {
        "source": "qwen2.5-coder:32b",
        "target": "qwen2.5-coder-32b:unreal",
        "profile": "unreal",
        "gpu_layers": 8,
        "stage": "stable",
        "role": "unreal_specialist",
        "note": "Unreal specialist for engine and plugin work.",
    },
    {
        "source": "deepseek-coder:33b-instruct-q4_K_M",
        "target": "deepseek-coder-33b:coding",
        "profile": "coding",
        "gpu_layers": 8,
        "stage": "stable",
        "role": "implementation_backup",
        "note": "Backup coder and alternative implementation angle.",
    },
    {
        "source": "deepseek-coder:33b-instruct-q4_K_M",
        "target": "deepseek-coder-33b:review",
        "profile": "review",
        "gpu_layers": 8,
        "stage": "stable",
        "role": "reviewer_primary",
        "note": "Primary deep code reviewer.",
    },
    {
        "source": "qwen2.5:14b-instruct",
        "target": "qwen2.5-14b:docs",
        "profile": "docs",
        "gpu_layers": 12,
        "stage": "stable",
        "role": "documentation_worker",
        "note": "Technical documentation and runbook writing.",
    },
    {
        "source": "qwen2.5:14b-instruct",
        "target": "qwen2.5-14b:packing",
        "profile": "packing",
        "gpu_layers": 12,
        "stage": "stable",
        "role": "context_packer",
        "note": "Pack builder and work brief compactor.",
    },
    {
        "source": "qwen2.5:14b-instruct",
        "target": "qwen2.5-14b:summarize",
        "profile": "summarize",
        "gpu_layers": 12,
        "stage": "stable",
        "role": "summarizer",
        "note": "Fast compact summaries for handoff.",
    },
    {
        "source": "qwen2.5:14b-instruct",
        "target": "qwen2.5-14b:research",
        "profile": "research",
        "gpu_layers": 12,
        "stage": "stable",
        "role": "research_fast",
        "note": "Fast option analysis for medium complexity tasks.",
    },
    {
        "source": "qwen2.5:72b-instruct-q5_K_M",
        "target": "qwen2.5-72b:planning",
        "profile": "planning",
        "gpu_layers": 6,
        "stage": "stable",
        "role": "designer_planner",
        "note": "Heavy planning and architecture task decomposition.",
    },
    {
        "source": "qwen2.5:72b-instruct-q5_K_M",
        "target": "qwen2.5-72b:reasoning",
        "profile": "reasoning",
        "gpu_layers": 6,
        "stage": "stable",
        "role": "research_heavy",
        "note": "Heavy trade-off reasoning and deep analysis.",
    },
    {
        "source": "qwen2.5:72b-instruct-q5_K_M",
        "target": "qwen2.5-72b:creative",
        "profile": "creative",
        "gpu_layers": 6,
        "stage": "stable",
        "role": "creative_backup",
        "note": "Backup creative model when 70B is not desirable.",
    },
    {
        "source": "llama3.3:70b-instruct-q5_K_M",
        "target": "llama3.3-70b:reasoning",
        "profile": "reasoning",
        "gpu_layers": 6,
        "stage": "stable",
        "role": "team_lead_orchestrator",
        "note": "Top-tier orchestration and escalations.",
    },
    {
        "source": "llama3.3:70b-instruct-q5_K_M",
        "target": "llama3.3-70b:planning",
        "profile": "planning",
        "gpu_layers": 6,
        "stage": "stable",
        "role": "planner_backup",
        "note": "Alternative strategic planner for difficult work.",
    },
    {
        "source": "llama3.3:70b-instruct-q5_K_M",
        "target": "llama3.3-70b:creative",
        "profile": "creative",
        "gpu_layers": 6,
        "stage": "stable",
        "role": "creative_primary",
        "note": "High-end creative exploration and narrative ideation.",
    },
]

OPTIONAL_RECIPES: List[Dict[str, object]] = [
    {
        "source": "qwen3-coder:30b",
        "target": "qwen3-coder-30b:coding",
        "profile": "coding",
        "gpu_layers": 8,
        "stage": "optional",
        "role": "repo_operator",
        "note": "Agentic repo operator and strong long-context coding candidate.",
    },
    {
        "source": "qwen3-coder:30b",
        "target": "qwen3-coder-30b:integration",
        "profile": "integration",
        "gpu_layers": 8,
        "stage": "optional",
        "role": "repo_integrator",
        "note": "Longer-context integrator for larger Clockwork packs.",
    },
    {
        "source": "devstral-small-2",
        "target": "devstral-small-2:execution",
        "profile": "execution",
        "gpu_layers": 8,
        "stage": "optional",
        "role": "taskrunner_repo",
        "note": "Tool-use and repo navigation specialist.",
    },
    {
        "source": "devstral-small-2",
        "target": "devstral-small-2:packing",
        "profile": "packing",
        "gpu_layers": 8,
        "stage": "optional",
        "role": "task_compactor",
        "note": "Repo-aware compactor for work briefs and pack curation.",
    },
    {
        "source": "deepseek-r1:14b",
        "target": "deepseek-r1-14b:judge",
        "profile": "judge",
        "gpu_layers": 10,
        "stage": "optional",
        "role": "arbiter",
        "note": "Independent judge when reviewers disagree.",
    },
    {
        "source": "deepseek-r1:14b",
        "target": "deepseek-r1-14b:autopsy",
        "profile": "autopsy",
        "gpu_layers": 10,
        "stage": "optional",
        "role": "failure_autopsy",
        "note": "Root-cause and regression autopsy specialist.",
    },
    {
        "source": "gemma3:12b",
        "target": "gemma3-12b:vision",
        "profile": "vision",
        "gpu_layers": 10,
        "stage": "optional",
        "role": "vision_review",
        "note": "Vision review for screenshots, UI, and visual QA.",
    },
]

EMBEDDING_MODELS = [
    {"source": "mxbai-embed-large", "role": "embedding_primary"},
    {"source": "nomic-embed-text", "role": "embedding_long_context"},
]

PRUNE_CANDIDATES = [
    "qwen2.5-coder:14b",
    "qwen2.5-coder:latest",
    "qwen2.5:7b-instruct",
    "deepseek-coder:6.7b",
    "qwen2.5-coder-32k:latest",
]

CLOCKWORK_MODE = {
    "mode_name": "claudeclockwork-local-ollama",
    "description": "Local model orchestration mode for ClaudeClockwork with quality-first defaults.",
    "repo_alignment": {
        "system_doc": ".claude/SYSTEM.md",
        "root_policy_doc": "MODEL_POLICY.md",
        "root_architecture_doc": "ARCHITECTURE.md",
        "external_routing_doc": ".claude/config/model_routing.yaml",
        "external_escalation_doc": ".claude/config/model_escalation_ladder.yaml",
    },
    "roles": {
        "team_lead_orchestrator": ["llama3.3-70b:reasoning", "qwen2.5-72b:reasoning"],
        "designer_planner": ["qwen2.5-72b:planning", "llama3.3-70b:planning"],
        "context_packer": ["qwen2.5-14b:packing", "qwen2.5-14b:summarize"],
        "task_compactor": ["devstral-small-2:packing", "qwen2.5-14b:packing"],
        "implementation_worker": ["qwen2.5-coder-32b:coding", "deepseek-coder-33b:coding"],
        "unreal_specialist": ["qwen2.5-coder-32b:unreal", "qwen2.5-coder-32b:coding"],
        "integrator": ["qwen2.5-coder-32b:integration", "qwen3-coder-30b:integration"],
        "reviewer_primary": ["deepseek-coder-33b:review", "qwen2.5-coder-32b:review"],
        "reviewer_crosscheck": ["qwen2.5-coder-32b:review", "qwen2.5-14b:research"],
        "arbiter": ["deepseek-r1-14b:judge", "qwen2.5-72b:reasoning"],
        "failure_autopsy": ["deepseek-r1-14b:autopsy", "llama3.3-70b:reasoning"],
        "documentation_worker": ["qwen2.5-14b:docs", "qwen2.5-14b:summarize"],
        "release_notes_editor": ["qwen2.5-14b:docs", "llama3.3-70b:planning"],
        "research_fast": ["qwen2.5-14b:research", "qwen2.5-14b:summarize"],
        "research_heavy": ["qwen2.5-72b:reasoning", "llama3.3-70b:reasoning"],
        "creative_primary": ["llama3.3-70b:creative", "qwen2.5-72b:creative"],
        "vision_review": ["gemma3-12b:vision"],
        "embedding_primary": ["mxbai-embed-large"],
        "embedding_long_context": ["nomic-embed-text"],
    },
}


def run(cmd: List[str], *, capture: bool = True) -> Tuple[int, str, str]:
    result = subprocess.run(cmd, capture_output=capture, text=True)
    return result.returncode, result.stdout, result.stderr


def ph(title: str) -> None:
    print(f"\n{'═' * 72}")
    print(f"  {title}")
    print(f"{'═' * 72}")


def ok(msg: str) -> None:
    print(f"     ✓  {msg}")


def warn(msg: str) -> None:
    print(f"     ⚠  {msg}")


def info(msg: str) -> None:
    print(f"     ℹ  {msg}")


def err(msg: str) -> None:
    print(f"     ✗  {msg}")


def skip(msg: str) -> None:
    print(f"     ○  {msg}")


def is_wsl() -> bool:
    return "microsoft" in platform.uname().release.lower() or os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop")


def get_installed_models() -> List[str]:
    code, out, _ = run(["ollama", "list"])
    if code != 0:
        return []
    models: List[str] = []
    for line in out.strip().splitlines()[1:]:
        parts = line.split()
        if parts:
            models.append(parts[0])
    return models


def ensure_ollama_available() -> bool:
    if shutil.which("ollama") is None:
        err("Ollama is not installed or not in PATH.")
        return False
    code, _, _ = run(["ollama", "list"])
    if code != 0:
        err("Ollama server is not reachable. Start it first, then rerun this script.")
        return False
    return True


def system_check() -> None:
    ph("1 / 7  —  System check")
    ok(f"Host platform: {platform.system()} | WSL={is_wsl()}")
    ok(f"Configured hardware budget: {HARDWARE['ram_gb']}GB RAM | {HARDWARE['gpu']} | {HARDWARE['cpu_threads']} threads")
    info(f"Effective OLLAMA_HOST: {DEFAULT_OLLAMA_HOST}")
    models_path = os.environ.get("OLLAMA_MODELS")
    if models_path:
        info(f"OLLAMA_MODELS={models_path}")
        if models_path.startswith("/mnt/"):
            warn("Models path is on a mounted Windows drive. This is valid, but large models will load more slowly.")
    else:
        info("OLLAMA_MODELS not set in current shell.")
    tmp_root = Path(os.environ.get("TMPDIR", "/tmp"))
    ok(f"Temp workspace root: {tmp_root}")


def make_modelfile(source: str, profile_name: str, gpu_layers: int, note: str) -> str:
    profile = PROFILES[profile_name]
    params = dict(profile["params"])
    src = source.lower()

    if any(tag in src for tag in ["70b", "72b"]):
        params["num_ctx"] = min(int(params["num_ctx"]), 8192)
    elif any(tag in src for tag in ["32b", "33b", "30b"]):
        params["num_ctx"] = min(int(params["num_ctx"]), 16384)
    elif any(tag in src for tag in ["14b", "12b", "11b"]):
        params["num_ctx"] = min(int(params["num_ctx"]), 16384)

    lines = [
        f"FROM {source}",
        f"SYSTEM \"\"\"{profile['system']}\"\"\"",
        f"# {note}",
        f"PARAMETER num_gpu {gpu_layers}",
    ]
    for key, value in params.items():
        lines.append(f"PARAMETER {key} {value}")
    return "\n".join(lines) + "\n"


def pull_model(name: str, dry_run: bool) -> bool:
    if dry_run:
        skip(f"[dry-run] ollama pull {name}")
        return True
    code, _, stderr = run(["ollama", "pull", name], capture=False)
    if code == 0:
        ok(f"Pulled: {name}")
        return True
    err(f"Pull failed: {name} | {stderr.strip()[:160]}")
    return False


def build_recipes(recipes: Iterable[Dict[str, object]], installed: List[str], *, dry_run: bool, pull_missing: bool) -> Dict[str, int]:
    TMP_MODELDIR.mkdir(parents=True, exist_ok=True)
    stats = {"built": 0, "missing": 0, "skipped": 0, "errors": 0}
    for recipe in recipes:
        source = str(recipe["source"])
        target = str(recipe["target"])
        profile = str(recipe["profile"])
        gpu_layers = int(recipe["gpu_layers"])
        role = str(recipe["role"])
        note = str(recipe["note"])

        if source not in installed:
            if pull_missing:
                info(f"Missing source model, attempting pull: {source}")
                if pull_model(source, dry_run=dry_run):
                    installed[:] = get_installed_models()
                else:
                    stats["errors"] += 1
                    continue
            else:
                skip(f"Missing source model: {source} -> cannot build {target}")
                stats["missing"] += 1
                continue

        safe_name = target.replace(":", "_").replace("/", "_")
        modelfile_path = TMP_MODELDIR / f"Modelfile_{safe_name}"
        modelfile_path.write_text(make_modelfile(source, profile, gpu_layers, note), encoding="utf-8")

        print(f"\n  [{role}] {source} -> {target}")
        info(note)

        if dry_run:
            skip(f"[dry-run] ollama create {target} -f {modelfile_path}")
            stats["skipped"] += 1
            continue

        code, _, stderr = run(["ollama", "create", target, "-f", str(modelfile_path)])
        if code == 0:
            ok(f"Created: {target}")
            stats["built"] += 1
        else:
            err(f"Create failed: {target} | {stderr.strip()[:160]}")
            stats["errors"] += 1
    return stats


def maybe_prune(installed: List[str], *, dry_run: bool, do_prune: bool) -> None:
    ph("2 / 7  —  Optional prune")
    if not do_prune:
        skip("Prune is disabled by default. Pass --prune to remove known low-value models.")
        return
    removed = 0
    for name in PRUNE_CANDIDATES:
        if name not in installed:
            skip(f"Not installed: {name}")
            continue
        if dry_run:
            skip(f"[dry-run] ollama rm {name}")
            removed += 1
            continue
        code, _, stderr = run(["ollama", "rm", name])
        if code == 0:
            ok(f"Removed: {name}")
            removed += 1
        else:
            err(f"Could not remove {name}: {stderr.strip()[:160]}")
    info(f"Prune operations prepared/executed: {removed}")


def write_clockwork_config(installed: List[str]) -> None:
    ph("6 / 7  —  Write Clockwork mode config")
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    aliases = {}
    for recipe in MODEL_RECIPES + OPTIONAL_RECIPES:
        aliases[str(recipe["target"])] = {
            "source": recipe["source"],
            "profile": recipe["profile"],
            "stage": recipe["stage"],
            "installed": str(recipe["target"]) in installed,
            "source_installed": str(recipe["source"]) in installed,
            "role": recipe["role"],
            "note": recipe["note"],
        }

    config = {
        "hardware": HARDWARE,
        "ollama_host": DEFAULT_OLLAMA_HOST,
        "clockwork_mode": CLOCKWORK_MODE,
        "profiles": {k: {"description": v["description"], "params": v["params"]} for k, v in PROFILES.items()},
        "aliases": aliases,
        "embeddings": EMBEDDING_MODELS,
        "paths": {
            "config_path": str(CONFIG_PATH),
            "tmp_modelfiles": str(TMP_MODELDIR),
        },
    }
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")
    ok(f"Wrote: {CONFIG_PATH}")


def list_profiles() -> None:
    ph("Available profiles")
    for name, profile in PROFILES.items():
        icon = PROFILE_ICONS.get(name, "•")
        params = profile["params"]
        print(f"\n  {icon}  {name}")
        print(f"     {profile['description']}")
        print(
            "     "
            f"t={params['temperature']}  top_k={params['top_k']}  top_p={params['top_p']}  "
            f"repeat_penalty={params['repeat_penalty']}  num_ctx={params['num_ctx']}"
        )


def list_roles() -> None:
    ph("Clockwork role map")
    for role, models in CLOCKWORK_MODE["roles"].items():
        print(f"\n  {role}")
        for model in models:
            print(f"     - {model}")


def print_recipe_summary(include_optional: bool) -> None:
    ph("Recipe summary")
    recipes = MODEL_RECIPES + (OPTIONAL_RECIPES if include_optional else [])
    for recipe in recipes:
        icon = PROFILE_ICONS.get(str(recipe['profile']), "•")
        print(f"  {icon}  {recipe['target']:<34} <- {recipe['source']}")


def print_final_summary(installed: List[str], include_optional: bool) -> None:
    ph("7 / 7  —  Final summary")
    print(f"  Active OLLAMA_HOST: {DEFAULT_OLLAMA_HOST}")
    print(f"  Config path:        {CONFIG_PATH}")
    print(f"  Temp modelfiles:    {TMP_MODELDIR}")
    print("\n  Role coverage:")
    for role, candidates in CLOCKWORK_MODE["roles"].items():
        resolved = next((m for m in candidates if m in installed), None)
        status = "✓" if resolved else "○"
        shown = resolved or candidates[0]
        print(f"     {status}  {role:<24} {shown}")
    print("\n  Embeddings:")
    for item in EMBEDDING_MODELS:
        status = "✓" if item['source'] in installed else "○"
        print(f"     {status}  {item['source']:<22} {item['role']}")
    if include_optional:
        info("Optional recipes were included in this run.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ClaudeClockwork local Ollama setup")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without mutating Ollama")
    parser.add_argument("--check", action="store_true", help="Run system and Ollama availability checks only")
    parser.add_argument("--summary", action="store_true", help="Print recipes and role mapping only")
    parser.add_argument("--list-profiles", action="store_true", help="List all profiles")
    parser.add_argument("--list-roles", action="store_true", help="List Clockwork role mapping")
    parser.add_argument("--with-optional", action="store_true", help="Also build optional model recipes")
    parser.add_argument("--pull-missing", action="store_true", help="Pull missing source models before building aliases")
    parser.add_argument("--skip-build", action="store_true", help="Do not build model aliases")
    parser.add_argument("--skip-config", action="store_true", help="Do not write the Clockwork mode config")
    parser.add_argument("--prune", action="store_true", help="Remove known low-value models")
    return parser.parse_args()


def main() -> int:
    print(
        """
╔══════════════════════════════════════════════════════════════════════════╗
║                ClaudeClockwork — Local Ollama Mode Setup               ║
║         Quality-first profile aliases for WSL / Linux workstations     ║
╚══════════════════════════════════════════════════════════════════════════╝
        """.strip()
    )

    args = parse_args()

    if args.list_profiles:
        list_profiles()
        return 0
    if args.list_roles:
        list_roles()
        return 0
    if args.summary:
        print_recipe_summary(include_optional=args.with_optional)
        list_roles()
        return 0

    system_check()

    if not ensure_ollama_available():
        return 1

    installed = get_installed_models()
    ok(f"Installed model count: {len(installed)}")

    if args.check:
        print_final_summary(installed, include_optional=args.with_optional)
        return 0

    maybe_prune(installed, dry_run=args.dry_run, do_prune=args.prune)
    installed = get_installed_models()

    ph("3 / 7  —  Ensure embeddings")
    for embedding in EMBEDDING_MODELS:
        name = embedding["source"]
        if name in installed:
            ok(f"Embedding present: {name}")
        elif args.pull_missing:
            info(f"Embedding missing, attempting pull: {name}")
            pull_model(name, dry_run=args.dry_run)
        else:
            skip(f"Embedding missing: {name}")

    ph("4 / 7  —  Build stable aliases")
    if args.skip_build:
        skip("Alias creation skipped by flag.")
    else:
        stable_stats = build_recipes(MODEL_RECIPES, installed, dry_run=args.dry_run, pull_missing=args.pull_missing)
        info(f"Stable alias stats: {stable_stats}")

    if args.with_optional and not args.skip_build:
        ph("5 / 7  —  Build optional aliases")
        optional_stats = build_recipes(OPTIONAL_RECIPES, installed, dry_run=args.dry_run, pull_missing=args.pull_missing)
        info(f"Optional alias stats: {optional_stats}")

    installed = get_installed_models()

    if not args.skip_config:
        write_clockwork_config(installed)
    else:
        ph("6 / 7  —  Write Clockwork mode config")
        skip("Config writing skipped by flag.")

    print_final_summary(installed, include_optional=args.with_optional)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
