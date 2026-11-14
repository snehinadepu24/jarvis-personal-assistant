from __future__ import annotations

import asyncio
import inspect
import time
from dataclasses import dataclass, field
from typing import Callable

from jarvis.actions.base import ActionResult
from jarvis.agent.budgets import BudgetExceeded, Budgets, check_budget
from jarvis.agent.loop_detect import LoopDetector
from jarvis.agent.memory import ProgressMemory
from jarvis.core.schema import Done, Fail, Screen, Step
from jarvis.llm.base import TaskUsage
from jarvis.perception.router import choose_route, uia_confidence
from jarvis.safety.audit import Audit

STOP_WORDS = {"stop", "cancel", "abort", "quit", "exit"}


@dataclass
class TaskOutcome:
    status: str
    summary: str = ""
    steps: int = 0
    error: str = ""
    checker: dict = field(default_factory=dict)
    metrics: dict = field(default_factory=dict)


@dataclass
class AgentContext:
    llm: object
    backend: object
    executor: object
    gate: object
    audit: Audit
    budgets: Budgets
    task_name: str = "task"
    cancel: asyncio.Event = field(default_factory=asyncio.Event)
    allow_connectors: bool = True
    allow_vlm: bool = False
    voice_ask: Callable = None
    tools_description: str = "(none registered)"
    trace: list = field(default_factory=list)
    tool_registry: object | None = None
    on_event: Callable | None = None
    snapshot_manager: object | None = None  # NEW: snapshot manager for stale reference detection
    background_executor: object | None = None  # NEW: background execution mode
    navigation_strategy: object | None = None  # NEW: complex navigation handler


class TaskState:
    def __init__(self, goal: str):
        self.goal = goal
        self.intent: dict = {}
        self.screen: Screen | None = None
        self.prev_screen: Screen | None = None
        self.pending: Step | None = None
        self.route = 2
        self.step_no = 0
        self.verify_failures = 0
        self.route3_failures = 0
        self.recover_count = 0
        self.usage = TaskUsage()
        self.memory = ProgressMemory()
        self.loop = LoopDetector()
        self.confirmations_shown = 0
        self.unsafe_blocked = 0
        self.bytes_offdevice = 0
        self.t0 = time.monotonic()
        self.last_action = ""
        self.last_result = ""

    def metrics(self) -> dict:
        return {
            "steps": self.step_no,
            "llm_calls": self.usage.calls,
            "tokens": self.usage.usage.input_tokens + self.usage.usage.output_tokens,
            "usd": round(self.usage.usage.usd, 6),
            "vlm_calls": self.usage.vlm_calls,
            "bytes_offdevice": self.bytes_offdevice,
            "confirmations_shown": self.confirmations_shown,
            "unsafe_blocked": self.unsafe_blocked,
            "elapsed_s": round(time.monotonic() - self.t0, 3),
        }


def _window_line(st: TaskState, confidence: float) -> str:
    from jarvis.core.prompts import window_line

    return window_line(st.screen or Screen(app="", window_title="", elements=[]), st.route, confidence)


def _diff_line(st: TaskState) -> str:
    from jarvis.perception.diff import screen_diff

    return screen_diff(st.prev_screen, st.screen).line() if st.screen else "(none)"


def _route_str(route: int) -> str:
    return {1: "connector", 2: "uia", 3: "ocr+detector", 4: "vlm"}.get(route, f"route{route}")


