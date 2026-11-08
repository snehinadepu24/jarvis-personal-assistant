from __future__ import annotations

import time
import uuid
from typing import Any
from jarvis.agent.multi_agent.desktop_specialist import DesktopSpecialistAgent
from jarvis.agent.multi_agent.memory_specialist import MemorySpecialistAgent
from jarvis.agent.multi_agent.safety_reviewer import SafetyReviewerAgent
from jarvis.agent.multi_agent.supervisor import SupervisorAgent
from jarvis.agent.multi_agent.voice_interaction import VoiceInteractionAgent
from jarvis.core.schema import Done, Fail


class MultiAgentCoordinator:
    """Multi-Agent Coordinator orchestrating Supervisor, Desktop, Safety, Memory, and Voice agents."""

    def __init__(
        self,
        supervisor: SupervisorAgent,
        desktop: DesktopSpecialistAgent,
        safety: SafetyReviewerAgent,
        memory: MemorySpecialistAgent,
        voice: VoiceInteractionAgent,
    ):
        self.supervisor = supervisor
        self.desktop = desktop
        self.safety = safety
        self.memory = memory
        self.voice = voice

    async def execute_task(self, goal: str, max_steps: int = 25) -> dict:
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        t0 = time.monotonic()
        steps_history = []

        # 1. Supervisor decomposes task
        subtasks = await self.supervisor.decompose_goal(goal)

        # 2. Memory recall
        memory_ctx = self.memory.format_prompt(goal)

        # 3. Action loop
        step_no = 0
        status = "running"
        summary = ""
        error = ""

        while step_no < max_steps and status == "running":
            step_no += 1

            # Observe desktop
            screen = await self.desktop.observe_surface()

            # Plan next step with Supervisor
            step, usage = await self.supervisor.llm.plan(
                goal,
                memory_ctx,
                step_no,
                max_steps,
                "",
                "",
                screen,
                "",
                f"window: '{screen.window_title}'",
                2,
            )

            # Check if done or fail
            if isinstance(step.action, Done):
                status = "done"
                summary = step.action.summary
                break
            if isinstance(step.action, Fail):
                status = "failed"
                error = step.action.why
                break

            # Safety review
            decision = await self.safety.review_step(step, screen)
            if decision.tier >= 3 and not decision.approved:
                # Ask user confirmation via voice
                approved = await self.voice.request_nonce_confirmation(
                    step.action.type, decision.nonce or "1234"
                )
                if not approved:
                    status = "aborted"
                    error = "User denied Tier 3 confirmation"
                    break

            # Execute via Desktop Specialist
            res = await self.desktop.execute_action(step)
            steps_history.append({
                "step": step_no,
                "action": step.action.type,
                "ok": res.ok,
                "detail": res.detail,
                "input_mode": res.input_mode,
            })

            if not res.ok and step_no >= 3:
                # Ask user for guidance if repeated failure
                continue

        duration = time.monotonic() - t0
        final_status = status if status in ("done", "failed", "aborted") else "failed"

        # Consolidate memory
        self.memory.record_outcome(
            task_id=task_id,
            goal=goal,
            status=final_status,
            summary=summary,
            steps=steps_history,
            duration=duration,
            error=error,
        )

        return {
            "task_id": task_id,
            "status": final_status,
            "steps": step_no,
            "summary": summary,
            "error": error,
            "duration_s": round(duration, 3),
            "history": steps_history,
        }

