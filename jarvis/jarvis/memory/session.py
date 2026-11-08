from __future__ import annotations

import time
from dataclasses import dataclass, field
from jarvis.memory.types import SessionCheckpoint

MAX_SESSION_WORDS = 150


class SessionMemory:
    """Tier 2: Short-term thread memory, turn trajectory, and goal stack."""

    def __init__(self, thread_id: str = "default"):
        self.thread_id = thread_id
        self._goals_stack: list[str] = []
        self._facts: list[str] = []
        self._checkpoints: list[SessionCheckpoint] = []
        self._last_rewrite = 0

    def push_goal(self, goal: str) -> None:
        self._goals_stack.append(goal)

    def pop_goal(self) -> str | None:
        return self._goals_stack.pop() if self._goals_stack else None

    @property
    def current_goal(self) -> str:
        return self._goals_stack[-1] if self._goals_stack else ""

    def add(self, fact: str) -> None:
        self._facts.append(fact)
        self._facts = self._facts[-16:]

    def text(self) -> str:
        prefix = f"Goal Stack: {' -> '.join(self._goals_stack)} | " if self._goals_stack else ""
        return (prefix + " ".join(self._facts))[-1600:]

    def condense(self, step_no: int) -> None:
        if step_no - self._last_rewrite >= 5 and len(self._facts) > 3:
            seen, out = set(), []
            for f in self._facts:
                k = f.lower()[:60]
                if k not in seen:
                    seen.add(k)
                    out.append(f)
            self._facts = out[-8:]
            self._last_rewrite = step_no

    def words(self) -> int:
        return len(self.text().split())

    def record_checkpoint(self, checkpoint: SessionCheckpoint) -> None:
        self._checkpoints.append(checkpoint)

    def get_recent_checkpoints(self, count: int = 5) -> list[SessionCheckpoint]:
        return self._checkpoints[-count:]

