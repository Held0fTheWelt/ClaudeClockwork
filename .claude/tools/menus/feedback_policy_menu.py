#!/usr/bin/env python3
import json
from pathlib import Path

SETTINGS_PATH = Path(".claude/settings.local.json")

ROLES = ["personaler","content_packer","testops_orchestrator","critic_dispatcher","team_lead"]
MODES = ["strict","balanced","creative"]
BUDGETS = ["tool_only","tool_then_deep_oodle"]

DEFAULTS = {
  "personaler": {"mode":"balanced","budget":"tool_only"},
  "content_packer": {"mode":"strict","budget":"tool_only"},
  "testops_orchestrator": {"mode":"balanced","budget":"tool_only"},
  "critic_dispatcher": {"mode":"strict","budget":"tool_only"},
  "team_lead": {"mode":"balanced","budget":"tool_only"},
}

def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    return {}

def save_settings(cfg: dict) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")

def ensure_feedback(cfg: dict) -> dict:
    cfg.setdefault("feedback", {})
    cfg["feedback"].setdefault("defaults", DEFAULTS)
    cfg["feedback"].setdefault("overrides", {})
    return cfg

def set_override(role: str, mode: str, budget: str) -> None:
    cfg = ensure_feedback(load_settings())
    cfg["feedback"]["overrides"][role] = {"mode": mode, "budget": budget}
    save_settings(cfg)

def clear_override(role: str) -> None:
    cfg = ensure_feedback(load_settings())
    cfg["feedback"]["overrides"].pop(role, None)
    save_settings(cfg)

def effective(role: str, cfg: dict) -> dict:
    cfg = ensure_feedback(cfg)
    ov = cfg["feedback"]["overrides"].get(role)
    if ov:
        return ov
    return cfg["feedback"]["defaults"].get(role, DEFAULTS[role])

def menu():
    while True:
        cfg = ensure_feedback(load_settings())
        print("\nFeedback Policy Menu")
        print("--------------------")
        for i, role in enumerate(ROLES, start=1):
            eff = effective(role, cfg)
            ov = cfg["feedback"]["overrides"].get(role)
            mark = "*" if ov else " "
            print(f"{i}){mark} {role:18} mode={eff['mode']:<8} budget={eff['budget']}")
        print("\nActions:")
        print("  s) set override for a role")
        print("  c) clear override for a role")
        print("  r) reset ALL overrides")
        print("  0) exit")

        choice = input("\nSelect: ").strip().lower()
        if choice == "0":
            return
        if choice == "r":
            cfg["feedback"]["overrides"] = {}
            save_settings(cfg)
            continue
        if choice in ("s","c"):
            try:
                idx = int(input(f"Role number (1-{len(ROLES)}): ").strip())
                role = ROLES[idx-1]
            except Exception:
                print("Invalid role selection.")
                continue
            if choice == "c":
                clear_override(role)
                continue
            # set
            mode = input(f"Mode {MODES} (default {DEFAULTS[role]['mode']}): ").strip().lower() or DEFAULTS[role]['mode']
            if mode not in MODES:
                print("Invalid mode.")
                continue
            budget = input(f"Budget {BUDGETS} (default {DEFAULTS[role]['budget']}): ").strip().lower() or DEFAULTS[role]['budget']
            if budget not in BUDGETS:
                print("Invalid budget.")
                continue
            set_override(role, mode, budget)
            continue
        print("Unknown action.")

if __name__ == "__main__":
    menu()
