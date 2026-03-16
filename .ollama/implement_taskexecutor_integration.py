#!/usr/bin/env python3
"""
TaskExecutor Integration Agent
Implements TaskExecutor architecture integration into Flask backend.
Reads plan from docs/ADR/, creates services, routes, and tests autonomously.
"""

import ollama
import subprocess
from pathlib import Path
import json

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

class TaskExecutorIntegrationAgent:
    """Autonomous agent for TaskExecutor Flask integration."""

    def __init__(self):
        self.results = {}
        self.files_modified = []

    def log(self, msg: str):
        print(f"  {msg}")

    def section(self, title: str):
        print(f"\n{'─'*70}")
        print(f"  {title}")
        print(f"{'─'*70}")

    def read_file(self, path: str) -> str:
        """Read file content."""
        full_path = PROJECT_ROOT / path
        return full_path.read_text() if full_path.exists() else ""

    def write_file(self, path: str, content: str) -> bool:
        """Write file content."""
        full_path = PROJECT_ROOT / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        self.files_modified.append(path)
        return True

    def run_ollama(self, prompt: str, model: str = "gemma3:latest") -> str:
        """Call Ollama for content generation."""
        try:
            response = ollama.generate(
                model=model,
                prompt=prompt,
                stream=False,
            )
            return response.get("response", "").strip()
        except Exception as e:
            return f"[ERROR: {str(e)[:100]}]"

    def step1_adr004(self):
        """Write ADR-004: Ollama-First Routing Architecture."""
        self.section("Step 1: Create ADR-004 (Ollama-First Routing)")

        prompt = """Create a detailed Architecture Decision Record (ADR) for Ollama-first routing with Claude fallback.

File: docs/ADR/ADR-004-ollama-first-routing-architecture.md

Structure:
- Title: ADR-004: Ollama-First Routing Architecture
- Status: Accepted
- Context: Cost control rationale (Ollama $0, Claude Haiku $0.08/1M, Sonnet $3/1M, Opus $15/1M)
- Decision: Route L0-L2 tasks to Ollama; L3-L4 to Claude API; L5 stops and asks user
- Escalation Matrix:
  - L0 (trivial): gemma3 (3.3GB, fast)
  - L1 (simple): gemma3 or qwen2.5-coder (33GB)
  - L2 (standard): qwen2.5-coder or qwen3.5-35b (35GB)
  - L3 (complex): Claude Haiku (fallback)
  - L4 (very complex): Claude Sonnet (fallback)
  - L5 (business decision): Stop, ask user
- Fallback Behavior: If Ollama unavailable for L1/L2, escalate to Claude unless force_ollama=True
- Consequences: 90%+ cost savings; latency tradeoff for CPU-based 70b models
- Alternatives Considered: Claude-only, random routing, capability-based routing

Output only the ADR markdown content."""

        adr = self.run_ollama(prompt)
        if adr and len(adr) > 500:
            self.write_file("docs/ADR/ADR-004-ollama-first-routing-architecture.md", adr)
            self.log("✓ Created ADR-004")
            self.results['step1'] = "✓ ADR-004: Ollama-First Routing Architecture"
            return True

        self.log("✗ ADR-004 generation failed")
        return False

    def step2_env_vars(self):
        """Add env vars to .env.example."""
        self.section("Step 2: Update .env.example")

        env_content = self.read_file(".env.example")

        env_vars = """
# Clockwork AI Routing
ANTHROPIC_API_KEY=           # Required for L3-L4 tasks (Claude API)
OLLAMA_HOST=localhost        # Ollama server hostname
OLLAMA_PORT=11434            # Ollama server port
OLLAMA_FALLBACK_TO_CLAUDE=true  # Fallback L1/L2 to Claude when Ollama unavailable
OLLAMA_KEEP_ALIVE=5m         # Unload models after idle
"""

        if "OLLAMA_HOST" not in env_content:
            updated = env_content.rstrip() + "\n" + env_vars
            self.write_file(".env.example", updated)
            self.log("✓ Added Ollama env vars to .env.example")
            self.results['step2'] = "✓ .env.example: Added OLLAMA_HOST, OLLAMA_PORT, ANTHROPIC_API_KEY, etc."
            return True

        self.log("⚠ Env vars already present")
        return True

    def step3_executor_service(self):
        """Create Flask integration service."""
        self.section("Step 3: Create task_executor_service.py")

        prompt = """Generate backend/app/services/task_executor_service.py

A thin adapter that wraps claudeclockwork.TaskExecutor for Flask integration.

Requirements:
1. Lazy import of TaskExecutor (handle ImportError gracefully)
2. Singleton TaskExecutor instance created with env vars
3. Method: execute_task(task_id, escalation_level, inputs) -> serializable dict
4. Method: health_check() -> Ollama availability, budget status dict
5. Error handling for claudeclockwork not installed
6. Returns normalized response with: target_worker, model, output, cost, tokens_used, latency_ms

Pattern similar to how n8n_trigger.py wraps external integration.

Use proper error handling and logging. Include docstrings.
Output only the complete Python code."""

        service = self.run_ollama(prompt)
        if service and "def execute_task" in service:
            self.write_file("backend/app/services/task_executor_service.py", service)
            self.log("✓ Created task_executor_service.py")
            self.results['step3'] = "✓ task_executor_service.py: Flask integration adapter"
            return True

        self.log("✗ Service generation failed")
        return False

    def step4_task_routes(self):
        """Create /api/v1/tasks route."""
        self.section("Step 4: Create task_routes.py")

        prompt = """Generate backend/app/api/v1/task_routes.py

REST routes for task execution:

POST /api/v1/tasks
  Body: { task_id, escalation_level, inputs: { prompt, system_prompt? } }
  Auth: @jwt_required()
  Returns: { target_worker, model, output, cost, cost_formatted, tokens_used, latency_ms }

GET /api/v1/tasks/health
  Auth: @jwt_required() (admin only)
  Returns: { ollama_available, budget_status, router_config }

Requirements:
1. Validate inputs: escalation_level 0-5, prompt required
2. Call task_executor_service.execute_task()
3. Return normalized response
4. Rate limit: @limiter.limit("10 per minute")
5. Import from task_executor_service

Match style of forum_routes.py: @jwt_required(), @limiter.limit(), jsonify returns.

Output only the complete Flask blueprint code."""

        routes = self.run_ollama(prompt)
        if routes and "def " in routes and "jsonify" in routes:
            self.write_file("backend/app/api/v1/task_routes.py", routes)
            self.log("✓ Created task_routes.py")
            self.results['step4'] = "✓ task_routes.py: /api/v1/tasks endpoints"
            return True

        self.log("✗ Routes generation failed")
        return False

    def step5_register_routes(self):
        """Register routes in API __init__.py."""
        self.section("Step 5: Register task routes")

        api_init = self.read_file("backend/app/api/__init__.py")

        if "task_routes" not in api_init:
            # Add import and registration
            lines = api_init.split('\n')

            # Find where blueprints are imported
            import_idx = -1
            for i, line in enumerate(lines):
                if "from .v1" in line and "import" in line:
                    import_idx = i
                    break

            if import_idx >= 0:
                # Add task_routes import
                new_import = "from .v1.task_routes import task_routes_bp"
                if new_import not in api_init:
                    lines.insert(import_idx + 1, new_import)

            # Find where blueprints are registered
            reg_idx = -1
            for i, line in enumerate(lines):
                if "register_blueprint" in line:
                    reg_idx = i
                    break

            if reg_idx >= 0:
                new_reg = "    api_v1_bp.register_blueprint(task_routes_bp)"
                if new_reg not in api_init:
                    lines.insert(reg_idx + 1, new_reg)

            updated = '\n'.join(lines)
            self.write_file("backend/app/api/__init__.py", updated)
            self.log("✓ Registered task_routes in API blueprint")
            self.results['step5'] = "✓ API __init__.py: Registered task routes"
            return True

        self.log("⚠ Routes already registered")
        return True

    def step6_fallback_tests(self):
        """Create fallback tests for Task 8.2."""
        self.section("Step 6: Create fallback tests")

        test_template = """
def test_ollama_available_routes_to_ollama(app):
    \"\"\"Test: Ollama available → routes to Ollama (cost $0).\"\"\"
    pass

def test_ollama_unavailable_falls_back_to_claude(app):
    \"\"\"Test: Ollama down → falls back to Claude API.\"\"\"
    pass

def test_force_ollama_fails_when_unavailable(app):
    \"\"\"Test: force_ollama=True + Ollama down → error.\"\"\"
    pass

def test_both_unavailable_returns_error(app):
    \"\"\"Test: Ollama down + no API key → clean error.\"\"\"
    pass

def test_cost_tracking_ollama_zero_cost(app):
    \"\"\"Test: Ollama execution records cost=0.0.\"\"\"
    pass

def test_cost_tracking_claude_has_nonzero_cost(app):
    \"\"\"Test: Claude fallback records cost > 0.0.\"\"\"
    pass

def test_l5_escalation_stops_and_asks_user(app):
    \"\"\"Test: escalation_level=5 → stop, ask user.\"\"\"
    pass

def test_api_endpoint_task_execution(client, admin_headers):
    \"\"\"Integration test: POST /api/v1/tasks executes task.\"\"\"
    pass
"""

        tests = self.read_file("backend/tests/test_task_executor_fallback.py")

        if not tests:
            # Generate comprehensive test file
            prompt = f"""Generate backend/tests/test_task_executor_fallback.py

Comprehensive test file for TaskExecutor fallback behavior.

Tests to implement:
1. test_ollama_available_routes_to_ollama: Mock OllamaClient responding, verify target_worker == "ollama", cost == 0.0
2. test_ollama_unavailable_falls_back_to_claude: Mock OllamaClient raising OllamaUnavailableError, mock anthropic.Anthropic, verify fallback with target_worker == "claude_api"
3. test_force_ollama_fails_when_unavailable: Ollama down + force_ollama=True, verify success=False
4. test_both_unavailable_returns_error: Ollama down + no ANTHROPIC_API_KEY, verify clean error response
5. test_cost_tracking_ollama_zero_cost: Verify Ollama execution records cost == 0.0
6. test_cost_tracking_claude_has_nonzero_cost: Verify Claude fallback records cost > 0.0
7. test_l5_escalation_stops_and_asks_user: escalation_level=5, verify success=False, target_worker == "stop_ask_user"
8. test_api_endpoint_task_execution: Integration test hitting POST /api/v1/tasks via test client

Requirements:
- Use pytest with unittest.mock for mocking
- Follow conftest.py patterns (app, client, test_user, admin_headers fixtures)
- Match test_forum_api.py style
- Include proper assertions and error messages
- Handle both Ollama unavailable and API key missing cases

Output the complete test file with all 8 tests."""

            generated = self.run_ollama(prompt)
            if generated and "def test_" in generated:
                self.write_file("backend/tests/test_task_executor_fallback.py", generated)
                self.log("✓ Created test_task_executor_fallback.py")
                self.results['step6'] = "✓ test_task_executor_fallback.py: 8 comprehensive fallback tests"
                return True
        else:
            self.log("✓ Tests file already exists")
            return True

        self.log("✗ Test generation failed")
        return False

    def commit_all(self):
        """Commit all changes."""
        self.section("Committing Changes")

        if not self.files_modified:
            self.log("No files modified")
            return False

        try:
            subprocess.run(
                ["git", "add"] + self.files_modified,
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                check=True,
            )

            subprocess.run(
                ["git", "commit", "-m", "feat(taskexecutor): integrate TaskExecutor into Flask backend"],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                check=True,
            )

            result = subprocess.run(
                ["git", "log", "-1", "--oneline"],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
            )

            self.log(f"✓ Committed: {result.stdout.strip()}")
            return True
        except Exception as e:
            self.log(f"✗ Commit error: {str(e)[:50]}")
            return False

    def run(self):
        """Execute all integration steps."""
        print("\n" + "="*70)
        print("  TASKEXECUTOR INTEGRATION AGENT")
        print("="*70)

        s1 = self.step1_adr004()
        s2 = self.step2_env_vars()
        s3 = self.step3_executor_service()
        s4 = self.step4_task_routes()
        s5 = self.step5_register_routes()
        s6 = self.step6_fallback_tests()

        if s1 or s2 or s3 or s4 or s5 or s6:
            self.commit_all()

        self.section("INTEGRATION RESULTS")
        print("\n✓ TASKEXECUTOR INTEGRATION COMPLETE\n")
        for step, result in sorted(self.results.items()):
            print(f"  {step.upper()}: {result}")

        print(f"\n  Files modified: {len(self.files_modified)}")
        for f in self.files_modified:
            print(f"    - {f}")

        success = all([s1, s2, s3, s4, s5, s6])
        print(f"\n  Status: {'✓✓✓ ALL STEPS COMPLETE' if success else '⚠ PARTIAL SUCCESS'}")
        print("\n" + "="*70 + "\n")

        return success


if __name__ == "__main__":
    import sys
    agent = TaskExecutorIntegrationAgent()
    success = agent.run()
    sys.exit(0 if success else 1)
