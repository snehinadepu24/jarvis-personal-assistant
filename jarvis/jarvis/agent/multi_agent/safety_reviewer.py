from __future__ import annotations

from typing import Any
from jarvis.core.schema import Screen, Step
from jarvis.safety.gate import GateDecision
from jarvis.safety.risk import classify


class SafetyReviewerAgent:
    """Specialist Agent: Audits actions against safety policy, redacts sensitive text, and manages risk tiers."""

    def __init__(self, gate: Any):
        self.gate = gate

    async def review_step(self, step: Step, screen: Screen | None = None) -> GateDecision:
        return await self.gate.approve(step, screen)

    def is_physical_input(self, step: Step) -> bool:
        return step.input_mode == "physical"

