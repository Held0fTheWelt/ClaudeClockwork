"""Mode system audit and self-check tool."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from .mode_manager import ModeManager
from .mode_validator import ModeMetadataValidator


class ModeAudit:
    """Self-check tooling for mode system integrity."""

    def __init__(self):
        """Initialize audit tool."""
        self.manager = ModeManager()
        self.validator = ModeMetadataValidator()

    def audit_mode_system(self) -> dict[str, Any]:
        """
        Run comprehensive audit of mode system.

        Returns:
            Audit report dict
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "active_mode": self.manager.get_active_mode(),
            "checks": {},
            "status": "UNKNOWN"
        }

        # Check 1: Mode state validity
        state_valid, state_errors = self.validator.validate_mode_state()
        report["checks"]["mode_state"] = {
            "status": "PASS" if state_valid else "FAIL",
            "errors": state_errors
        }

        # Check 2: Mode config completeness
        try:
            config = self.manager.get_mode_config()
            config_valid = all(k in config for k in [
                "allow_claude", "allow_ollama", "allow_mixed", "require_ollama_available"
            ])
            report["checks"]["mode_config"] = {
                "status": "PASS" if config_valid else "FAIL",
                "fields": list(config.keys())
            }
        except Exception as e:
            report["checks"]["mode_config"] = {
                "status": "FAIL",
                "error": str(e)
            }

        # Check 3: Mode constraints enforcement
        active_mode = self.manager.get_active_mode()
        constraints_ok = True
        constraint_issues = []

        if active_mode == "default":
            if not self._check_default_mode_constraints():
                constraints_ok = False
                constraint_issues.append("default mode constraint violation")
        elif active_mode == "adaptive":
            if not self._check_adaptive_mode_constraints():
                constraints_ok = False
                constraint_issues.append("adaptive mode constraint violation")
        elif active_mode == "claude-min":
            if not self._check_claude_min_constraints():
                constraints_ok = False
                constraint_issues.append("claude-min mode constraint violation")

        report["checks"]["mode_constraints"] = {
            "status": "PASS" if constraints_ok else "FAIL",
            "issues": constraint_issues
        }

        # Check 4: Persistent state integrity
        state_ok = True
        state_issues = []

        try:
            # State file should exist and be readable
            if not ModeManager.STATE_FILE.exists():
                state_ok = False
                state_issues.append("state file does not exist")
        except Exception as e:
            state_ok = False
            state_issues.append(f"state file error: {str(e)}")

        report["checks"]["persistent_state"] = {
            "status": "PASS" if state_ok else "FAIL",
            "issues": state_issues
        }

        # Overall status
        all_checks_pass = all(
            check["status"] == "PASS"
            for check in report["checks"].values()
        )
        report["status"] = "PASS" if all_checks_pass else "FAIL"

        return report

    def _check_default_mode_constraints(self) -> bool:
        """Check default mode has correct constraints."""
        config = self.manager.get_mode_config("default")
        return (
            config.get("allow_ollama") is True and
            config.get("allow_claude") is False and
            config.get("allow_mixed") is False and
            config.get("require_ollama_available") is True
        )

    def _check_adaptive_mode_constraints(self) -> bool:
        """Check adaptive mode has correct constraints."""
        config = self.manager.get_mode_config("adaptive")
        return (
            config.get("allow_ollama") is True and
            config.get("allow_claude") is True and
            config.get("allow_mixed") is True
        )

    def _check_claude_min_constraints(self) -> bool:
        """Check claude-min mode has correct constraints."""
        config = self.manager.get_mode_config("claude-min")
        return (
            config.get("allow_ollama") is False and
            config.get("allow_claude") is True and
            config.get("allow_mixed") is False and
            "claude-haiku-4-5" in config.get("llm_allowlist", [])
        )

    def audit_manifest_compliance(self, manifests: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Audit all skill manifests for mode compliance.

        Args:
            manifests: List of skill manifests

        Returns:
            Compliance report
        """
        report = self.validator.validate_all_manifests(manifests)
        report["timestamp"] = datetime.now().isoformat()
        report["mode"] = self.manager.get_active_mode()
        return report

    def get_mode_status(self) -> dict[str, Any]:
        """
        Get current mode status for reporting.

        Returns:
            Mode status dict
        """
        from .mode_guard import ModeGuard
        guard = ModeGuard(self.manager)
        return guard.get_mode_status()

    def export_audit_report(self) -> str:
        """
        Export human-readable audit report.

        Returns:
            Formatted audit report
        """
        audit = self.audit_mode_system()

        lines = [
            "╔════════════════════════════════════════════╗",
            "║         Mode System Audit Report           ║",
            "╚════════════════════════════════════════════╝",
            "",
            f"Timestamp: {audit['timestamp']}",
            f"Active Mode: {audit['active_mode']}",
            f"Status: {audit['status']}",
            "",
            "Checks:",
        ]

        for check_name, check_result in audit['checks'].items():
            status = check_result['status']
            symbol = "✅" if status == "PASS" else "❌"
            lines.append(f"  {symbol} {check_name}: {status}")

            if status == "FAIL" and 'errors' in check_result:
                for error in check_result['errors']:
                    lines.append(f"     → {error}")
            if status == "FAIL" and 'issues' in check_result:
                for issue in check_result['issues']:
                    lines.append(f"     → {issue}")

        lines.append("")
        lines.append("⚠️  Mode is binding. Report any audit failures immediately.")

        return "\n".join(lines)
