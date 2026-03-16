"""Example agent: Simple task executor."""

from claudeclockwork.agents.base_agent import BaseAgent

class ExampleAgent(BaseAgent):
    """Example agent demonstrating autonomous execution."""

    def execute(self, task):
        self.section("Executing Task")
        """Execute the task."""
        print(f"\n  Executing: {task['description']}")

        # Use Ollama to help
        prompt = task.get("prompt", "Hello")
        response = self.run_ollama(prompt)

        # Write result
        output_file = task.get("output", "output.txt")
        self.write_file(output_file, response)

        # Commit
        self.git_add([output_file])
        self.git_commit(f"feat: {task['description']}")

        return {
            "success": True,
            "task_id": task["id"],
            "output_file": output_file,
            "response_length": len(response),
        }
