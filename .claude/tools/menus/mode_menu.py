#!/usr/bin/env python3
"""Interactive menu for managing ClaudeClockwork execution modes."""
import json
from pathlib import Path

SETTINGS_PATH = Path(".claude/settings.local.json")
MODE_STATE_PATH = Path(".claude/state/mode_state.json")

MODES = {
    "default": {
        "name": "Pure Ollama Agent Mode",
        "description": "Execute all skills with local Ollama agents only",
        "allows_ollama": True,
        "allows_claude": False,
        "allows_hybrid": False,
        "use_case": "Cost-effective, privacy-focused, offline-capable"
    },
    "adaptive": {
        "name": "Adaptive Mode",
        "description": "Support both Ollama and Claude agents, optimize per task",
        "allows_ollama": True,
        "allows_claude": True,
        "allows_hybrid": True,
        "use_case": "Balanced performance and cost, intelligent routing"
    },
    "claude-min": {
        "name": "Claude Minimal Mode",
        "description": "Execute with Claude API agents only (minimized costs)",
        "allows_ollama": False,
        "allows_claude": True,
        "allows_hybrid": False,
        "use_case": "Cloud-based, minimized API costs, complex reasoning"
    }
}


def load_mode_state() -> dict:
    """Load current mode state."""
    if MODE_STATE_PATH.exists():
        try:
            return json.loads(MODE_STATE_PATH.read_text(encoding="utf-8"))
        except:
            return {"active_mode": "default"}
    return {"active_mode": "default"}


def save_mode_state(state: dict) -> None:
    """Save mode state."""
    MODE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODE_STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def get_active_mode() -> str:
    """Get currently active mode."""
    state = load_mode_state()
    return state.get("active_mode", "default")


def set_active_mode(mode: str) -> bool:
    """Set active mode."""
    if mode not in MODES:
        return False
    state = load_mode_state()
    state["active_mode"] = mode
    save_mode_state(state)
    return True


def print_mode_details(mode: str) -> None:
    """Print detailed information about a mode."""
    info = MODES.get(mode)
    if not info:
        return

    print(f"\n  {info['name']}")
    print(f"  {'-' * len(info['name'])}")
    print(f"  {info['description']}")
    print(f"  Use case: {info['use_case']}")
    print(f"  Supports: ", end="")
    supports = []
    if info['allows_ollama']:
        supports.append("Ollama")
    if info['allows_claude']:
        supports.append("Claude")
    if info['allows_hybrid']:
        supports.append("Hybrid")
    print(", ".join(supports))


def menu():
    """Interactive mode selection menu."""
    while True:
        active = get_active_mode()

        print("\n╔══════════════════════════════════════════════════════════╗")
        print("║         ClaudeClockwork Execution Mode Menu              ║")
        print("╚══════════════════════════════════════════════════════════╝")

        # Show all modes with selection indicator
        for i, (mode_key, mode_info) in enumerate(MODES.items(), start=1):
            marker = " ✓ " if mode_key == active else "   "
            print(f"{i}){marker}{mode_info['name']:40} [{mode_key}]")

        print("\nOptions:")
        print("  i) Show mode details")
        print("  s) Switch mode")
        print("  0) Exit")

        choice = input("\nSelect option (or mode number): ").strip().lower()

        if choice == "0":
            print("Goodbye!")
            return

        if choice == "i":
            # Show details for a mode
            mode_num = input(f"Which mode? (1-{len(MODES)}): ").strip()
            try:
                idx = int(mode_num) - 1
                mode_key = list(MODES.keys())[idx]
                print_mode_details(mode_key)
            except (ValueError, IndexError):
                print("Invalid selection.")
            continue

        if choice == "s":
            # Switch mode
            mode_num = input(f"Switch to mode (1-{len(MODES)}): ").strip()
            try:
                idx = int(mode_num) - 1
                mode_key = list(MODES.keys())[idx]
                if set_active_mode(mode_key):
                    mode_info = MODES[mode_key]
                    print(f"\n✓ Mode switched to: {mode_info['name']}")
                    print(f"  {mode_info['description']}")
                else:
                    print("Invalid mode selection.")
            except (ValueError, IndexError):
                print("Invalid selection.")
            continue

        # Direct mode number selection
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(MODES):
                mode_key = list(MODES.keys())[idx]
                if set_active_mode(mode_key):
                    mode_info = MODES[mode_key]
                    print(f"\n✓ Mode switched to: {mode_info['name']}")
                    print(f"  {mode_info['description']}")
                continue
        except ValueError:
            pass

        print("Unknown option. Please try again.")


if __name__ == "__main__":
    menu()
