from __future__ import annotations

import json
from pathlib import Path
from jarvis.memory.episodic import EpisodicMemory
from jarvis.memory.procedural import ProceduralMemory
from jarvis.memory.session import SessionMemory
from jarvis.memory.types import EpisodicRecord
from jarvis.memory.user_consistent import UserConsistentMemory
from jarvis.memory.working import WorkingMemory


class MemoryManager:
    """Unified coordinator for all 5 tiers of the JARVIS memory architecture."""

    def __init__(self, data_dir: Path | str, thread_id: str = "default"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.working = WorkingMemory()
        self.session = SessionMemory(thread_id=thread_id)
        self.episodic = EpisodicMemory(self.data_dir / "episodic_memory.db")
        self.user_consistent = UserConsistentMemory(self.data_dir / "user_memory.db")
        self.procedural = ProceduralMemory(self.data_dir / "skills")

    def recall(self, goal: str, app_name: str = "") -> dict:
        """Recall context across all memory tiers for planning."""
        similar_episodes = self.episodic.query_similar(goal, limit=2)
        user_facts = self.user_consistent.list_facts()
        app_pref = self.user_consistent.get_preference("default_view", app_name=app_name) if app_name else None

        return {
            "working_notes": self.working.snapshot()["notes"],
            "session_progress": self.session.text(),
            "similar_episodes": [
                {"goal": e.goal, "status": e.status, "summary": e.summary}
                for e in similar_episodes
            ],
            "user_facts": [{"k": f.key, "v": f.value} for f in user_facts[:5]],
            "app_preference": app_pref,
        }

    def consolidate(
        self,
        task_id: str,
        goal: str,
        status: str,
        summary: str = "",
        steps: list | None = None,
        duration: float = 0.0,
        recovery_count: int = 0,
        error: str = "",
    ) -> None:
        """Consolidate the outcome of a completed task into episodic memory."""
        steps_json = json.dumps(steps or [])
        rec = EpisodicRecord(
            task_id=task_id,
            goal=goal,
            steps_json=steps_json,
            status=status if status in ("done", "failed", "aborted") else "failed",
            summary=summary,
            error=error,
            duration_s=duration,
            recovery_count=recovery_count,
        )
        self.episodic.record_episode(rec)

    def format_prompt_context(self, goal: str, app_name: str = "") -> str:
        ctx = self.recall(goal, app_name=app_name)
        lines = []

        if ctx["user_facts"]:
            lines.append("Relevant User Profile:")
            for f in ctx["user_facts"]:
                lines.append(f"  • {f['k']}: {f['v']}")

        if ctx["similar_episodes"]:
            lines.append("Past Similar Experiences:")
            for e in ctx["similar_episodes"]:
                lines.append(f"  • Goal: {e['goal']} -> {e['status']}: {e['summary']}")

        if ctx["session_progress"]:
            lines.append(f"Current Progress: {ctx['session_progress']}")

        return "\n".join(lines) if lines else ""

