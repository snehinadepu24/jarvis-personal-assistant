from __future__ import annotations

import inspect
import time
from typing import Any
from jarvis.actions.base import ActionResult
from jarvis.actions.verify import verify_step
from jarvis.agent.graph.state import AgentState
from jarvis.core.schema import Done, Fail, Screen, Step
from jarvis.perception.diff import screen_diff
from jarvis.perception.router import choose_route, uia_confidence
from jarvis.perception.serialize import serialize_screen


async def interpret_node(state: AgentState, ctx: Any) -> AgentState:
    state["intent"] = await ctx.llm.intent(state["goal"])
    state["state"] = "ROUTE"
    return state


async def route_node(state: AgentState, ctx: Any) -> AgentState:
    pending = None
    if getattr(ctx, "tool_registry", None) is not None:
        pending = ctx.tool_registry.match(state.get("intent", {}))
        if pending is not None:
            state["step_no"] = state.get("step_no", 0) + 1
            state["pending"] = pending
            state["state"] = "GATE"
            return state

    state["state"] = "OBSERVE"
    return state


async def observe_node(state: AgentState, ctx: Any) -> AgentState:
    screen = state.get("screen")
    conf = uia_confidence(screen) if screen else 1.0
    route, _ = choose_route(
        conf,
        verify_failures=state.get("verify_failures", 0),
        route3_failures=state.get("route3_failures", 0),
        allow_vlm=getattr(ctx, "allow_vlm", False),
    )
    state["route"] = route

    if hasattr(ctx.backend, "wait_idle"):
        await ctx.backend.wait_idle()

    state["prev_screen"] = screen
    obs = ctx.backend.observe(route)
    scr = await obs if inspect.isawaitable(obs) else obs
    if scr is not None:
        scr.ensure_snapshot_id()
    state["screen"] = scr
    state["state"] = "DECIDE"
    return state


async def plan_node(state: AgentState, ctx: Any, memory_manager: Any = None) -> AgentState:
    state["step_no"] = state.get("step_no", 0) + 1
    screen = state.get("screen")
    prev_screen = state.get("prev_screen")

    diff_line = screen_diff(prev_screen, screen).line() if screen else "(none)"
    win_line = f"window: '{screen.window_title}' ({screen.app})" if screen else "(none)"

    # Include memory recall context if available
    memory_text = ""
    if memory_manager:
        memory_text = memory_manager.format_prompt_context(state["goal"], screen.app if screen else "")
    elif hasattr(ctx, "memory") and hasattr(ctx.memory, "text"):
        memory_text = ctx.memory.text()

    step, usage = await ctx.llm.plan(
        state["goal"],
        memory_text,
        state["step_no"],
        ctx.budgets.steps,
        state.get("last_action", ""),
        state.get("last_result", ""),
        screen,
        diff_line,
        win_line,
        state.get("route", 2),
    )

    # Attach current snapshot_id to step
    if screen:
        step.snapshot_id = screen.snapshot_id

    state["pending"] = step
    state["state"] = "GATE"
    return state


async def gate_node(state: AgentState, ctx: Any) -> AgentState:
    step = state.get("pending")
    screen = state.get("screen")
    decision = await ctx.gate.approve(step, screen)
    state["gate_decision"] = decision

    if decision.tier >= 3 and not decision.approved:
        # Emit interrupt state for HITL nonce confirmation
        state["status"] = "suspended"
        state["interrupt"] = {
            "tier": decision.tier,
            "nonce": decision.nonce,
            "reason": decision.reason,
            "action": step.action.type,
            "summary": f"Tier {decision.tier} action requires confirmation: {step.action.type}",
        }
        return state

    if decision.approved:
        state["state"] = "ACT"
    else:
        state["state"] = "RECOVER"
    return state


async def act_node(state: AgentState, ctx: Any) -> AgentState:
    step = state.get("pending")
    screen = state.get("screen")

    result: ActionResult = await ctx.executor.apply(step, screen=screen)
    state["last_action"] = f"{step.action.type} {step.action.model_dump(exclude={'type', 'reason'})}"
    state["last_result"] = f"{'ok' if result.ok else 'fail'}: {result.detail}"

    audit_entry = {
        "step": state["step_no"],
        "action": step.action.type,
        "input_mode": result.input_mode,
        "ok": result.ok,
        "detail": result.detail,
        "snapshot_id": getattr(screen, "snapshot_id", ""),
    }
    state.setdefault("audit_trail", []).append(audit_entry)

    state["state"] = "VERIFY"
    return state


async def verify_node(state: AgentState, ctx: Any) -> AgentState:
    step = state.get("pending")
    a = step.action

    if state.get("last_result", "").startswith("fail:"):
        state["verify_failures"] = state.get("verify_failures", 0) + 1
        state["state"] = "RECOVER"
        return state

    if isinstance(a, Done):
        state["status"] = "done"
        state["summary"] = a.summary
        state["state"] = "CONSOLIDATE"
        return state

    if isinstance(a, Fail):
        state["status"] = "failed"
        state["error"] = a.why
        state["state"] = "CONSOLIDATE"
        return state

    v = await verify_step(step, state.get("prev_screen"), state.get("screen"), ctx.backend, ctx.executor)
    if v.ok:
        state["verify_failures"] = 0
        state["recover_count"] = 0
        state["state"] = "OBSERVE"
    else:
        state["verify_failures"] = state.get("verify_failures", 0) + 1
        state["state"] = "RECOVER"
    return state


async def recover_node(state: AgentState, ctx: Any) -> AgentState:
    rec_count = state.get("recover_count", 0) + 1
    state["recover_count"] = rec_count

    if rec_count > 3:
        state["status"] = "failed"
        state["error"] = "Max recovery attempts exceeded"
        state["state"] = "CONSOLIDATE"
        return state

    if state.get("route", 2) < 3:
        state["route"] = 3
        state["route3_failures"] = state.get("route3_failures", 0) + 1

    state["state"] = "OBSERVE"
    return state


async def consolidate_node(state: AgentState, memory_manager: Any = None) -> AgentState:
    if memory_manager:
        memory_manager.consolidate(
            task_id=state.get("task_id", f"task_{int(time.time())}"),
            goal=state["goal"],
            status=state.get("status", "done"),
            summary=state.get("summary", ""),
            steps=state.get("audit_trail", []),
            recovery_count=state.get("recover_count", 0),
            error=state.get("error", ""),
        )
    state["state"] = "FINISHED"
    return state

