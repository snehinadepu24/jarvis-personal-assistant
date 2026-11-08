from __future__ import annotations

from dataclasses import dataclass, field
from jarvis.memory.types import WorkingMemoryState


class WorkingMemory:
    """Tier 1: Fast in-flight scratchpad for the active execution cycle."""

    def __init__(self, max_notes: int = 15):
        self._state = WorkingMemoryState()
        self.max_notes = max_notes

    def add_note(self, note: str) -> None:
        self._state.notes.append(note.strip())
        if len(self._state.notes) > self.max_notes:
            self._state.notes = self._state.notes[-self.max_notes:]

    def add_diff(self, diff: str) -> None:
        self._state.recent_diffs.append(diff)
        if len(self._state.recent_diffs) > 5:
            self._state.recent_diffs = self._state.recent_diffs[-5:]

    def track_ref(self, ref: str) -> None:
        if ref and ref not in self._state.active_refs:
            self._state.active_refs.append(ref)
            if len(self._state.active_refs) > 20:
                self._state.active_refs = self._state.active_refs[-20:]

    def clear_cycle(self) -> None:
        self._state.active_refs.clear()

    def snapshot(self) -> dict:
        return {
            "notes": list(self._state.notes),
            "recent_diffs": list(self._state.recent_diffs),
            "active_refs": list(self._state.active_refs),
            "loop_count": self._state.loop_count,
        }

    def text_summary(self) -> str:
        return " | ".join(self._state.notes[-6:]) if self._state.notes else "(empty scratchpad)"

