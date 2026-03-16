#!/usr/bin/env python3
import json
from pathlib import Path

SETTINGS_PATH = Path(".claude/settings.local.json")
DEFAULT_MAX = 12
ALLOWED = list(range(8, 13))

def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    return {}

def save_settings(cfg: dict) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")

def set_max_plan_tasks(value: int) -> None:
    if value not in ALLOWED:
        raise ValueError(f"max_plan_tasks must be one of {ALLOWED}")
    cfg = load_settings()
    cfg.setdefault("planning", {})
    cfg["planning"].setdefault("max_plan_tasks_default", DEFAULT_MAX)
    cfg["planning"]["max_plan_tasks"] = value
    save_settings(cfg)

def reset_to_default() -> None:
    cfg = load_settings()
    cfg.setdefault("planning", {})
    cfg["planning"]["max_plan_tasks_default"] = DEFAULT_MAX
    cfg["planning"]["max_plan_tasks"] = cfg["planning"]["max_plan_tasks_default"]
    save_settings(cfg)

def menu():
    while True:
        cfg = load_settings()
        planning = cfg.get("planning", {})
        current = planning.get("max_plan_tasks", DEFAULT_MAX)
        default = planning.get("max_plan_tasks_default", DEFAULT_MAX)

        print("\nPlanning Policy Menu")
        print("--------------------")
        print(f"Current max_plan_tasks: {current} (default: {default})\n")
        for i, v in enumerate(ALLOWED, start=1):
            print(f"{i}) Set max_plan_tasks to {v}")
        print(f"{len(ALLOWED)+1}) Reset to default ({default})")
        print("0) Exit")

        choice = input("\nSelect: ").strip()
        if choice == "0":
            return
        if choice == str(len(ALLOWED)+1):
            reset_to_default()
            continue
        try:
            idx = int(choice)
            if 1 <= idx <= len(ALLOWED):
                set_max_plan_tasks(ALLOWED[idx-1])
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")

if __name__ == "__main__":
    menu()
