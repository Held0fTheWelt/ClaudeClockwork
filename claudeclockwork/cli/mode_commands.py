"""CLI commands for mode management: /mode commands."""
from __future__ import annotations

from claudeclockwork.core.mode import ModeManager, ModeViolationError


class ModeCommands:
    """CLI handler for /mode commands."""

    def __init__(self):
        """Initialize mode commands."""
        self.manager = ModeManager()

    def show_current_mode(self) -> str:
        """
        Show the currently active mode.

        Command: /mode show

        Returns:
            Formatted status string
        """
        active_mode = self.manager.get_active_mode()
        config = self.manager.get_mode_config()

        lines = [
            "╔════════════════════════════════════════════╗",
            "║          Active Execution Mode            ║",
            "╚════════════════════════════════════════════╝",
            "",
            f"Mode:        {active_mode.upper()}",
            f"Name:        {config.get('name', '')}",
            "",
            "Constraints:",
        ]

        # Add constraint details
        if not config.get('allow_claude'):
            lines.append("  • Claude execution: FORBIDDEN")
        else:
            lines.append("  • Claude execution: ALLOWED")

        if not config.get('allow_ollama'):
            lines.append("  • Ollama execution: FORBIDDEN")
        else:
            lines.append("  • Ollama execution: ALLOWED")

        if not config.get('allow_mixed'):
            lines.append("  • Mixed execution: FORBIDDEN")
        else:
            lines.append("  • Mixed execution: ALLOWED")

        if config.get('max_token_budget'):
            lines.append(f"  • Token budget: {config['max_token_budget']}")

        if config.get('llm_allowlist'):
            models = ", ".join(config['llm_allowlist'])
            lines.append(f"  • Allowed models: {models}")

        lines.append("")
        lines.append("⚠️  Mode is binding. Cannot be bypassed.")

        return "\n".join(lines)

    def list_available_modes(self) -> str:
        """
        List all available modes.

        Command: /mode list

        Returns:
            Formatted list of modes
        """
        modes = self.manager.list_modes()

        lines = [
            "╔════════════════════════════════════════════╗",
            "║           Available Execution Modes        ║",
            "╚════════════════════════════════════════════╝",
            "",
        ]

        for mode_name, description in modes.items():
            # Show current mode marker
            active = self.manager.get_active_mode()
            marker = "→ " if mode_name == active else "  "

            lines.append(f"{marker}{mode_name}")
            lines.append(f"   {description}")
            lines.append("")

        lines.append("Command: /mode set <mode_name>")

        return "\n".join(lines)

    def set_mode(self, mode_name: str) -> str:
        """
        Change the active execution mode.

        Command: /mode set <mode_name>

        Args:
            mode_name: Name of the mode to activate

        Returns:
            Status message
        """
        current_mode = self.manager.get_active_mode()

        try:
            # Validate mode exists
            is_valid, msg = self.manager.validate_mode(mode_name)
            if not is_valid:
                return f"❌ Error: {msg}\n\nUse '/mode list' to see available modes."

            # Attempt mode change
            self.manager.set_mode(mode_name)

            # Success
            config = self.manager.get_mode_config()
            lines = [
                f"✅ Mode changed: {current_mode} → {mode_name}",
                "",
                f"Name: {config.get('name', '')}",
                f"Description: {config.get('description', '')}",
                "",
                "⚠️  New constraints are active immediately.",
            ]
            return "\n".join(lines)

        except ValueError as e:
            return f"❌ Error: {e}\n\nCheck transition rules with '/mode list'."

    def validate_mode_name(self, mode_name: str) -> str:
        """
        Validate if a mode name is valid.

        Command: /mode validate <mode_name>

        Args:
            mode_name: Mode name to validate

        Returns:
            Status message
        """
        is_valid, msg = self.manager.validate_mode(mode_name)

        if is_valid:
            return f"✅ {msg}"
        else:
            return f"❌ {msg}"

    def get_help(self) -> str:
        """
        Get help for /mode commands.

        Command: /mode help

        Returns:
            Help text
        """
        return """
╔════════════════════════════════════════════╗
║           /mode Command Reference          ║
╚════════════════════════════════════════════╝

COMMANDS:

  /mode show
    Display the currently active mode and its constraints.

  /mode list
    List all available modes with descriptions.

  /mode set <mode_name>
    Change the active mode to <mode_name>.
    Example: /mode set adaptive

  /mode validate <mode_name>
    Check if a mode name is valid.

  /mode help
    Display this help text.

MODES:

  default
    Pure Ollama Agent Mode. No Claude execution.
    Use for cost minimization and offline deployments.

  adaptive
    Claude + Ollama Hybrid Mode. Both allowed, mixed ok.
    Use for flexibility and complex reasoning workflows.

  claude-min
    Cheap Claude Only (Haiku). No Ollama.
    Use for budget-constrained environments.

⚠️  IMPORTANT: Mode is binding and cannot be bypassed.
    All operations are hard-gated by the active mode.
    Only you can change the mode.

For detailed documentation, see .claude/docs/MODE_SYSTEM.md
"""
