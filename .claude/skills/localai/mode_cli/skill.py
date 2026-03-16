"""Mode CLI skill: manage execution modes (default, adaptive, claude-min)."""
import subprocess
import sys
from pathlib import Path

from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult
from claudeclockwork.core.mode import ModeManager


class ModeCliSkill(SkillBase):
    """CLI interface for mode management."""

    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        root = kwargs.get("root") or context.working_directory
        action = (kwargs.get("action") or "menu").strip().lower()
        mode = (kwargs.get("mode") or "").strip().lower()
        manager = ModeManager(project_root=Path(root))

        # If no action or action is "menu", show interactive menu
        if action == "menu" or action == "":
            return self._show_menu()

        if action == "list":
            return self._action_list(manager)
        if action == "get":
            return self._action_get(manager)
        if action == "set":
            return self._action_set(manager, mode)
        if action == "info":
            return self._action_info(manager)

        return SkillResult(
            False,
            "mode_cli",
            error=f"Unknown action: {action!r}. Use one of: list, get, set, info",
            data={"action": action},
        )

    def _action_list(self, manager: ModeManager) -> SkillResult:
        """List all available modes."""
        modes = ["default", "adaptive", "claude-min"]
        active = manager.get_active_mode()

        mode_descriptions = {
            "default": "Pure Ollama Agent Mode - executes all skills with Ollama agents only",
            "adaptive": "Adaptive Mode - supports both Ollama and Claude agents, chooses optimal route",
            "claude-min": "Claude Minimal Mode - executes with Claude API agents (minimal/cheaper)",
        }

        return SkillResult(
            True,
            "mode_cli",
            data={
                "action": "list",
                "available_modes": modes,
                "active_mode": active,
                "modes": {
                    m: mode_descriptions.get(m, "") for m in modes
                },
                "message": f"Available modes: {', '.join(modes)}. Active: {active}",
            },
        )

    def _action_get(self, manager: ModeManager) -> SkillResult:
        """Get current active mode."""
        active = manager.get_active_mode()
        return SkillResult(
            True,
            "mode_cli",
            data={
                "action": "get",
                "active_mode": active,
                "message": f"Current mode: {active}",
            },
        )

    def _action_set(self, manager: ModeManager, mode: str) -> SkillResult:
        """Set active mode."""
        if not mode:
            return SkillResult(
                False,
                "mode_cli",
                error="Missing 'mode' argument. Use: /mode set default|adaptive|claude-min",
                data={"action": "set"},
            )

        valid_modes = ["default", "adaptive", "claude-min"]
        if mode not in valid_modes:
            return SkillResult(
                False,
                "mode_cli",
                error=f"Invalid mode: {mode!r}. Valid modes: {', '.join(valid_modes)}",
                data={"action": "set", "mode": mode},
            )

        try:
            manager.set_mode(mode)
            return SkillResult(
                True,
                "mode_cli",
                data={
                    "action": "set",
                    "active_mode": mode,
                    "message": f"Mode set to: {mode}",
                },
            )
        except Exception as e:
            return SkillResult(
                False,
                "mode_cli",
                error=str(e),
                data={"action": "set", "mode": mode},
            )

    def _action_info(self, manager: ModeManager) -> SkillResult:
        """Get detailed information about modes and current state."""
        active = manager.get_active_mode()

        info = {
            "default": {
                "description": "Pure Ollama Agent Mode",
                "allows_ollama": True,
                "allows_claude": False,
                "allows_hybrid": False,
                "use_case": "Cost-effective, privacy-focused execution using local models",
            },
            "adaptive": {
                "description": "Adaptive Mode",
                "allows_ollama": True,
                "allows_claude": True,
                "allows_hybrid": True,
                "use_case": "Optimal routing - chooses best agent type per task",
            },
            "claude-min": {
                "description": "Claude Minimal Mode",
                "allows_ollama": False,
                "allows_claude": True,
                "allows_hybrid": False,
                "use_case": "Cloud-based execution with minimized API costs",
            },
        }

        return SkillResult(
            True,
            "mode_cli",
            data={
                "action": "info",
                "active_mode": active,
                "modes": info,
                "message": f"Mode info retrieved. Current mode: {active}",
            },
        )

    def _show_menu(self) -> SkillResult:
        """Show interactive mode selection menu."""
        menu_script = Path(__file__).parent.parent.parent / "tools" / "menus" / "mode_menu.py"

        if not menu_script.exists():
            return SkillResult(
                False,
                "mode_cli",
                error="Mode menu script not found",
                data={"action": "menu"},
            )

        try:
            subprocess.run([sys.executable, str(menu_script)], check=False)
            return SkillResult(
                True,
                "mode_cli",
                data={
                    "action": "menu",
                    "message": "Mode menu closed",
                },
            )
        except Exception as e:
            return SkillResult(
                False,
                "mode_cli",
                error=f"Failed to launch menu: {str(e)}",
                data={"action": "menu"},
            )
