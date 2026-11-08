from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SubTask:
    id: str
    description: str
    target_specialist: str  # desktop, safety, memory, interaction
    status: str = "pending"
    result: Any = None


class SupervisorAgent:
    """Orchestrator: Decomposes complex user commands, budgets resources, and delegates to specialists."""

    def __init__(self, llm: Any, budgets: Any):
        self.llm = llm
        self.budgets = budgets

    async def decompose_goal(self, goal: str, context: str = "") -> list[SubTask]:
        """Decompose a high-level goal into specialist subtasks."""
        # Standard decomposition for desktop tasks
        subtasks = [
            SubTask(id="task_mem", description=f"Recall past experiences and user facts for: {goal}", target_specialist="memory"),
            SubTask(id="task_desktop", description=goal, target_specialist="desktop"),
            SubTask(id="task_audit", description="Review safety and policy compliance", target_specialist="safety"),
        ]
        return subtasks

    def summarize_outcome(self, goal: str, subtasks: list[SubTask]) -> str:
        completed = [t for t in subtasks if t.status == "completed"]
        return f"Completed {len(completed)}/{len(subtasks)} subtasks for goal: {goal}"

