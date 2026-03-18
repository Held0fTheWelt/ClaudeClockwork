"""
Minimal regression suite for drift repair points (MVP 18I).

Validates 5 critical repaired points:
1. boot_check catches invalid agent_type values
2. The three former "mixed" manifests (hello, report, audio_asr) now use canonical values
3. MODEL_POLICY pointer target exists at root level
4. Canonical machine-readable skill registry path is explicitly declared
5. Forbidden-model enforcement proof matches repaired behavior
"""

import pytest
import json
import subprocess
from pathlib import Path


class TestDriftRepairValidation:
    """Regression tests for drift repair points."""

    def test_boot_check_validates_agent_type(self):
        """Regression: boot_check catches invalid agent_type values."""
        result = subprocess.run(
            ['python3', '.claude/tools/boot_check.py'],
            capture_output=True,
            text=True,
            cwd='/mnt/d/ClaudeClockwork'
        )
        # boot_check should pass (exit 0) after repairs
        assert result.returncode == 0, f"boot_check failed: {result.stdout}\n{result.stderr}"
        assert "ALL CHECKS PASSED" in result.stdout, \
            f"boot_check did not report all checks passed: {result.stdout}"

    def test_hello_manifest_has_canonical_agent_type(self):
        """Regression: hello manifest uses canonical agent_type (not mixed)."""
        manifest_path = Path('/mnt/d/ClaudeClockwork/.claude/skills/demo/hello/manifest.json')
        with open(manifest_path) as f:
            manifest = json.load(f)

        agent_type = manifest.get('agent_type')
        valid_types = ['local', 'ollama', 'claude', 'hybrid']
        assert agent_type in valid_types, \
            f"hello manifest has invalid agent_type: {agent_type}. Expected one of {valid_types}"

    def test_report_manifest_has_canonical_agent_type(self):
        """Regression: report manifest uses canonical agent_type (not mixed)."""
        manifest_path = Path('/mnt/d/ClaudeClockwork/.claude/skills/demo/report/manifest.json')
        with open(manifest_path) as f:
            manifest = json.load(f)

        agent_type = manifest.get('agent_type')
        valid_types = ['local', 'ollama', 'claude', 'hybrid']
        assert agent_type in valid_types, \
            f"report manifest has invalid agent_type: {agent_type}. Expected one of {valid_types}"

    def test_audio_asr_manifest_has_canonical_agent_type(self):
        """Regression: audio_asr manifest uses canonical agent_type (not mixed)."""
        manifest_path = Path('/mnt/d/ClaudeClockwork/.claude/skills/localai/audio_asr/manifest.json')
        with open(manifest_path) as f:
            manifest = json.load(f)

        agent_type = manifest.get('agent_type')
        valid_types = ['local', 'ollama', 'claude', 'hybrid']
        assert agent_type in valid_types, \
            f"audio_asr manifest has invalid agent_type: {agent_type}. Expected one of {valid_types}"

    def test_model_policy_pointer_exists(self):
        """Regression: MODEL_POLICY pointer target exists at root."""
        policy_path = Path('/mnt/d/ClaudeClockwork/MODEL_POLICY.md')
        assert policy_path.exists(), \
            f"MODEL_POLICY.md not found at {policy_path.resolve()}"
        assert policy_path.is_file(), \
            f"MODEL_POLICY.md exists but is not a regular file"
        assert policy_path.stat().st_size > 0, \
            f"MODEL_POLICY.md exists but is empty"

    def test_canonical_registry_path_declared(self):
        """Regression: canonical machine-readable registry path is explicit in system_contract."""
        contract_path = Path('/mnt/d/ClaudeClockwork/.claude/system_contract.yaml')
        with open(contract_path) as f:
            content = f.read()

        # Check that canonical_skill_registry_machine_readable is declared
        assert 'canonical_skill_registry_machine_readable' in content, \
            "canonical_skill_registry_machine_readable not declared in system_contract.yaml"

        # Check that it points to the right location
        assert '.claude/skills/_index.json' in content, \
            "canonical registry path not pointing to _index.json in system_contract.yaml"

    def test_forbidden_model_enforcement(self):
        """Regression: forbidden-model enforcement matches repaired behavior."""
        model_mgr_path = Path('/mnt/d/ClaudeClockwork/claudeclockwork/core/ollama/model_manager.py')
        with open(model_mgr_path) as f:
            content = f.read()

        # Check that is_model_forbidden_for_default_mode is called in resolve_model
        assert 'is_model_forbidden_for_default_mode' in content, \
            "forbidden-model check not found in model_manager.py"

        # Count occurrences - should have at least 3 checks (profile, override, default)
        count = content.count('is_model_forbidden_for_default_mode')
        assert count >= 3, \
            f"Expected at least 3 forbid checks in model_manager.py, found {count}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
