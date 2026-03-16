"""
Autonomous agents for the skill-forge pipeline.

This module provides reusable agent implementations that can be invoked by Ollama
or any other system to autonomously execute tasks through the forge pipeline.
"""

from .generic_forge_agent import GenericForgeAgent

__all__ = ["GenericForgeAgent"]
