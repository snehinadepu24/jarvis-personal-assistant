from __future__ import annotations

from typing import Any, Literal, TypedDict
from jarvis.actions.base import ActionResult
from jarvis.core.schema import Screen, Step
from jarvis.safety.gate import GateDecision


class AgentState(TypedDict, total=False):
    task_id: str
    thread_id: str
    goal: str
    step_no: int
    state: str  # INTERPRET, ROUTE, OBSERVE, DECIDE, GATE, ACT, VERIFY, RECOVER, CONSOLIDATE, FINISHED
    route: int
    screen: Screen | None
    prev_screen: Screen | None
    intent: dict
    pending: Step | None
    gate_decision: GateDecision | None
    last_action: str
    last_result: str
    verify_failures: int
    route3_failures: int
    recover_count: int
    status: Literal["running", "suspended", "done", "failed", "aborted"]
    summary: str
    error: str
    audit_trail: list[dict]
    interrupt: dict | None  # Contains nonce and confirmation request if suspended

