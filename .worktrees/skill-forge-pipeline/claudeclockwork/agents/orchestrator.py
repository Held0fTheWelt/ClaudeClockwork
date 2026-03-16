"""Task orchestrator for autonomous execution."""

from pathlib import Path
from .agents.base_agent import BaseAgent

class TaskOrchestrator:
    """Manages autonomous agent execution."""

    def __init__(self, project_root: Path):
        self.root = project_root
        self.agents = {}
        self.completed = []
        self.failed = []
        self.files_modified = []

    def register_agent(self, name: str, agent_class):
        """Register an agent type."""
        self.agents[name] = agent_class

    def execute_task(self, task):
        """Execute a small autonomous task."""
        agent_type = task.get("agent_type", "generic")

        if agent_type not in self.agents:
            return {"success": False, "error": f"Unknown agent: {agent_type}"}

        agent = self.agents[agent_type](self.root)

        try:
            result = agent.execute(task)
            if result.get("success"):
                self.completed.append(task["id"])
            else:
                self.failed.append(task["id"])
            return result
        except Exception as e:
            self.failed.append(task["id"])
            return {"success": False, "error": str(e)}

    def report(self):
        """Print execution summary."""
        print(f"\nCompleted: {len(self.completed)}")
        print(f"Failed: {len(self.failed)}")
        return len(self.failed) == 0
