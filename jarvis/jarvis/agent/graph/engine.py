from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any
from jarvis.agent.graph.checkpointer import SqliteCheckpointer
from jarvis.agent.graph.nodes import (
    act_node,
    consolidate_node,
    gate_node,
    interpret_node,
    observe_node,
    plan_node,
    recover_node,
    route_node,
    verify_node,
)
from jarvis.agent.graph.state import AgentState
from jarvis.memory.manager import MemoryManager


class GraphEngine:
    """LangGraph execution engine with checkpointing, HITL suspension, and rewind."""

    def __init__(self, ctx: Any, checkpointer: SqliteCheckpointer, memory_manager: MemoryManager | None = None):
        self.ctx = ctx
        self.checkpointer = checkpointer
        self.memory = memory_manager

    async def run(self, goal: str, thread_id: str | None = None) -> AgentState:
        thread_id = thread_id or f"thread_{uuid.uuid4().hex[:8]}"
        task_id = f"task_{uuid.uuid4().hex[:8]}"

        state: AgentState = {
            "task_id": task_id,
            "thread_id": thread_id,
            "goal": goal,
            "step_no": 0,
            "state": "INTERPRET",
            "route": 2,
            "screen": None,
            "prev_screen": None,
            "status": "running",
            "audit_trail": [],
            "verify_failures": 0,
            "route3_failures": 0,
            "recover_count": 0,
        }

        return await self._step_loop(state)

    async def resume(self, thread_id: str, approved: bool) -> AgentState:
        """Resume an interrupted / suspended graph execution."""
        state_data = self.checkpointer.get(thread_id)
        if not state_data:
            raise KeyError(f"No checkpoint found for thread {thread_id}")

        state: AgentState = state_data
        if approved:
            state["status"] = "running"
            state["interrupt"] = None
            state["state"] = "ACT"
            if state.get("gate_decision"):
                state["gate_decision"].approved = True
            return await self._step_loop(state)
        else:
            state["status"] = "aborted"
            state["summary"] = "User rejected confirmation gate"
            state["state"] = "CONSOLIDATE"
            return await self._step_loop(state)

    async def rewind(self, thread_id: str, steps: int = 1) -> AgentState | None:
        """Time-travel rewind back N checkpoints."""
        return self.checkpointer.rewind(thread_id, steps=steps)

    async def _step_loop(self, state: AgentState) -> AgentState:
        thread_id = state["thread_id"]
        step_idx = 0

        while state.get("status") == "running" and state.get("state") != "FINISHED":
            current_phase = state.get("state")
            chk_id = f"chk_{state.get('step_no', 0)}_{current_phase}_{step_idx}"

            # Persist checkpoint before executing phase
            self.checkpointer.put(thread_id, chk_id, state, metadata={"phase": current_phase})

            if current_phase == "INTERPRET":
                state = await interpret_node(state, self.ctx)
            elif current_phase == "ROUTE":
                state = await route_node(state, self.ctx)
            elif current_phase == "OBSERVE":
                state = await observe_node(state, self.ctx)
            elif current_phase == "DECIDE":
                state = await plan_node(state, self.ctx, self.memory)
            elif current_phase == "GATE":
                state = await gate_node(state, self.ctx)
                if state.get("status") == "suspended":
                    # Save suspended state and return for external user approval
                    self.checkpointer.put(thread_id, f"{chk_id}_suspended", state, metadata={"suspended": True})
                    return state
            elif current_phase == "ACT":
                state = await act_node(state, self.ctx)
            elif current_phase == "VERIFY":
                state = await verify_node(state, self.ctx)
            elif current_phase == "RECOVER":
                state = await recover_node(state, self.ctx)
            elif current_phase == "CONSOLIDATE":
                state = await consolidate_node(state, self.memory)
                break
            else:
                break

            step_idx += 1
            if step_idx > 100:
                state["status"] = "failed"
                state["error"] = "Max graph iteration budget exceeded"
                break

        # Final checkpoint
        self.checkpointer.put(thread_id, f"chk_final_{state.get('status')}", state)
        return state

