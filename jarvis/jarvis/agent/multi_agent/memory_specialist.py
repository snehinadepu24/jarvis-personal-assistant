from __future__ import annotations

from typing import Any
from jarvis.memory.manager import MemoryManager


class MemorySpecialistAgent:
    """Specialist Agent: Queries episodic experiences, user facts, and consolidates session knowledge."""

    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    def recall_context(self, goal: str, app_name: str = "") -> dict:
        return self.memory.recall(goal, app_name=app_name)

    def format_prompt(self, goal: str, app_name: str = "") -> str:
        return self.memory.format_prompt_context(goal, app_name=app_name)

    def record_outcome(
        self,
        task_id: str,
        goal: str,
        status: str,
        summary: str = "",
        steps: list | None = None,
        duration: float = 0.0,
        error: str = "",
    ) -> None:
        self.memory.consolidate(
            task_id=task_id,
            goal=goal,
            status=status,
            summary=summary,
            steps=steps,
            duration=duration,
            error=error,
        )

