from __future__ import annotations

import asyncio

import pytest

from jarvis.core.schema import Rect, Screen, Step, UiElement, element_key
from jarvis.safety import gate as gate_mod
from jarvis.safety.gate import ConfirmationGate


def el(mark, name="Send", aid="send"):
    return UiElement(mark=mark, role="button", name=name, automation_id=aid, control_type=50000,
                     rect=Rect(l=0, t=0, r=10, b=10), enabled=True, patterns=["invoke"],
                     key=element_key(aid, 50000, name, "W"))


def screen():
    return Screen(app="a", window_title="W", elements=[el(1)])


def step():
    return Step(thought="t", action={"type": "click", "mark": 1}, expect="e")


@pytest.fixture
def no_voice():
    # jarvis.voice.tts is import-guarded off Windows; console_confirm handles the
    # ImportError and prints a note instead of speaking.
    yield


def test_console_cancel_within_2s_window(monkeypatch, no_voice):
    def fake_timed_input(prompt, timeout):
        assert timeout == pytest.approx(2.0)
        return "n"

    monkeypatch.setattr(gate_mod, "timed_input", fake_timed_input)
    gate = ConfirmationGate(cancel_window_s=2.0, timeout_s=30.0, speak_summary=False)
    d = asyncio.run(gate.approve(step(), screen()))
    assert not d.approved and d.reason == "user denied"


def test_console_typed_nonce_approves(monkeypatch, no_voice):
    class FixedGate(ConfirmationGate):
        def _nonce(self):
            return "4242"

    seq = iter([None, "4242"])  # 2s cancel window expires, then user types the nonce

    def fake_timed_input(prompt, timeout):
        return next(seq)

    monkeypatch.setattr(gate_mod, "timed_input", fake_timed_input)
    gate = FixedGate(cancel_window_s=2.0, timeout_s=30.0, speak_summary=False)
    d = asyncio.run(gate.approve(step(), screen()))
    assert d.approved and d.nonce == "4242"


def test_console_timeout_denies(monkeypatch, no_voice):
    def fake_timed_input(prompt, timeout):
        return "n" if timeout == pytest.approx(2.0) else None

    monkeypatch.setattr(gate_mod, "timed_input", fake_timed_input)
    gate = ConfirmationGate(cancel_window_s=2.0, timeout_s=30.0, speak_summary=False)
    d = asyncio.run(gate.approve(step(), screen()))
    assert not d.approved


def test_gate_records_shown_and_blocked(no_voice):
    gate = ConfirmationGate(confirmer=gate_mod.auto_approve_confirmer)
    asyncio.run(gate.approve(step(), screen()))
    assert gate.shown == 1 and gate.blocked == 0
    gate2 = ConfirmationGate(confirmer=gate_mod.always_deny_confirmer)
    asyncio.run(gate2.approve(step(), screen()))
    assert gate2.blocked == 1
