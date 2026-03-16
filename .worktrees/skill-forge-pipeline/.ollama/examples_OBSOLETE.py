"""Example usage of TaskExecutorService.

Demonstrates all major features: health checks, task execution, cost tracking, and error handling.
No Flask dependency; runs standalone.

Usage:
    python examples.py [example_name]

Examples:
    python examples.py health
    python examples.py l1_code_draft
    python examples.py l2_architecture
    python examples.py fallback
    python examples.py stats
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from app.services import TaskExecutorService


def example_health_check():
    """Example 1: Check Ollama and budget health."""
    print("\n=== Example 1: Health Check ===\n")

    service = TaskExecutorService()

    if not service.is_available():
        print("❌ TaskExecutor not available")
        print(f"   Error: {TaskExecutorService._init_error}")
        return

    health = service.health_check()

    print("✅ Health Check Results:")
    print(f"  Available: {health.get('available')}")
    print(f"  Ollama Available: {health.get('ollama_available')}")
    print(f"  Budget Status: {health.get('budget_status')}")
    print(f"  Total Cost: ${health.get('total_cost', 0):.2f}")
    print(f"  Total Tokens: {health.get('total_tokens', 0)}")


def example_l1_code_draft():
    """Example 2: L1 task (code drafting) - routes to Ollama."""
    print("\n=== Example 2: L1 Code Drafting (Ollama) ===\n")

    service = TaskExecutorService()

    if not service.is_available():
        print("❌ TaskExecutor not available")
        return

    print("Executing L1 task (code drafting)...")
    print("  Will route to: Ollama (qwen2.5-coder:32b)")
    print("  Expected cost: $0.00")

    result = service.execute_task(
        task_id="example_code_draft",
        escalation_level=1,  # L1: Code drafting
        inputs={
            "prompt": "Write a function that calculates Fibonacci numbers iteratively.",
            "system_prompt": "You are a Python expert. Write clean, well-documented code.",
        },
    )

    print(f"\nResult:")
    print(f"  Success: {result['success']}")
    print(f"  Target Worker: {result['target_worker']}")
    print(f"  Model: {result['model']}")
    print(f"  Cost: {result['cost_formatted']}")
    print(f"  Tokens Used: {result['tokens_used']}")
    print(f"  Latency: {result['latency_ms']:.0f}ms")

    if result["success"]:
        print(f"\nOutput:\n{result['output'][:200]}...")
    else:
        print(f"\nError: {result['error']}")


def example_l2_architecture():
    """Example 3: L2 task (architecture) - routes to Ollama 72B."""
    print("\n=== Example 3: L2 Architecture (Ollama 72B) ===\n")

    service = TaskExecutorService()

    if not service.is_available():
        print("❌ TaskExecutor not available")
        return

    print("Executing L2 task (architecture design)...")
    print("  Will route to: Ollama (qwen2.5:72b)")
    print("  Expected cost: $0.00")

    result = service.execute_task(
        task_id="example_arch_design",
        escalation_level=2,  # L2: Architecture
        inputs={
            "prompt": "Design a caching layer for a high-traffic forum API. Consider cache invalidation, memory limits, TTL strategies, and monitoring.",
        },
        preferred_models=["qwen2.5:72b"],  # Prefer 72B for reasoning
    )

    print(f"\nResult:")
    print(f"  Success: {result['success']}")
    print(f"  Target Worker: {result['target_worker']}")
    print(f"  Model: {result['model']}")
    print(f"  Latency: {result['latency_ms']:.0f}ms")

    if result["success"]:
        print(f"\nArchitecture proposal:\n{result['output'][:300]}...")
    else:
        print(f"\nError: {result['error']}")


def example_fallback_behavior():
    """Example 4: Demonstrate fallback to Claude when Ollama unavailable."""
    print("\n=== Example 4: Fallback to Claude (Simulated) ===\n")

    service = TaskExecutorService()

    if not service.is_available():
        print("❌ TaskExecutor not available")
        print("   (This example requires claudeclockwork installed)")
        return

    print("Executing L1 task with Ollama fallback to Claude...")
    print("  Primary target: Ollama")
    print("  Fallback target: Claude Sonnet (if Ollama unavailable)")

    result = service.execute_task(
        task_id="example_fallback",
        escalation_level=1,
        inputs={"prompt": "Write unit tests for a user authentication module."},
    )

    print(f"\nResult:")
    print(f"  Success: {result['success']}")
    print(f"  Target Worker: {result['target_worker']}")
    print(f"  Model: {result['model']}")
    print(f"  Cost: {result['cost_formatted']}")

    if result["target_worker"] == "ollama":
        print("  ✅ Ollama was available, no fallback needed")
    elif result["target_worker"] == "claude_api":
        print("  ⚠️  Ollama was unavailable, fell back to Claude API")
    else:
        print(f"  ❌ Error: {result['error']}")


def example_cost_tracking():
    """Example 5: Check cumulative cost and token tracking."""
    print("\n=== Example 5: Cost & Token Tracking ===\n")

    service = TaskExecutorService()

    if not service.is_available():
        print("❌ TaskExecutor not available")
        return

    stats = service.get_stats()

    print("Cumulative Stats:")
    print(f"  Total Cost: ${stats.get('total_cost', 0):.2f}")
    print(f"  Total Tokens Used: {stats.get('total_tokens', 0)}")
    print(f"  Token Limit: {stats.get('token_limit', 'unlimited')}")

    remaining = stats.get("token_limit", float("inf")) - stats.get("total_tokens", 0)
    if remaining >= 0:
        print(f"  Tokens Remaining: {remaining}")
    else:
        print(f"  ❌ Token budget exceeded by {abs(remaining)} tokens")


def example_force_ollama():
    """Example 6: Force Ollama mode (no fallback to Claude)."""
    print("\n=== Example 6: Force Ollama (No Fallback) ===\n")

    service = TaskExecutorService()

    if not service.is_available():
        print("❌ TaskExecutor not available")
        return

    print("Executing L1 task with force_ollama=True...")
    print("  Will fail if Ollama is unavailable (no fallback)")

    result = service.execute_task(
        task_id="example_force_ollama",
        escalation_level=1,
        inputs={"prompt": "Explain how REST APIs work."},
        force_ollama=True,  # Strict mode: no fallback
    )

    print(f"\nResult:")
    print(f"  Success: {result['success']}")
    if result["success"]:
        print(f"  ✅ Ollama executed successfully")
        print(f"  Model: {result['model']}")
    else:
        print(f"  ❌ Failed (Ollama unavailable and force_ollama=True)")
        print(f"  Error: {result['error']}")


def main():
    """Run example(s)."""
    examples = {
        "health": example_health_check,
        "l1_code_draft": example_l1_code_draft,
        "l2_architecture": example_l2_architecture,
        "fallback": example_fallback_behavior,
        "stats": example_cost_tracking,
        "force_ollama": example_force_ollama,
    }

    if len(sys.argv) > 1:
        example_name = sys.argv[1]
        if example_name in examples:
            examples[example_name]()
        else:
            print(f"Unknown example: {example_name}")
            print(f"Available: {', '.join(examples.keys())}")
    else:
        print("Running all examples...\n")
        for name, func in examples.items():
            try:
                func()
            except Exception as e:
                print(f"\n⚠️  Example '{name}' failed: {e}")

        print("\n" + "=" * 60)
        print("Run individual examples: python examples.py [name]")
        print("=" * 60)


if __name__ == "__main__":
    main()