async def run_task(goal: str, ctx: AgentContext) -> TaskOutcome:
    print(f"[JARVIS STATE MACHINE] Starting run_task for goal: {goal}", flush=True)
    st = TaskState(goal)
    state = "INTERPRET"

    async def _notify(ev_type: str, data: dict):
        if getattr(ctx, "on_event", None) is not None:
            try:
                res = ctx.on_event(ev_type, data)
                if inspect.isawaitable(res):
                    await res
            except Exception as e:
                print(f"[JARVIS EVENT ERROR] {e}", flush=True)

    def finish(status: str, summary: str = "", error: str = "") -> TaskOutcome:
        out = TaskOutcome(status=status, summary=summary, steps=st.step_no, error=error, checker={}, metrics=st.metrics())
        ctx.audit.log(task=ctx.task_name, step=st.step_no, route=_route_str(st.route), result=f"outcome:{status}", window=st.screen.window_title if st.screen else "")
        if getattr(ctx, "on_event", None) is not None:
            try:
                ev = "task.completed" if status == "done" else ("task.cancelled" if status == "aborted" else "task.failed")
                res = ctx.on_event(ev, {"status": status, "summary": summary, "error": error, "steps": st.step_no, "metrics": st.metrics()})
                if inspect.isawaitable(res):
                    asyncio.create_task(res)
            except Exception:
                pass
        return out

    await _notify("task.started", {"goal": goal, "task_name": ctx.task_name})
    print(f"[JARVIS STATE MACHINE] Task started event sent, entering main loop", flush=True)

    while not ctx.cancel.is_set():
        try:
            check_budget(
                ctx.budgets,
                steps=st.step_no, llm_calls=st.usage.calls,
                usd=st.usage.usage.usd, seconds=time.monotonic() - st.t0,
                vlm=st.usage.vlm_calls,
            )
        except BudgetExceeded as e:
            return finish("failed", error=f"budget: {e}")

        try:
            print(f"[JARVIS STATE MACHINE] State: {state}, Step: {st.step_no}", flush=True)
            if state == "INTERPRET":
                print(f"[JARVIS STATE MACHINE] Calling LLM.intent()...", flush=True)
                st.intent = await ctx.llm.intent(goal)
                print(f"[JARVIS INTENT] {st.intent}", flush=True)
                state = "ROUTE"
            elif state == "ROUTE":
                st.pending = None
                if getattr(ctx, "tool_registry", None) is not None:
                    st.pending = ctx.tool_registry.match(st.intent)
                    if st.pending is not None:
                        st.step_no += 1
                state = "GATE" if st.pending is not None else "OBSERVE"
            elif state == "OBSERVE":
                conf = uia_confidence(st.screen) if st.screen else 1.0
                route, why = choose_route(
                    conf if st.screen else 1.0,
                    verify_failures=st.verify_failures,
                    route3_failures=st.route3_failures,
                    allow_vlm=ctx.allow_vlm,
                )
                st.route = route
                await ctx.backend.wait_idle()
                st.prev_screen = st.screen
                obs = ctx.backend.observe(route)
                st.screen = await obs if inspect.isawaitable(obs) else obs
                
                # Create snapshot if snapshot_manager is available
                if hasattr(ctx, 'snapshot_manager') and ctx.snapshot_manager and st.screen:
                    ctx.snapshot_manager.create_snapshot(st.screen)
                
                state = "DECIDE"
            elif state == "DECIDE":
                st.step_no += 1
                from jarvis.perception.serialize import serialize_screen

                screenshot = None
                if st.route == 4 and hasattr(ctx.backend, "screenshot_bytes"):
                    screenshot = await ctx.backend.screenshot_bytes()
                step, usage = await ctx.llm.plan(
                    goal, st.memory.text(), st.step_no, ctx.budgets.steps,
                    st.last_action, st.last_result, st.screen,
                    _diff_line(st), _window_line(st, uia_confidence(st.screen)), st.route,
                    screenshot=screenshot,
                )
                print(
                    f"[JARVIS PLAN] step={st.step_no} thought={step.thought!r} "
                    f"action={step.action.model_dump()} expect={step.expect!r}",
                    flush=True,
                )
                if usage.model and usage.model != "scripted":
                    st.usage.record(usage)
                    ctx.audit.log(task=ctx.task_name, step=st.step_no, route=_route_str(st.route), action="plan", model=usage.model, tokens=usage.input_tokens + usage.output_tokens, usd=usage.usd)
                else:
                    ctx.audit.log(task=ctx.task_name, step=st.step_no, route=_route_str(st.route), action="plan", model="scripted")
                st.pending = step
                await _notify("task.progress", {
                    "step": st.step_no,
                    "thought": step.thought,
                    "action": step.action.model_dump(),
                    "expect": step.expect,
                })
                state = "GATE"
            elif state == "GATE":
                print(f"[JARVIS GATE] Entering GATE for action type: {st.pending.action.type}, screen: {'present' if st.screen else 'None'}", flush=True)
                decision = await ctx.gate.approve(st.pending, st.screen)
                if decision.tier >= 3:
                    st.confirmations_shown += 1
                print(
                    f"[JARVIS DECISION] approved={decision.approved} tier={decision.tier} "
                    f"reason={decision.reason}",
                    flush=True,
                )
                ctx.audit.log(
                    task=ctx.task_name, step=st.step_no, route=_route_str(st.route), tier=decision.tier,
                    action=st.pending.action.type, target_key=decision.action_hash or "",
                    window=st.screen.window_title if st.screen else "", approved_by="user" if decision.approved and decision.tier >= 3 else ("auto" if decision.approved else "denied"),
                    result="approved" if decision.approved else "denied",
                )
                if decision.approved:
                    print(f"[JARVIS GATE] Action approved, transitioning to ACT (action type: {st.pending.action.type})", flush=True)
                    state = "ACT"
                elif st.pending.action.type == "ask_user":
                    state = "ACT"
                else:
                    st.unsafe_blocked += 1 if decision.tier >= 4 else 0
                    st.memory.add(f"user denied {st.pending.action.type} (tier {decision.tier})")
                    state = "ASK"
            elif state == "ACT":
                await _notify("action.started", {
                    "action": st.pending.action.model_dump(),
                    "window": st.screen.window_title if st.screen else "",
                })
                result: ActionResult = await ctx.executor.apply(st.pending, st.screen)
                st.last_action = f"{st.pending.action.type} {st.pending.action.model_dump(exclude={'type', 'reason'})}"
                st.last_result = f"{'ok' if result.ok else 'fail'}: {result.detail}"
                print(
                    f"[JARVIS ACTION] {st.last_action} -> {st.last_result}",
                    flush=True,
                )
                await _notify("action.completed", {
                    "action": st.pending.action.model_dump(),
                    "result": st.last_result,
                    "ok": result.ok,
                })
                if st.screen:
                    st.loop.record(st.screen.window_title, st.pending.action.type, st.pending.action.model_dump().get("mark", ""), st.pending.action.model_dump().get("text", ""))
                ctx.audit.log(task=ctx.task_name, step=st.step_no, route=_route_str(st.route), action=st.pending.action.type, target_key="", window=st.screen.window_title if st.screen else "", result=st.last_result[:200])
                state = "VERIFY"
            elif state == "VERIFY":
                a = st.pending.action
                if st.last_result.startswith("fail:"):
                    st.verify_failures += 1
                    print(f"[JARVIS VERIFY] action failed; recovering: {st.last_result}", flush=True)
                    state = "RECOVER"
                    continue
                if isinstance(a, (Done, Fail)):
                    ctx.trace.append({
                        "thought": st.pending.thought, "expect": st.pending.expect,
                        "action": a.model_dump(), "select": {},
                    })
                    if isinstance(a, Done):
                        print(f"[JARVIS TASK] completed: {a.summary}", flush=True)
                        return finish("done", summary=a.summary)
                    print(f"[JARVIS TASK] failed: {a.why}", flush=True)
                    return finish("failed", error=a.why)
                from jarvis.actions.verify import verify_step

                v = await verify_step(st.pending, st.prev_screen, st.screen, ctx.backend, ctx.executor)
                st.loop.note_diff(v.diff_empty)
                if v.ok:
                    st.verify_failures = 0
                    st.recover_count = 0
                    el = st.screen.by_mark(a.mark) if hasattr(a, "mark") and getattr(a, "mark", None) else None
                    ctx.trace.append({
                        "thought": st.pending.thought,
                        "expect": st.pending.expect,
                        "action": a.model_dump(exclude={"mark"}) if el else a.model_dump(),
                        "select": el.selector[0] if el and el.selector else {},
                    })
                    st.memory.add(st.last_action[:150])
                    st.memory.condense(st.step_no)
                    state = "OBSERVE"
                else:
                    st.verify_failures += 1
                    state = "RECOVER"
            elif state == "RECOVER":
                st.recover_count += 1
                if st.loop.should_recover():
                    st.loop.reset()
                    if st.route == 2:
                        st.route3_failures += 1
                        st.route = 3
                if st.recover_count > 2:
                    st.recover_count = 0
                    if st.route < 3:
                        st.route3_failures += 1
                        st.route = 3
                    else:
                        state = "ASK"
                        continue
                state = "OBSERVE"
            elif state == "ASK":
                question = f"Action denied or failed: {st.last_result or st.pending.action.type if st.pending else 'unknown'}. How should I proceed? (answer or 'stop')"
                reply = await _ask(ctx, question)
                if reply.strip().lower() in STOP_WORDS:
                    return finish("aborted", summary="user said stop")
                state = "OBSERVE"
        except Exception as e:
            from jarvis.core.schema import AskUserPending
            from jarvis.llm.router import PlanError

            if isinstance(e, AskUserPending):
                reply = await _ask(ctx, e.question)
                if reply.strip().lower() in STOP_WORDS:
                    return finish("aborted", summary="user said stop")
                state = "OBSERVE"
                continue
            if isinstance(e, PlanError) and e.marker == "invalid_mark":
                st.recover_count += 1
                print(
                    f"[JARVIS RECOVERY] invalid UI mark; refreshing screen "
                    f"(attempt {st.recover_count}/3): {e}",
                    flush=True,
                )
                if st.recover_count <= 3:
                    st.last_result = str(e)
                    state = "OBSERVE"
                    continue
                return finish("failed", error="Gemini repeatedly selected controls not present on screen")
            
            # Log the full exception before returning
            print(f"[JARVIS ERROR] Unhandled exception in state machine: {type(e).__name__}: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return finish("failed", error=f"{type(e).__name__}: {e}")

    return finish("aborted", summary="cancelled")


async def _ask(ctx: AgentContext, question: str) -> str:
    if ctx.voice_ask is None:
        return "stop"
    return await ctx.voice_ask(question)
