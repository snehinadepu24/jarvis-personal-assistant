from __future__ import annotations

import asyncio
import hashlib
import inspect
import json
import queue
import threading
from dataclasses import dataclass, field
from typing import Callable

from pydantic import BaseModel

from jarvis.core.schema import Screen, Step
from jarvis.safety.risk import Risk, classify


class GateRequest(BaseModel):
    tier: int
    nonce: str
    action_hash: str
    summary: str
    window_title: str
    element_desc: str
    thought: str = ""
    expect: str = ""


class GateDecision(BaseModel):
    approved: bool
    tier: int
    reason: str = ""
    nonce: str = ""
    action_hash: str = ""


class GateDenied(Exception):
    pass


def timed_input(prompt: str, timeout: float) -> str | None:
    print(prompt, end="", flush=True)
    q: queue.Queue = queue.Queue()

    def reader():
        try:
            q.put(input())
        except EOFError:
            q.put("")

    threading.Thread(target=reader, daemon=True).start()
    try:
        return q.get(timeout=timeout)
    except queue.Empty:
        return None


async def console_confirm(req: GateRequest, *, cancel_window_s: float = 2.0, timeout_s: float = 30.0, speak_summary: bool = True) -> bool:
    print(f"\n[JARVIS GATE] tier {req.tier}: {req.summary}")
    print(f"[JARVIS GATE] window: {req.window_title}  target: {req.element_desc or '-'}")
    print(f"[JARVIS GATE] nonce {req.nonce} (approval is bound to this action's hash)")
    if speak_summary:
        try:
            from jarvis.voice.tts import speak

            speak(f"Tier {req.tier} action. {req.summary}. Approve by typing nonce {req.nonce}, or press n to cancel.")
        except ImportError:
            print("[JARVIS GATE] (voice unavailable here; spoken summary plays on Windows)")
    first = timed_input(f"[JARVIS GATE] type 'n' to cancel within {cancel_window_s:.0f}s, or the nonce to approve: ", cancel_window_s)
    if first is not None and first.strip().lower() == "n":
        return False
    if first is not None and first.strip() == req.nonce:
        print("[JARVIS GATE] approved by nonce.", flush=True)
        return True
    second = timed_input(f"[JARVIS GATE] enter the nonce ({timeout_s:.0f}s to approve, empty denies): ", timeout_s)
    if second is None:
        print("[JARVIS GATE] timed out; treated as denied")
        return False
    approved = second.strip() == req.nonce
    print(
        f"[JARVIS GATE] {'approved by nonce.' if approved else 'denied; nonce did not match.'}",
        flush=True,
    )
    return approved


class ConfirmationGate:
    def __init__(self, confirmer=None, cancel_window_s: float = 2.0, timeout_s: float = 30.0, speak_summary: bool = True):
        self.confirmer = confirmer
        self.cancel_window_s = cancel_window_s
        self.timeout_s = timeout_s
        self.speak_summary = speak_summary
        self.shown = 0
        self.blocked = 0
        self.last_risk: Risk | None = None

    def _nonce(self) -> str:
        import secrets

        return f"{secrets.randbelow(10000):04d}"

    def _console(self, req: GateRequest) -> bool:
        return console_confirm(
            req, cancel_window_s=self.cancel_window_s, timeout_s=self.timeout_s, speak_summary=self.speak_summary
        )

    async def approve(self, step: Step, screen: Screen) -> GateDecision:
        risk = classify(step, screen)
        self.last_risk = risk
        if risk.denied:
            self.blocked += 1
            return GateDecision(approved=False, tier=risk.tier, reason=f"deny-list: {risk.reason}")

        if risk.tier <= 1:
            return GateDecision(approved=True, tier=risk.tier, reason=risk.reason)

        if risk.tier == 2:
            return GateDecision(approved=True, tier=2, reason=f"notice (spoken in production): {risk.reason}")

        self.shown += 1
        a = step.action
        req = GateRequest(
            tier=risk.tier,
            nonce=self._nonce(),
            action_hash="",
            summary=f"{a.type}: {risk.reason}",
            window_title=screen.window_title,
            element_desc=risk.element_desc,
            thought=step.thought,
            expect=step.expect,
        )
        req.action_hash = bind_hash(req, a)
        confirmer = self.confirmer or self._console
        if req.tier >= 4:
            ans = confirmer(req)
            if inspect.isawaitable(ans):
                ans = await ans
            ok = isinstance(ans, str) and ans.strip() == req.nonce
            self.blocked += 0 if ok else 1
            return GateDecision(approved=ok, tier=req.tier, reason="typed nonce" if ok else "tier-4 denied (default deny)", nonce=req.nonce, action_hash=req.action_hash)
        ans = confirmer(req)
        if inspect.isawaitable(ans):
            ans = await ans
        ok = bool(ans)
        self.blocked += 0 if ok else 1
        return GateDecision(approved=ok, tier=req.tier, reason="user approved" if ok else "user denied", nonce=req.nonce, action_hash=req.action_hash)


def bind_hash(req: GateRequest, action) -> str:
    try:
        action_json = action.model_dump()
    except Exception:
        action_json = {"type": getattr(action, "type", "?")}
    basis = json.dumps({"action": action_json, "nonce": req.nonce, "window": req.window_title}, sort_keys=True)
    return hashlib.sha256(basis.encode()).hexdigest()[:16]


def auto_approve_confirmer(req: GateRequest) -> bool:
    return True


def always_deny_confirmer(req: GateRequest) -> bool:
    return False
